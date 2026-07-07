"""JSON envelope helpers (bearctl pattern) for the vault-rag CLI."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional


def success(
    action: str,
    result: Any = None,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "ok": True,
        "action": action,
        "result": result,
        "meta": meta or {},
    }


def failure(
    action: str,
    err_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "ok": False,
        "action": action,
        "error": {
            "type": err_type,
            "message": message,
            "details": details or {},
        },
    }


def print_json(payload: Dict[str, Any]) -> None:
    sys.stdout.write(
        json.dumps(payload, separators=(",", ":"), sort_keys=True, default=str)
    )
    sys.stdout.write("\n")
