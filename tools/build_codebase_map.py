"""Generate docs/codebase-map.json and docs/codebase-map.html.

Walks version-controlled Python source (including pending untracked additions)
with ``ast`` to extract modules, classes,
functions, signatures, and internal imports, then renders two snapshots of the
codebase: a machine-readable JSON map for agents and a self-contained HTML
overview page for humans. Structure comes from the source; the prose (package
roles, data flows, invariants, command table) is maintained by hand below and
should be kept in sync with AGENTS.md when the architecture changes.

Usage:  uv run python tools/build_codebase_map.py
"""

from __future__ import annotations

import ast
import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- extraction


def _signature(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    parts = []
    args = fn.args
    pos = args.posonlyargs + args.args
    defaults = [None] * (len(pos) - len(args.defaults)) + list(args.defaults)
    for a, d in zip(pos, defaults):
        s = a.arg
        if a.annotation is not None:
            s += ": " + ast.unparse(a.annotation)
        if d is not None:
            s += "=" + ast.unparse(d)
        parts.append(s)
    if args.vararg:
        parts.append("*" + args.vararg.arg)
    elif args.kwonlyargs:
        parts.append("*")
    for a, d in zip(args.kwonlyargs, args.kw_defaults):
        s = a.arg
        if a.annotation is not None:
            s += ": " + ast.unparse(a.annotation)
        if d is not None:
            s += "=" + ast.unparse(d)
        parts.append(s)
    if args.kwarg:
        parts.append("**" + args.kwarg.arg)
    ret = ""
    if fn.returns is not None:
        ret = " -> " + ast.unparse(fn.returns)
    return f"({', '.join(parts)}){ret}"


def _first_line(doc: str | None) -> str | None:
    if not doc:
        return None
    return doc.strip().splitlines()[0].strip()


def extract_modules() -> list[dict]:
    tracked = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
        ],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    py_files = [
        f for f in tracked
        if f.endswith(".py") and f.split("/")[0] in
        ("vault_spider", "scripts", "tools", "tests")
    ]

    modules = []
    for rel in sorted(py_files):
        src = (ROOT / rel).read_text()
        tree = ast.parse(src)
        internal_deps: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module
                if node.level > 0:
                    pkg_parts = rel.split("/")[:-1]
                    base = pkg_parts[: len(pkg_parts) - (node.level - 1)]
                    mod = ".".join(base + [node.module])
                if mod.startswith("vault_spider"):
                    internal_deps.add(mod)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("vault_spider"):
                        internal_deps.add(alias.name)

        classes, functions, constants = [], [], []
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods, fields = [], []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not item.name.startswith("_") or item.name == "__init__":
                            methods.append({
                                "name": item.name,
                                "signature": _signature(item),
                                "doc": _first_line(ast.get_docstring(item)),
                                "line": item.lineno,
                            })
                    elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        fields.append(item.target.id)
                classes.append({
                    "name": node.name,
                    "bases": [ast.unparse(b) for b in node.bases],
                    "doc": _first_line(ast.get_docstring(node)),
                    "line": node.lineno,
                    "fields": fields,
                    "methods": methods,
                })
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    functions.append({
                        "name": node.name,
                        "signature": _signature(node),
                        "doc": _first_line(ast.get_docstring(node)),
                        "line": node.lineno,
                    })
            elif isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name) \
                    and node.targets[0].id.isupper():
                constants.append(node.targets[0].id)

        modules.append({
            "path": rel,
            "loc": len(src.splitlines()),
            "doc": ast.get_docstring(tree),
            "internal_deps": sorted(internal_deps),
            "classes": classes,
            "functions": functions,
            "constants": constants,
        })
    return modules


# ------------------------------------------------------ hand-maintained prose

PACKAGES = {
    "vault_spider (root)": {
        "match": lambda p: p.startswith("vault_spider/") and "/" not in p[len("vault_spider/"):],
        "role": "Entry points and cross-cutting plumbing: the JSON-only CLI, the MCP server, "
                "configuration, the JSON envelope, and shared helpers.",
    },
    "vault_spider.corpus": {
        "match": lambda p: p.startswith("vault_spider/corpus/"),
        "role": "Reads the vault: loads Markdown notes, parses frontmatter, resolves note "
                "identity (ULID or path hash), and splits notes into deterministic, "
                "Markdown-aware chunks with heading ancestry and exact source ranges.",
    },
    "vault_spider.index": {
        "match": lambda p: p.startswith("vault_spider/index/"),
        "role": "Builds and maintains the ChromaDB collection (one document entry + N section "
                "entries per note, distinguished by the `granularity` metadata field) with "
                "failure-safe incremental sync, one canonical note-summary store shared by "
                "manual and OpenRouter generation, and separate dense/lexical/source views; "
                "plus a read-only stats reader.",
    },
    "vault_spider.retrieval": {
        "match": lambda p: p.startswith("vault_spider/retrieval/"),
        "role": "Hybrid search: BM25 + embeddings fused by pure scoring functions, optional "
                "rerank (thorough mode), document-promoted mixed retrieval, an on-disk "
                "query-embedding cache, and source-safe evidence/citation assembly.",
    },
    "vault_spider.synthesis": {
        "match": lambda p: p.startswith("vault_spider/synthesis/"),
        "role": "Turns a retrieval output contract into an LLM-synthesized, cited answer; "
                "abstains when the notes lack the answer.",
    },
    "vault_spider.compounding": {
        "match": lambda p: p.startswith("vault_spider/compounding/"),
        "role": "Vault health and write-back: the read-only lint report, saving good answers "
                "as distilled notes, and shared frontmatter-backfill mechanics.",
    },
    "vault_spider.enrich": {
        "match": lambda p: p.startswith("vault_spider/enrich/"),
        "role": "App-agnostic enrichment planner: retrieves a note's neighborhood and proposes "
                "title/frontmatter/links/placement as JSON. Never mutates files or the index; "
                "plans are applied via the mutation commands.",
    },
    "vault_spider.obsidian": {
        "match": lambda p: p.startswith("vault_spider/obsidian/"),
        "role": "The write path: contract-enforcing note mutations executed through the "
                "official Obsidian CLI (app must be running, macOS only), plus the macOS vault "
                "registry bridge. Mutation code never writes vault files directly.",
    },
    "vault_spider.evaluation": {
        "match": lambda p: p.startswith("vault_spider/evaluation/"),
        "role": "Golden-dataset benchmark: strict label validation against the corpus, then "
                "scored retrieval (nDCG@k, evidence recall, complete@k, MRR) and optional "
                "LLM-judged synthesis runs. Always run against a dedicated --chroma-path.",
    },
    "vault_spider.llm": {
        "match": lambda p: p.startswith("vault_spider/llm/"),
        "role": "OpenRouter client: embeddings, reranking, and chat completions. The only "
                "module that talks to the LLM provider.",
    },
    "vault_spider.web": {
        "match": lambda p: p.startswith("vault_spider/web/"),
        "role": "Read-only web app (FastAPI + Jinja2 + HTMX, no build step): retrieval page, "
                "note reading view with resolved wikilinks and backlinks, and the retrieval "
                "contract as JSON. Holds the IndexStore/Searcher singletons and a cached vault "
                "link graph; renders Obsidian Markdown (wikilinks, callouts) with raw HTML off. "
                "Never writes to the vault.",
    },
    "scripts": {
        "match": lambda p: p.startswith("scripts/"),
        "role": "Operational surfaces: the launchd periodic-sync installer and runner, and the "
                "Obsidian-side setup script.",
    },
    "tools": {
        "match": lambda p: p.startswith("tools/"),
        "role": "Maintenance tools: frontmatter backfills for existing vaults (dry-run by "
                "default) and this codebase-map generator.",
    },
}

DATA_FLOW = {
    "read_path": [
        "vault .md files",
        "corpus.loader / corpus.frontmatter / corpus.identity / corpus.chunker",
        "index.store (Chroma collection: document + section entries; BM25 corpus)",
        "retrieval.searcher (BM25 + embeddings via llm.openrouter, fused by retrieval.fusion; "
        "thorough mode reranks)",
        "retrieval.evidence (retrieval output contract)",
        "synthesis.answer (cited answer or abstention)",
        "compounding.distill (--save: write answer back as a distilled note)",
    ],
    "write_path": [
        "cli.py mutation commands (create-note, edit-note, merge-frontmatter, add-links, "
        "insert-related, move-note, rename-note, open-note)",
        "obsidian.notes (contract enforcement, dry-run diffs, sha256 compare-and-write)",
        "obsidian.backend (official Obsidian CLI invocation)",
        "running Obsidian app -> vault files (wikilinks update, plugins fire)",
    ],
    "surfaces": [
        "bin/vault-spider -> vault_spider.cli (JSON envelope on stdout, exit 1 on error)",
        "bin/vault-spider-mcp -> vault_spider.mcp_server (dual-transport MCP for Claude "
        "Desktop / ChatGPT)",
        "bin/vault-spider-web -> vault_spider.web (phone-first read-only app on 127.0.0.1:8765)",
    ],
}

MERMAID_CODE_AND_DATA_FLOW = """flowchart LR
    subgraph surfaces["Surfaces"]
        CLI["bin/vault-spider<br/>JSON CLI"]
        MCP["bin/vault-spider-mcp<br/>MCP server"]
        UI["bin/vault-spider-web<br/>web app"]
    end

    subgraph read["Read, index, and query"]
        Vault[("Obsidian vault<br/>Markdown notes")]
        Corpus["corpus<br/>load, normalize, identify, chunk"]
        Store["index.store<br/>sync + BM25"]
        Index[("ChromaDB<br/>document + section entries")]
        Search["retrieval.searcher<br/>hybrid search + fusion"]
        Evidence["retrieval.evidence<br/>ranked candidate contract"]
        Synthesis["synthesis.answer<br/>cited answer or abstention"]
        Distill["compounding.distill<br/>optional distilled note"]
        Lint["compounding.lint<br/>corpus health"]
        Enrich["enrich.planner<br/>proposed metadata + links"]
        Eval["evaluation<br/>validate + score"]
        OpenRouter["llm.openrouter<br/>embed, rerank, chat"]
    end

    subgraph write["Mutation path"]
        Commands["cli mutation commands"]
        Notes["obsidian.notes<br/>contracts, dry-run, guarded edits"]
        Backend["obsidian.backend<br/>official CLI adapter"]
        Obsidian["Running Obsidian app<br/>link updates + plugins"]
    end

    MCP -->|"isolated CLI subprocess"| CLI
    UI --> Search
    UI --> Synthesis
    UI --> Corpus
    CLI -->|"sync"| Corpus
    Vault -->|"direct reads"| Corpus
    Corpus --> Store
    Store -->|"embeddings"| OpenRouter
    Store --> Index
    CLI -->|"retrieve"| Search
    Index --> Search
    Search <-->|"query embedding / optional rerank"| OpenRouter
    Search --> Evidence
    CLI -->|"synthesize"| Synthesis
    Evidence --> Synthesis
    Synthesis <-->|"chat"| OpenRouter
    Synthesis --> Distill
    Distill -->|"create-only save"| Vault
    CLI -->|"lint"| Lint
    Vault --> Lint
    Lint -->|"--fix: missing metadata only"| Vault
    CLI -->|"enrich"| Enrich
    Vault --> Enrich
    Index --> Enrich
    Enrich <-->|"chat"| OpenRouter
    CLI -->|"eval"| Eval
    Eval --> Search
    Eval --> Synthesis
    CLI -->|"create/edit/move/rename/link"| Commands
    Commands --> Notes --> Backend --> Obsidian
    Obsidian -->|"mutation-command writes"| Vault
"""

INVARIANTS = [
    "Every CLI command prints exactly one JSON envelope: {ok: true, action, result, meta} or "
    "{ok: false, action, error}; check `ok`, not just the exit code.",
    "Read path (sync, retrieve, lint) works on vault files directly; the write path goes only "
    "through the Obsidian CLI. Never write vault files directly from mutation code.",
    "One note indexes as one document-granularity entry plus N section entries in a single "
    "Chroma collection (granularity metadata field). Chunking is deterministic and "
    "Markdown-aware; generated context never becomes cited source evidence.",
    "`provenance` frontmatter (human | reference | llm | distilled) is set at note creation, "
    "immutable once set, never proposed by enrichment, and orthogonal to `type`.",
    "`id`, `created`, and `provenance` are immutable once set; `lint --fix` writes only "
    "missing values, never edits existing ones.",
    "Sync is failure-safe: old index entries are deleted only after all new embeddings are "
    "computed and validated.",
    "Every mutating command accepts --dry-run and returns exactly what would change with "
    "meta.dry_run: true, making no backend calls.",
    "Eval runs go against a dedicated --chroma-path, never the live-vault index.",
    "Distilled notes are regenerable pointers to their sources; raw notes always win on "
    "conflict.",
]

COMMANDS = [
    {"command": "schema",
     "summary": "Print the machine-readable command + contract schema (version 2)."},
    {"command": "sync [--root DIR] [--reset] [--contextualize] [--refresh-context]",
     "summary": "Incremental index sync; consumes canonical note summaries and optionally "
                "generates missing/stale summaries through OpenRouter."},
    {"command": "context prepare|import|status",
     "summary": "Export coding-agent summary jobs, validate/promote canonical records, or report "
                "ready/missing/stale/orphaned coverage."},
    {"command": "stats", "summary": "Index statistics (no API key needed)."},
    {"command": "retrieve --query Q [--mode fast|thorough] "
                "[--granularity document|section|mixed] [filters]",
     "summary": "Hybrid retrieval returning the scored-candidate contract; mixed fuses "
                "document/section signals and returns exact chunks. Filters: --folder --tag "
                "--type --provenance --since --until."},
    {"command": "synthesize --query Q [--mode thorough] [--retrieval FILE] [--save]",
     "summary": "Retrieve then synthesize a cited answer; abstains when unsupported; --save "
                "persists a distilled note."},
    {"command": "enrich --root DIR (--note PATH | --stdin) [--intent ...]",
     "summary": "Plan-only enrichment: proposed title/frontmatter/links/placement as JSON; "
                "never mutates."},
    {"command": "lint --root DIR [--format json|text] [--fix] [--fix-timestamps]",
     "summary": "Read-only corpus health report; --fix writes only missing id/created/updated."},
    {"command": "eval validate|run --dataset DIR [--stage retrieval|synthesis]",
     "summary": "Golden-dataset validation and scored benchmark with a versioned results "
                "contract."},
    {"command": "create-note / read-note / edit-note / merge-frontmatter / add-links / "
                "insert-related / move-note / rename-note / open-note",
     "summary": "Note mutations through the running Obsidian app; all mutating commands accept "
                "--dry-run."},
]

OTHER_FILES = [
    {"path": "AGENTS.md", "role": "Canonical project instructions (CLAUDE.md delegates here)."},
    {"path": "README.md", "role": "User-facing overview and install/usage guide."},
    {"path": "bin/vault-spider",
     "role": "Stable CLI wrapper; locates the project and delegates to `uv run vault-spider`."},
    {"path": "bin/vault-spider-mcp", "role": "Wrapper launching the MCP server."},
    {"path": "bin/vault-spider-web", "role": "Wrapper launching the web app."},
    {"path": "vault_spider/web/templates/",
     "role": "Jinja2 templates for the web app: base, index (retrieval), note (reading view), "
             "answer, error, and the HTMX fragments. Not visible to the module extractor "
             "below, which only reads Python."},
    {"path": "vault_spider/web/static/",
     "role": "app.css (hand-written, phone-first, light+dark) and a vendored htmx.min.js. "
             "No build step and no external requests: the app works offline."},
    {"path": "config.yaml.example",
     "role": "Template for installation settings (vault root, folders, tag rules, context "
             "summaries, timestamps). Real config.yaml is gitignored."},
    {"path": ".env.example", "role": "Template for secrets: OpenRouter key and model names."},
    {"path": "pyproject.toml", "role": "Package metadata and dependencies (uv-managed)."},
    {"path": ".github/workflows/ci.yml", "role": "CI workflow."},
    {"path": "docs/launchd.md",
     "role": "LaunchAgents: periodic-sync (interval, logs, status, uninstall) and the "
             "web-app supervisor behind a reverse proxy."},
    {"path": "docs/obsidian-setup.md", "role": "Obsidian-side setup for the mutation backend."},
    {"path": "docs/note-context-summaries.md",
     "role": "Canonical summary storage, manual Codex/Claude and automatic OpenRouter workflows, "
             "embedding, and staleness behavior."},
    {"path": "skills/vault/SKILL.md",
     "role": "Agent skill for operating the vault (plus references/ for capture, commands, "
             "eval/server)."},
    {"path": "eval/",
     "role": "Committed golden dataset #1: public_vault corpus, golden_queries.jsonl, "
             "dataset.yaml, and persistent baseline/contextual configs whose local artifacts "
             "stay under gitignored context-data/."},
    {"path": "eval-realistic/",
     "role": "Committed golden dataset #2: larger realistic corpus with the same persistent, "
             "isolated baseline/contextual layout."},
    {"path": "tests/fixtures/notes/", "role": "Small fixture vault used by the pytest suite."},
    {"path": "chroma_db/ (gitignored)", "role": "Local Chroma index of the live vault."},
]

# ---------------------------------------------------------------- JSON output


def build_json(code_modules: list[dict], test_modules: list[dict]) -> dict:
    def strip_module(m: dict) -> dict:
        out = {
            "path": m["path"],
            "loc": m["loc"],
            "summary": (m["doc"] or "").strip().split("\n\n")[0].replace("\n", " ") or None,
            "internal_deps": m["internal_deps"],
            "classes": m["classes"],
            "functions": m["functions"],
        }
        if m["constants"]:
            out["constants"] = m["constants"]
        return out

    tests_json = []
    for t in test_modules:
        n_tests = sum(1 for f in t["functions"] if f["name"].startswith("test_"))
        n_tests += sum(
            1 for c in t["classes"] for meth in c["methods"]
            if meth["name"].startswith("test_")
        )
        tests_json.append({
            "path": t["path"],
            "loc": t["loc"],
            "test_count": n_tests,
            "summary": _first_line(t["doc"]),
            "covers": t["internal_deps"],
        })

    packages_json = {}
    for name, spec in PACKAGES.items():
        mods = [strip_module(m) for m in code_modules if spec["match"](m["path"])]
        mods = [m for m in mods if m["loc"] > 1 or m["summary"]]
        packages_json[name] = {"role": spec["role"], "modules": mods}

    return {
        "project": {
            "name": "vault-spider",
            "description": "JSON-only CLI (plus MCP server and a read-only web app) for an Obsidian "
                           "vault: hybrid retrieval over ChromaDB + BM25, cited answer "
                           "synthesis with abstention, corpus health lint, plan-only "
                           "enrichment, a golden eval harness, and safe note mutations "
                           "executed through the running Obsidian app.",
            "language": "Python (uv-managed)",
            "entry_points": {
                "cli": "bin/vault-spider -> vault_spider/cli.py:main",
                "mcp": "bin/vault-spider-mcp -> vault_spider/mcp_server.py:main",
                "ui": "bin/vault-spider-web -> vault_spider/web/__main__.py:main",
            },
            "canonical_instructions": "AGENTS.md",
            "json_envelope": "{ok: true, action, result, meta} | {ok: false, action, error}; "
                             "always check `ok`, not just the exit code",
        },
        "generated": date.today().isoformat(),
        "generator_note": "Regenerate with `uv run python tools/build_codebase_map.py`. "
                          "Structure extracted from version-controlled source via Python ast; "
                          "line numbers refer to the commit current on the generation date.",
        "architecture": {
            "data_flow": DATA_FLOW,
            "mermaid": {
                "title": "Code and data flow",
                "source": MERMAID_CODE_AND_DATA_FLOW,
            },
            "invariants": INVARIANTS,
        },
        "commands": COMMANDS,
        "packages": packages_json,
        "tests": {"runner": "uv run pytest", "files": tests_json},
        "other_files": OTHER_FILES,
    }


# ---------------------------------------------------------------- HTML output


def _page_css() -> str:
    """The page CSS.

    Kept as a plain string rather than inside the f-string below so the braces do not
    have to be doubled.
    """
    return """
:root {
  --paper: #f7f8f6;
  --paper-sunk: #eff1ed;
  --ink: #16181c;
  --ink-soft: #5a6068;
  --ink-faint: #8b9198;
  --rule: #dfe2de;
  --accent: #2f5d50;
  --wash: #e8ede7;
  --serif: ui-serif, "New York", Charter, "Iowan Old Style", Georgia, serif;
  --mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  --measure: 44rem;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #14161a; --paper-sunk: #1a1d22; --ink: #e6e8e4; --ink-soft: #9aa2a6;
    --ink-faint: #6c747a; --rule: #2a2e33; --accent: #7fbba6; --wash: #1e2a26;
  }
}

*, *::before, *::after { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: var(--serif);
  font-size: 16px;
  line-height: 1.6;
  overflow-x: hidden;
}

a { color: var(--accent); text-underline-offset: .16em; text-decoration-thickness: .06em; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 2px; }

code, .mono {
  font-family: var(--mono);
  font-size: .84em;
  font-variant-ligatures: none;
}

/* --------------------------------------------------------------- shell */

.shell {
  display: grid;
  grid-template-columns: 1fr;
  max-width: 78rem;
  margin: 0 auto;
  padding: 0 1.5rem;
}

main { min-width: 0; padding: 3rem 0 6rem; max-width: var(--measure); }

/* --------------------------------------------------------------- index */

.index { display: none; }

.index__mobile { margin: 1.5rem 0 0; }
.index__mobile summary {
  cursor: pointer; font-family: var(--mono); font-size: .72rem;
  letter-spacing: .1em; text-transform: uppercase; color: var(--ink-soft);
  padding: .6rem 0;
}
.index__mobile ol { columns: 2; column-gap: 1.5rem; }

.index ol, .index__mobile ol {
  list-style: none; margin: .25rem 0 0; padding: 0;
  font-family: var(--mono); font-size: .74rem; line-height: 1.9;
}
.index a { color: var(--ink-soft); text-decoration: none; display: block; }
.index a:hover, .index a.is-current { color: var(--accent); }
.index li.is-group {
  color: var(--ink-faint); letter-spacing: .1em; text-transform: uppercase;
  font-size: .65rem; margin-top: 1rem;
}

/* ------------------------------------------------------------- masthead */

.title {
  font-size: 2rem; line-height: 1.1; font-weight: 400; margin: 0;
  letter-spacing: -0.01em;
}
.title em { font-style: normal; color: var(--ink-soft); }
.lede { color: var(--ink-soft); margin: .9rem 0 0; text-wrap: pretty; }

/* One mono strip rather than four big-number tiles: these are reference
   figures, not headline metrics. */
.counts {
  font-family: var(--mono); font-size: .72rem; color: var(--ink-soft);
  margin: 1.5rem 0 0; padding-top: 1rem; border-top: 1px solid var(--rule);
  display: flex; flex-wrap: wrap; gap: .35rem 1.25rem;
}
.counts b { color: var(--ink); font-weight: 600; }

/* -------------------------------------------------------------- headings */

h2 {
  font-family: var(--mono);
  font-size: .74rem; font-weight: 600; letter-spacing: .14em; text-transform: uppercase;
  color: var(--ink-soft);
  margin: 4rem 0 1.25rem; padding-bottom: .5rem;
  border-bottom: 1px solid var(--rule);
  scroll-margin-top: 1.5rem;
}
h2 code { font-size: 1em; background: none; padding: 0; text-transform: none;
  letter-spacing: .04em; color: var(--accent); }
h2 .anchor {
  float: right; color: var(--ink-faint); text-decoration: none; opacity: 0;
  transition: opacity 120ms ease;
}
h2:hover .anchor { opacity: 1; }

h3 { font-size: 1rem; font-weight: 600; margin: 0 0 .5rem; }

/* ----------------------------------------------------------------- flows */

.flows { display: grid; gap: 2rem; }
.flow ol { margin: 0; padding: 0; list-style: none; counter-reset: step; }
.flow li {
  position: relative; padding-left: 2rem; margin: .5rem 0;
  font-size: .92rem; counter-increment: step;
}
.flow li::before {
  content: counter(step, decimal-leading-zero);
  position: absolute; left: 0; top: .15em;
  font-family: var(--mono); font-size: .68rem; color: var(--ink-faint);
}
.flow--surfaces li::before { content: "→"; font-size: .8rem; top: 0; }

/* --------------------------------------------------------------- diagram */

/* The graph is genuinely wide; it gets the full viewport rather than the
   reading measure, and scrolls inside its own box on a narrow screen. */
.diagram {
  margin: 2.5rem 0 0;
  width: 100vw; position: relative; left: 50%; margin-left: -50vw;
  padding: 2rem 0;
  background: var(--paper-sunk);
  border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule);
}
.diagram__head {
  max-width: 78rem; margin: 0 auto; padding: 0 1.5rem .75rem;
  font-family: var(--mono); font-size: .68rem; letter-spacing: .12em;
  text-transform: uppercase; color: var(--ink-soft);
}
.diagram__scroll { overflow-x: auto; padding: 0 1.5rem; }
.mermaid {
  white-space: pre; margin: 0; overflow-x: auto;
  font-family: var(--mono); font-size: .72rem; line-height: 1.55; color: var(--ink-soft);
}
.diagram.is-rendered .mermaid {
  min-width: 60rem; white-space: normal; font-size: 0; overflow: visible;
}
.diagram.is-rendered .diagram__fallback { display: none; }
.mermaid svg { max-width: none !important; height: auto; display: block; margin: 0 auto; }
.diagram__note {
  max-width: 78rem; margin: .75rem auto 0; padding: 0 1.5rem;
  color: var(--ink-faint); font-size: .78rem;
}
.diagram__note summary { cursor: pointer; color: var(--accent); }
.diagram__note pre {
  background: var(--paper); border: 1px solid var(--rule); border-radius: 4px;
  overflow-x: auto; padding: .9rem; font-size: .74rem; line-height: 1.5;
}

/* ------------------------------------------------------------ invariants */

.invariants { margin: 0; padding: 0; list-style: none; }
.invariants li {
  position: relative; padding-left: 1.25rem; margin: .75rem 0; font-size: .95rem;
}
.invariants li::before {
  content: ""; position: absolute; left: 0; top: .62em;
  width: .45rem; height: 1px; background: var(--accent);
}

/* --------------------------------------------------------------- modules */

.pkg-role { color: var(--ink-soft); font-size: .92rem; margin: -.5rem 0 1.5rem; }

.mod { padding: 1.1rem 0; border-top: 1px solid var(--rule); scroll-margin-top: 1.5rem; }
.mod:first-child { border-top: 0; padding-top: 0; }

.mod__head { display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; }
.mod__path {
  font-family: var(--mono); font-size: .82rem; font-weight: 600;
  color: var(--ink); text-decoration: none; min-width: 0;
  overflow-wrap: anywhere;
}
.mod__path:hover { color: var(--accent); }
.mod__loc {
  font-family: var(--mono); font-size: .68rem; color: var(--ink-faint);
  white-space: nowrap; flex: 0 0 auto;
}
.mod__doc { margin: .35rem 0 0; font-size: .92rem; color: var(--ink-soft); }
.mod__deps {
  margin: .45rem 0 0; font-size: .7rem; font-family: var(--mono); color: var(--ink-faint);
  /* Flex wrapping, not separators inside each name: a `·` glued to a nowrap span
     removes the very break opportunity the line needs. */
  display: flex; flex-wrap: wrap; align-items: baseline; gap: .15rem .9rem;
}
.mod__deps a { color: var(--ink-soft); text-decoration: none; }
.mod__deps a:hover { color: var(--accent); text-decoration: underline; }
.mod__deps .dep { white-space: nowrap; }
.dep-label { color: var(--ink-faint); }

details.symbols { margin: .6rem 0 0; }
details.symbols > summary {
  cursor: pointer; font-family: var(--mono); font-size: .7rem;
  color: var(--accent); list-style: none;
}
details.symbols > summary::-webkit-details-marker { display: none; }
details.symbols > summary::before { content: "▸ "; }
details.symbols[open] > summary::before { content: "▾ "; }
.symbols ul { margin: .6rem 0 0; padding-left: 1rem; list-style: none; }
.symbols li { margin: .35rem 0; font-size: .84rem; color: var(--ink-soft); }
.symbols li code { color: var(--ink); }
.symbols ul ul { padding-left: 1rem; margin-top: .25rem; }
.symbols .cls > code { font-weight: 600; }

/* ---------------------------------------------------------------- tables */

.tablewrap { overflow-x: auto; margin-top: .5rem; }
table { border-collapse: collapse; width: 100%; font-size: .86rem; }
th, td {
  text-align: left; padding: .55rem .7rem .55rem 0;
  border-bottom: 1px solid var(--rule); vertical-align: top;
}
th {
  font-family: var(--mono); font-weight: 400; font-size: .65rem;
  text-transform: uppercase; letter-spacing: .1em; color: var(--ink-faint);
}
td code { color: var(--ink); }
.num { text-align: right; font-family: var(--mono); font-size: .78rem; padding-right: 1.5rem; }
td.covers { color: var(--ink-faint); font-family: var(--mono); font-size: .7rem; }
tbody tr:hover { background: var(--wash); }

footer {
  margin-top: 4rem; padding-top: 1.25rem; border-top: 1px solid var(--rule);
  color: var(--ink-faint); font-size: .78rem;
}

/* --------------------------------------------------------------- desktop */

@media (min-width: 64rem) {
  .shell { grid-template-columns: 13rem minmax(0, 1fr); gap: 3.5rem; }
  .index { display: block; }
  .index__inner { position: sticky; top: 0; max-height: 100vh; overflow-y: auto;
    padding: 3rem 0 3rem; scrollbar-width: thin; }
  .index__mobile { display: none; }
  .flows { grid-template-columns: repeat(2, 1fr); gap: 2rem 2.5rem; }
  .flow--surfaces { grid-column: 1 / -1; }
  .title { font-size: 2.5rem; }
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
}
"""


def _page_script() -> str:
    """Mermaid init (themed to the page) plus index highlighting."""
    return """
const dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
const palette = dark
  ? { bg: "#1a1d22", node: "#1e2a26", line: "#3a4d46", text: "#e6e8e4",
      cluster: "#191c20", clusterBorder: "#2a2e33" }
  : { bg: "#eff1ed", node: "#e8ede7", line: "#7f9d92", text: "#16181c",
      cluster: "#f7f8f6", clusterBorder: "#dfe2de" };

import("https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs")
  .then(({ default: mermaid }) => {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      // `themeVariables` is only honoured by the "base" theme.
      theme: "base",
      flowchart: { curve: "basis", nodeSpacing: 34, rankSpacing: 52, padding: 8 },
      themeVariables: {
        fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
        fontSize: "14px",
        background: palette.bg,
        primaryColor: palette.node,
        primaryBorderColor: palette.line,
        primaryTextColor: palette.text,
        lineColor: palette.line,
        textColor: palette.text,
        clusterBkg: palette.cluster,
        clusterBorder: palette.clusterBorder,
        edgeLabelBackground: palette.bg,
      },
    });
    // `startOnLoad` cannot be used here: the import resolves after the load event.
    return mermaid.run({ querySelector: ".mermaid" });
  })
  .then(() => {
    document.querySelector(".diagram").classList.add("is-rendered");
  })
  .catch(() => {
    const note = document.querySelector(".diagram__fallback");
    if (note) {
      note.textContent =
        "Mermaid could not be loaded, so the diagram is shown as its source.";
    }
  });

// Mark the section currently on screen in the index.
const links = new Map();
document.querySelectorAll(".index a").forEach((a) => {
  links.set(a.getAttribute("href").slice(1), a);
});
const seen = new Set();
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) { seen.add(entry.target.id); } else { seen.delete(entry.target.id); }
  });
  links.forEach((a, id) => a.classList.toggle("is-current", seen.has(id)));
}, { rootMargin: "0px 0px -70% 0px" });
document.querySelectorAll("h2[id]").forEach((h) => observer.observe(h));
"""


def build_html(codebase_map: dict) -> str:
    e = html.escape
    packages_json = codebase_map["packages"]
    tests_json = codebase_map["tests"]["files"]

    # Every module that exists, so an `imports x.y` mention can become a real link
    # into this document instead of dead text.
    module_paths = {
        m["path"] for spec in packages_json.values() for m in spec["modules"]
    }

    def dep_link(dotted: str) -> str:
        """Link a dotted import to the module's anchor when that module is on this page."""
        candidate = dotted.replace(".", "/") + ".py"
        label = e(dotted)
        if candidate in module_paths:
            return f'<span class="dep"><a href="#{e(candidate)}">{label}</a></span>'
        return f'<span class="dep">{label}</span>'

    def module_entry(m: dict) -> str:
        parts = [f'<article class="mod" id="{e(m["path"])}">']
        parts.append(
            f'<div class="mod__head">'
            f'<a class="mod__path" href="#{e(m["path"])}">{e(m["path"])}</a>'
            f'<span class="mod__loc">{m["loc"]} loc</span></div>'
        )
        if m["summary"]:
            parts.append(f'<p class="mod__doc">{e(m["summary"])}</p>')
        if m["internal_deps"]:
            deps = "".join(dep_link(d) for d in m["internal_deps"])
            parts.append(
                f'<p class="mod__deps"><span class="dep-label">imports</span>{deps}</p>'
            )

        inner = []
        for c in m["classes"]:
            bases = f'({e(", ".join(c["bases"]))})' if c["bases"] else ""
            inner.append(
                f'<li class="cls"><code>class {e(c["name"])}{bases}</code>'
                f'{" — " + e(c["doc"]) if c["doc"] else ""}'
            )
            meths = [meth for meth in c["methods"] if meth["name"] != "__init__"]
            if meths:
                inner.append("<ul>")
                for meth in meths:
                    inner.append(
                        f'<li><code>.{e(meth["name"])}{e(meth["signature"])}</code>'
                        f'{" — " + e(meth["doc"]) if meth["doc"] else ""}</li>'
                    )
                inner.append("</ul>")
            inner.append("</li>")
        for f in m["functions"]:
            inner.append(
                f'<li><code>{e(f["name"])}{e(f["signature"])}</code>'
                f'{" — " + e(f["doc"]) if f["doc"] else ""}</li>'
            )
        if inner:
            n = len(m["classes"]) + len(m["functions"])
            parts.append(
                f'<details class="symbols"><summary>{n} public '
                f'symbol{"s" if n != 1 else ""}</summary>'
                f'<ul>{"".join(inner)}</ul></details>'
            )
        parts.append("</article>")
        return "".join(parts)

    def slug(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    sections_html = []
    package_index = []
    for name, spec in packages_json.items():
        entries = "".join(module_entry(m) for m in spec["modules"])
        if not entries:
            continue
        section_id = slug(name)
        package_index.append((section_id, name))
        sections_html.append(
            f'<section><h2 id="{section_id}"><code>{e(name)}</code>'
            f'<a class="anchor" href="#{section_id}" aria-label="Link to this section">#</a></h2>'
            f'<p class="pkg-role">{e(spec["role"])}</p>{entries}</section>'
        )

    flow_html = ""
    data_flow = codebase_map["architecture"]["data_flow"]
    for title, key, extra in [
        ("Read path — query", "read_path", ""),
        ("Write path — mutation", "write_path", ""),
        ("Surfaces", "surfaces", " flow--surfaces"),
    ]:
        steps = "".join(f"<li>{e(s)}</li>" for s in data_flow[key])
        flow_html += f'<div class="flow{extra}"><h3>{title}</h3><ol>{steps}</ol></div>'

    mermaid = codebase_map["architecture"]["mermaid"]
    mermaid_source = e(mermaid["source"])
    inv_html = "".join(f"<li>{e(i)}</li>" for i in codebase_map["architecture"]["invariants"])
    cmd_rows = "".join(
        f'<tr><td><code>{e(c["command"])}</code></td><td>{e(c["summary"])}</td></tr>'
        for c in COMMANDS
    )
    test_rows = "".join(
        f'<tr><td><code>{e(t["path"])}</code></td><td class="num">{t["test_count"]}</td>'
        f'<td class="covers">{e(", ".join(t["covers"])) or "—"}</td></tr>'
        for t in tests_json
    )
    other_rows = "".join(
        f'<tr><td><code>{e(o["path"])}</code></td><td>{e(o["role"])}</td></tr>'
        for o in OTHER_FILES
    )

    total_loc = sum(m["loc"] for p in packages_json.values() for m in p["modules"])
    n_mods = sum(len(p["modules"]) for p in packages_json.values())
    n_tests_total = sum(t["test_count"] for t in tests_json)
    today = codebase_map["generated"]

    fixed_top = [("architecture", "Architecture"), ("invariants", "Invariants"),
                 ("cli-commands", "CLI commands")]
    fixed_bottom = [("tests", "Tests"), ("other-files", "Other files")]

    def index_items() -> str:
        items = "".join(f'<li><a href="#{i}">{e(label)}</a></li>' for i, label in fixed_top)
        items += '<li class="is-group">Packages</li>'
        items += "".join(
            f'<li><a href="#{i}">{e(label)}</a></li>' for i, label in package_index
        )
        items += '<li class="is-group">Reference</li>'
        items += "".join(f'<li><a href="#{i}">{e(label)}</a></li>' for i, label in fixed_bottom)
        return items

    nav_items = index_items()

    return f"""<!doctype html>
<html lang="en">
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<meta name='color-scheme' content='light dark'>
<title>vault-spider — codebase map</title>
<style>{_page_css()}</style>
<div class="shell">
<nav class="index" aria-label="Contents"><div class="index__inner"><ol>{nav_items}</ol></div></nav>
<main>
<h1 class="title">vault-spider <em>— codebase map</em></h1>
<p class="lede">A JSON-only CLI, an MCP server and a read-only web app over an Obsidian vault:
hybrid retrieval (ChromaDB + BM25), cited answer synthesis with abstention, corpus lint,
plan-only enrichment, a golden eval harness, and note mutations executed through the running
Obsidian app. Canonical instructions live in <code>AGENTS.md</code>.</p>
<p class="counts">
  <span><b>{n_mods}</b> modules</span>
  <span><b>{total_loc:,}</b> lines</span>
  <span><b>{len(tests_json)}</b> test files</span>
  <span><b>{n_tests_total}</b> tests</span>
</p>

<details class="index__mobile"><summary>Contents</summary><ol>{nav_items}</ol></details>

<section>
<h2 id="architecture">Architecture<a class="anchor" href="#architecture"
  aria-label="Link to this section">#</a></h2>
<div class="flows">{flow_html}</div>
</section>

<div class="diagram">
  <p class="diagram__head">{e(mermaid["title"])}</p>
  <div class="diagram__scroll"><pre class="mermaid">{mermaid_source}</pre></div>
  <div class="diagram__note">
    <p class="diagram__fallback">Scroll the diagram sideways on a narrow screen.</p>
    <details><summary>Mermaid source</summary>
    <pre><code>{mermaid_source}</code></pre></details>
  </div>
</div>

<section>
<h2 id="invariants">Invariants<a class="anchor" href="#invariants"
  aria-label="Link to this section">#</a></h2>
<ul class="invariants">{inv_html}</ul>
</section>

<section>
<h2 id="cli-commands">CLI commands<a class="anchor" href="#cli-commands"
  aria-label="Link to this section">#</a></h2>
<div class="tablewrap"><table>
<thead><tr><th>Command</th><th>What it does</th></tr></thead>
<tbody>{cmd_rows}</tbody>
</table></div>
</section>

{"".join(sections_html)}

<section>
<h2 id="tests">Tests<a class="anchor" href="#tests" aria-label="Link to this section">#</a></h2>
<p class="pkg-role">Run with <code>uv run pytest</code>. "Covers" is derived from each test
file's <code>vault_spider</code> imports.</p>
<div class="tablewrap"><table>
<thead><tr><th>File</th><th class="num">Tests</th><th>Covers</th></tr></thead>
<tbody>{test_rows}</tbody>
</table></div>
</section>

<section>
<h2 id="other-files">Other files<a class="anchor" href="#other-files"
  aria-label="Link to this section">#</a></h2>
<div class="tablewrap"><table>
<thead><tr><th>Path</th><th>Role</th></tr></thead>
<tbody>{other_rows}</tbody>
</table></div>
</section>

<footer>Generated {today} by <code>tools/build_codebase_map.py</code> from version-controlled
source via Python <code>ast</code>. Companion machine-readable file:
<code>docs/codebase-map.json</code>.</footer>
</main>
</div>
<script type="module">{_page_script()}</script>
"""


def main() -> None:
    modules = extract_modules()
    code_modules = [m for m in modules if not m["path"].startswith("tests/")]
    test_modules = [m for m in modules if m["path"].startswith("tests/")]

    codebase_map = build_json(code_modules, test_modules)

    json_path = ROOT / "docs" / "codebase-map.json"
    json_path.write_text(json.dumps(codebase_map, indent=2) + "\n")
    print(f"wrote {json_path.relative_to(ROOT)} ({json_path.stat().st_size} bytes)")

    html_path = ROOT / "docs" / "codebase-map.html"
    html_path.write_text(build_html(codebase_map))
    print(f"wrote {html_path.relative_to(ROOT)} ({html_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
