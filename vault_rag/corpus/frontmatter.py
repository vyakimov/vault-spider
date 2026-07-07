"""Frontmatter parsing and normalization helpers."""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Tuple

import yaml


def split_frontmatter(raw_text: str) -> Tuple[Dict[str, Any], str]:
    if not raw_text.startswith("---\n"):
        return {}, raw_text

    lines = raw_text.splitlines()
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            frontmatter = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :]).lstrip("\n")
            try:
                parsed = yaml.safe_load(frontmatter) or {}
                if isinstance(parsed, dict):
                    return parsed, body
            except yaml.YAMLError:
                return {}, raw_text
            return {}, body
    return {}, raw_text


def normalize_tags(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        separators = "," if "," in value else None
        parts = value.split(separators) if separators else value.split()
        return [part.strip() for part in parts if part.strip()]
    return [str(value).strip()]


def coerce_datetime(value: Any) -> dt.datetime | None:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value if value.tzinfo else value.replace(tzinfo=dt.timezone.utc)
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time.min, tzinfo=dt.timezone.utc)
    if isinstance(value, str):
        candidate = value.strip().replace("Z", "+00:00")
        for parser in (dt.datetime.fromisoformat,):
            try:
                parsed = parser(candidate)
                return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)
            except ValueError:
                continue
        try:
            parsed_date = dt.date.fromisoformat(candidate)
            return dt.datetime.combine(parsed_date, dt.time.min, tzinfo=dt.timezone.utc)
        except ValueError:
            return None
    return None
