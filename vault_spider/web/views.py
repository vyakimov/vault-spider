"""Routes.

Handlers are sync ``def`` on purpose: retrieval, Chroma and OpenRouter are all blocking,
so Starlette runs these in its threadpool instead of stalling the event loop.

Failures map onto the CLI's closed ``error_types`` union rather than inventing new names,
so the web, CLI and MCP surfaces keep describing the same system the same way.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from chromadb.errors import InternalError as ChromaInternalError
from fastapi import APIRouter, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates

from vault_spider.corpus.loader import is_skipped_path
from vault_spider.envelope import failure, success
from vault_spider.llm.openrouter import OpenRouterError
from vault_spider.retrieval.evidence import build_retrieval_output
from vault_spider.synthesis.answer import synthesize
from vault_spider.utils import validate_vault_relative_path
from vault_spider.web import format as fmt
from vault_spider.web.markdown import Highlight, render_inline, render_markdown
from vault_spider.web.state import AppState

router = APIRouter()

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

MODES = ("fast", "thorough")
GRANULARITIES = ("document", "section", "mixed")
MAX_RESULTS = 50

# error_type -> HTTP status, from the closed union in cli.py.
STATUS_BY_ERROR = {
    "invalid_arguments": 400,
    "not_found": 404,
    "index_empty": 409,
    "config_mismatch": 409,
    "provider_error": 502,
    "internal_error": 500,
}


def state_of(request: Request) -> AppState:
    return request.app.state.vault


# ---------------------------------------------------------------------------
# Query parsing
# ---------------------------------------------------------------------------


class SearchRequest:
    """The retrieval knobs, parsed and clamped once."""

    def __init__(self, params) -> None:
        self.query = (params.get("q") or "").strip()
        self.mode = params.get("mode") if params.get("mode") in MODES else "fast"
        granularity = params.get("granularity")
        self.granularity = granularity if granularity in GRANULARITIES else "document"
        self.n_results = self._clamp(params.get("n"), default=10)

    @staticmethod
    def _clamp(raw: Optional[str], default: int) -> int:
        try:
            value = int(raw) if raw is not None else default
        except (TypeError, ValueError):
            return default
        return max(1, min(MAX_RESULTS, value))

    @property
    def summary(self) -> str:
        return f"{self.mode} · {self.granularity} · {self.n_results}"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "q": self.query,
            "mode": self.mode,
            "granularity": self.granularity,
            "n": self.n_results,
        }


def run_retrieval(
    state: AppState, search: SearchRequest
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]], Dict[str, Any]]:
    """Retrieve, returning (output, error, meta). Exactly one of output/error is set."""
    # A `sync` between requests replaces the index under us; reconnect before querying.
    state.ensure_fresh_index()

    def search_once():
        return state.searcher.hybrid_search(
            query=search.query,
            mode=search.mode,
            granularity=search.granularity,
            n_results=search.n_results,
        )

    try:
        try:
            result = search_once()
        except ChromaInternalError:
            # A sync that lands mid-request slips past the freshness check above, and the
            # stale handle then fails for every later query too. Rebuild once and retry;
            # if it fails again the error is real, not staleness.
            if not state.reconnect():
                raise
            result = search_once()
    except OpenRouterError as exc:
        return None, fmt.humanize_error("provider_error", str(exc)), {}
    except ValueError as exc:
        # `hybrid_search` raises bare ValueError for an empty index and for a query
        # nothing matched; the CLI maps both to not_found.
        return None, fmt.humanize_error("not_found", str(exc)), {}
    except ChromaInternalError as exc:
        return None, fmt.humanize_error("internal_error", str(exc)), {}
    output = build_retrieval_output(
        search.query,
        search.mode,
        search.granularity,
        result.rows,
        vault_name=state.vault_name,
    )
    meta = {"timing_ms": round(result.timing_ms, 2), "tunables": result.debug_info}
    return output, None, meta


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> Response:
    """The retrieval page.

    Everything lives in the query string, so a result set is bookmarkable and survives a
    reload — HTMX requests this same route and selects the results region out of it.
    """
    state = state_of(request)
    search = SearchRequest(request.query_params)
    context: Dict[str, Any] = {
        "request": request,
        "search": search,
        "stats": state.stats(),
        "candidates": [],
        "error": None,
        "meta": {},
        "has_query": bool(search.query),
    }
    if search.query:
        output, error, meta = run_retrieval(state, search)
        context["error"] = error
        context["meta"] = meta
        if output is not None:
            context["candidates"] = fmt.decorate_candidates(
                output["candidates"], search.query
            )
    return TEMPLATES.TemplateResponse(request, "index.html", context)


@router.post("/answer", response_class=HTMLResponse)
def answer(
    request: Request,
    q: str = Form(...),
    mode: str = Form("thorough"),
    granularity: str = Form("mixed"),
    n: int = Form(10),
) -> Response:
    """Synthesize an answer over the retrieved notes. Returns a fragment for HTMX."""
    state = state_of(request)
    search = SearchRequest({"q": q, "mode": mode, "granularity": granularity, "n": str(n)})
    context: Dict[str, Any] = {
        "request": request,
        "search": search,
        "answer": None,
        "error": None,
    }
    # HTMX gets the fragment it asked for; a plain form post gets a whole page, so the
    # action still works with JavaScript unavailable.
    template = "_answer.html" if request.headers.get("HX-Request") else "answer.html"

    def rendered() -> Response:
        return TEMPLATES.TemplateResponse(request, template, context)

    if not search.query:
        context["error"] = fmt.humanize_error("invalid_arguments", "Ask a question first.")
        return rendered()

    output, error, _meta = run_retrieval(state, search)
    if error is not None or output is None:
        context["error"] = error
        return rendered()

    try:
        result = synthesize(state.provider, output, question=search.query)
    except OpenRouterError as exc:
        context["error"] = fmt.humanize_error("provider_error", str(exc))
        return rendered()

    citations = result.get("citations", [])
    context["answer"] = {
        "html": render_inline(fmt.link_citations(str(result.get("answer", "")), citations)),
        "confidence": result.get("confidence", ""),
        "abstained": bool(result.get("abstained")),
        "citations": citations,
        "warnings": result.get("warnings", []),
    }
    return rendered()


@router.get("/note/{path:path}", response_class=HTMLResponse)
def note(request: Request, path: str) -> Response:
    """The reading view: the note's own file, rendered."""
    state = state_of(request)
    try:
        relative = validate_vault_relative_path(path, label="path")
    except ValueError as exc:
        return _error_page(request, "invalid_arguments", str(exc))

    note = state.note(relative)
    if note is None:
        return _error_page(
            request, "not_found", f"No readable note at {relative}."
        )

    snapshot = state.snapshot()
    highlight = _highlight_from(request.query_params)
    body_html = render_markdown(
        note.body,
        resolver=snapshot.graph.resolver,
        highlight=highlight,
        drop_title=note.title,
    )
    backlinks = [
        {"path": link_path, "title": _title_of(snapshot, link_path)}
        for link_path in snapshot.graph.links_to(relative)
    ]
    context = {
        "request": request,
        "note": note,
        "body_html": body_html,
        "masthead": fmt.note_masthead(note),
        "backlinks": backlinks,
        "highlight": highlight,
        "back_query": request.query_params.get("q", ""),
        "stats": state.stats(),
    }
    return TEMPLATES.TemplateResponse(request, "note.html", context)


@router.get("/attachment/{path:path}")
def attachment(request: Request, path: str) -> Response:
    """Serve an image or file the vault links to."""
    state = state_of(request)
    try:
        relative = validate_vault_relative_path(path, label="path")
    except ValueError:
        return Response(status_code=400)
    if is_skipped_path(Path(relative)):
        return Response(status_code=404)
    root = Path(state.vault_root)
    target = root / relative
    try:
        resolved = target.resolve(strict=True)
        if not resolved.is_relative_to(root.resolve(strict=True)) or not resolved.is_file():
            return Response(status_code=404)
    except OSError:
        return Response(status_code=404)
    return FileResponse(resolved)


@router.get("/healthz")
def healthz(request: Request) -> JSONResponse:
    stats = state_of(request).stats()
    return JSONResponse({"ok": True, "notes": stats.get("total_documents", 0)})


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------


@router.get("/api/retrieve")
def api_retrieve(request: Request) -> JSONResponse:
    """The retrieval contract, in the same envelope the CLI emits."""
    state = state_of(request)
    search = SearchRequest(request.query_params)
    if not search.query:
        return _envelope_failure("retrieve", "invalid_arguments", "q is required")
    output, error, meta = run_retrieval(state, search)
    if error is not None or output is None:
        assert error is not None
        return _envelope_failure("retrieve", error["type"], error["message"])
    return JSONResponse(success("retrieve", result=output, meta=meta))


@router.get("/api/note/{path:path}")
def api_note(request: Request, path: str) -> JSONResponse:
    state = state_of(request)
    try:
        relative = validate_vault_relative_path(path, label="path")
    except ValueError as exc:
        return _envelope_failure("read-note", "invalid_arguments", str(exc))
    note = state.note(relative)
    if note is None:
        return _envelope_failure("read-note", "not_found", f"No readable note at {relative}")
    snapshot = state.snapshot()
    return JSONResponse(
        success(
            "read-note",
            result={
                "path": note.path,
                "title": note.title,
                "frontmatter": {key: str(value) for key, value in note.frontmatter.items()},
                "body": note.body,
                "backlinks": snapshot.graph.links_to(relative),
                "links": snapshot.graph.links_from(relative),
            },
        )
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _envelope_failure(action: str, error_type: str, message: str) -> JSONResponse:
    return JSONResponse(
        failure(action, error_type, message),
        status_code=STATUS_BY_ERROR.get(error_type, 500),
    )


def _error_page(request: Request, error_type: str, message: str) -> Response:
    return TEMPLATES.TemplateResponse(
        request,
        "error.html",
        {
            "request": request,
            "error": fmt.humanize_error(error_type, message),
            "stats": {},
        },
        status_code=STATUS_BY_ERROR.get(error_type, 500),
    )


def _highlight_from(params) -> Optional[Highlight]:
    try:
        start = int(params.get("from", ""))
        end = int(params.get("to", ""))
    except (TypeError, ValueError):
        return None
    if start < 1 or end < start:
        return None
    return Highlight(line_start=start, line_end=end)


def _title_of(snapshot, path: str) -> str:
    note = snapshot.by_path.get(path)
    return note.title if note is not None else Path(path).stem
