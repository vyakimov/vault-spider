"""JSON-only CLI for Vault RAG: schema, sync, retrieve, synthesize."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

from vault_rag.envelope import failure, print_json, success
from vault_rag.llm.openrouter import OpenRouterClient, OpenRouterError

SCHEMA_VERSION = 1


def get_provider() -> OpenRouterClient:
    return OpenRouterClient.from_env()


def get_store(chroma_path: str, collection: str, provider: Optional[OpenRouterClient] = None):
    # Imported lazily so `vault-rag schema` works without chromadb/model setup.
    from vault_rag.index.store import IndexStore

    return IndexStore(
        chroma_db_path=chroma_path,
        collection_name=collection,
        provider=provider,
    )


# -- schema -------------------------------------------------------------------

def _schema() -> Dict[str, Any]:
    return {
        "version": SCHEMA_VERSION,
        "commands": {
            "schema": {"args": {}, "result": "this document"},
            "sync": {
                "args": {"--root": "vault directory (required)", "--reset": "flag"},
                "result": {
                    "added_notes": "int",
                    "updated_notes": "int",
                    "deleted_notes": "int",
                    "unchanged": "int",
                    "total_entries": "int",
                },
            },
            "retrieve": {
                "args": {
                    "--query": "str (required)",
                    "--mode": "fast|thorough (default fast)",
                    "--granularity": "document|section|mixed (default document)",
                    "-n": "int (default 10)",
                },
                "result": "retrieval_output",
            },
            "synthesize": {
                "args": {
                    "--query": "str",
                    "--mode": "fast|thorough (default thorough)",
                    "--granularity": "document|section|mixed (default mixed)",
                    "--retrieval": "path to a prior retrieve envelope/contract",
                    "--n-context": "int (default 8)",
                },
                "result": "synthesis_output (with embedded retrieval)",
            },
        },
        "contracts": {
            "retrieval_output": {
                "query": "str",
                "mode": "str",
                "granularity": "str",
                "candidates": [
                    {
                        "note_id": "str",
                        "path": "str",
                        "title": "str",
                        "type": "str",
                        "heading": "str",
                        "chunk_id": "str",
                        "line_start": "int",
                        "line_end": "int",
                        "excerpt": "str",
                        "scores": {
                            "bm25": "float",
                            "semantic": "float",
                            "fused": "float",
                            "reranker": "float|null",
                            "final": "float",
                        },
                        "why": "str",
                    }
                ],
            },
            "synthesis_output": {
                "question": "str",
                "answer": "str",
                "confidence": "str",
                "abstained": "bool",
                "citations": [
                    {
                        "key": "str",
                        "note_id": "str",
                        "path": "str",
                        "title": "str",
                        "heading": "str",
                        "excerpt": "str",
                    }
                ],
                "notes_used": ["str"],
                "warnings": ["str"],
                "retrieval": "retrieval_output",
            },
        },
        "error_types": [
            "invalid_arguments",
            "index_empty",
            "provider_error",
            "not_found",
            "internal_error",
        ],
    }


# -- command handlers ---------------------------------------------------------

def cmd_schema(args: argparse.Namespace) -> Dict[str, Any]:
    return success("schema", result=_schema(), meta={"version": SCHEMA_VERSION})


def cmd_sync(args: argparse.Namespace) -> Dict[str, Any]:
    root = args.root
    if not os.path.isdir(root):
        return failure("sync", "invalid_arguments", f"root directory not found: {root}")
    provider = get_provider()
    store = get_store(args.chroma_path, args.collection, provider)
    result = store.sync(root, reset=args.reset)
    return success("sync", result=result, meta={"root": root, "reset": args.reset})


def _run_retrieval(store, provider, query, mode, granularity, n_results):
    from vault_rag.retrieval.evidence import build_retrieval_output
    from vault_rag.retrieval.searcher import Searcher

    searcher = Searcher(store, granularity=granularity, provider=provider)
    result = searcher.hybrid_search(
        query, mode=mode, granularity=granularity, n_results=n_results
    )
    output = build_retrieval_output(query, mode, granularity, result.rows, store)
    return output, result


def cmd_retrieve(args: argparse.Namespace) -> Dict[str, Any]:
    if not args.query or not args.query.strip():
        return failure("retrieve", "invalid_arguments", "--query is required")
    provider = get_provider()
    store = get_store(args.chroma_path, args.collection, provider)
    if store.collection.count() == 0:
        return failure(
            "retrieve",
            "index_empty",
            "index is empty; run `vault-rag sync --root <dir>` first",
        )
    try:
        output, result = _run_retrieval(
            store, provider, args.query, args.mode, args.granularity, args.n
        )
    except OpenRouterError as exc:
        return failure("retrieve", "provider_error", str(exc))
    except ValueError as exc:
        return failure("retrieve", "not_found", str(exc))
    meta = {"timing_ms": round(result.timing_ms, 2), "tunables": result.debug_info}
    return success("retrieve", result=output, meta=meta)


def _load_retrieval_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and "candidates" in payload:
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("result"), dict):
        return payload["result"]
    raise ValueError("retrieval file is not a valid retrieve contract or envelope")


def cmd_synthesize(args: argparse.Namespace) -> Dict[str, Any]:
    provider = get_provider()

    if args.retrieval:
        try:
            retrieval_output = _load_retrieval_file(args.retrieval)
        except FileNotFoundError:
            return failure("synthesize", "not_found", f"retrieval file not found: {args.retrieval}")
        except (ValueError, json.JSONDecodeError) as exc:
            return failure("synthesize", "invalid_arguments", str(exc))
        query = args.query or str(retrieval_output.get("query", ""))
    else:
        query = args.query
        if not query or not query.strip():
            return failure(
                "synthesize",
                "invalid_arguments",
                "--query is required unless --retrieval is provided",
            )
        store = get_store(args.chroma_path, args.collection, provider)
        if store.collection.count() == 0:
            return failure(
                "synthesize",
                "index_empty",
                "index is empty; run `vault-rag sync --root <dir>` first",
            )
        try:
            retrieval_output, _ = _run_retrieval(
                store, provider, query, args.mode, args.granularity, args.n
            )
        except OpenRouterError as exc:
            return failure("synthesize", "provider_error", str(exc))
        except ValueError as exc:
            return failure("synthesize", "not_found", str(exc))

    from vault_rag.synthesis.answer import synthesize as synthesize_answer

    try:
        synth = synthesize_answer(
            provider, retrieval_output, question=query, hard_cutoff=args.n_context
        )
    except OpenRouterError as exc:
        return failure("synthesize", "provider_error", str(exc))

    synth["retrieval"] = retrieval_output
    return success("synthesize", result=synth)


# -- parser -------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vault-rag", description="Vault RAG JSON CLI")
    parser.add_argument("--chroma-path", default="chroma_db", help="Chroma persistence dir")
    parser.add_argument("--collection", default="vault_notes", help="Chroma collection name")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("schema", help="Print machine-readable command + contract schema")

    p_sync = sub.add_parser("sync", help="Incrementally sync the vault into the index")
    p_sync.add_argument("--root", required=True, help="Vault directory to index")
    p_sync.add_argument("--reset", action="store_true", help="Rebuild from scratch")

    p_retrieve = sub.add_parser("retrieve", help="Retrieve candidate notes")
    p_retrieve.add_argument("--query", required=True)
    p_retrieve.add_argument("--mode", choices=["fast", "thorough"], default="fast")
    p_retrieve.add_argument(
        "--granularity", choices=["document", "section", "mixed"], default="document"
    )
    p_retrieve.add_argument("-n", type=int, default=10)

    p_synth = sub.add_parser("synthesize", help="Retrieve then synthesize an answer")
    p_synth.add_argument("--query", default=None)
    p_synth.add_argument("--mode", choices=["fast", "thorough"], default="thorough")
    p_synth.add_argument(
        "--granularity", choices=["document", "section", "mixed"], default="mixed"
    )
    p_synth.add_argument("--retrieval", default=None, help="Prior retrieve envelope/contract")
    p_synth.add_argument("-n", type=int, default=10)
    p_synth.add_argument("--n-context", dest="n_context", type=int, default=8)

    return parser


_HANDLERS = {
    "schema": cmd_schema,
    "sync": cmd_sync,
    "retrieve": cmd_retrieve,
    "synthesize": cmd_synthesize,
}


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    handler = _HANDLERS[args.command]
    try:
        envelope = handler(args)
    except Exception as exc:  # noqa: BLE001 - top-level guard -> internal_error envelope
        envelope = failure(args.command, "internal_error", str(exc))

    print_json(envelope)
    return 0 if envelope.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
