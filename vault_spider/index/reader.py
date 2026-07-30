"""Read-only Chroma access for Vault Spider."""

from __future__ import annotations

from typing import Any, Dict

import chromadb
from chromadb.errors import NotFoundError


class DatabaseReader:
    def __init__(
        self,
        chroma_db_path: str = "chroma_db",
        collection_name: str = "vault_notes",
    ):
        self.chroma_db_path = chroma_db_path
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=chroma_db_path)
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except (ValueError, NotFoundError):
            self.collection = None

    def get_collection_stats(self) -> Dict[str, object]:
        if self.collection is None:
            return {"error": "Collection not found"}

        payload = self.collection.get(include=["metadatas"])
        metadatas: list[dict[str, Any]] = [
            dict(metadata) for metadata in payload.get("metadatas") or []
        ]
        document_metas = [
            metadata
            for metadata in metadatas
            if metadata.get("granularity", "document") == "document"
        ]
        folders = {
            str(metadata.get("folder", ""))
            for metadata in document_metas
            if metadata.get("folder")
        }
        tags = set()
        dated_notes = 0
        section_metas = [
            metadata
            for metadata in metadatas
            if metadata.get("granularity") == "section"
        ]
        eligible_sections = sum(
            bool(metadata.get("context_eligible")) for metadata in section_metas
        )
        ready_sections = sum(
            metadata.get("context_status") == "ready" for metadata in section_metas
        )
        collection_metadata = self.collection.metadata or {}
        contextual_enabled = collection_metadata.get("contextual_state") == "on"
        for metadata in document_metas:
            tag_string = metadata.get("tags", "")
            if tag_string:
                tags.update(
                    tag.strip()
                    for tag in str(tag_string).split(",")
                    if tag.strip()
                )
            if metadata.get("date"):
                dated_notes += 1

        return {
            "total_documents": len(document_metas),
            "total_entries": self.collection.count(),
            "section_entries": sum(
                metadata.get("granularity") == "section" for metadata in metadatas
            ),
            "unique_folders": len(folders),
            "unique_tags": len(tags),
            "dated_notes": dated_notes,
            "embedding_model": collection_metadata.get("embedding_model", "unknown"),
            "chunk_schema_version": collection_metadata.get(
                "chunk_schema_version", "unknown"
            ),
            "context_prompt_version": collection_metadata.get(
                "context_prompt_version", "unknown"
            ),
            "context_model": collection_metadata.get("context_model", ""),
            "context_source": collection_metadata.get("context_source", "off"),
            "context_eligible_sections": eligible_sections,
            "context_ready_sections": ready_sections,
            "context_stale_sections": (
                max(0, eligible_sections - ready_sections)
                if contextual_enabled
                else 0
            ),
            "context_coverage": (
                round(ready_sections / eligible_sections, 4)
                if contextual_enabled and eligible_sections
                else 1.0
            ),
            "context_missing_notes": sum(
                metadata.get("context_status") == "missing"
                for metadata in document_metas
            ),
            "context_stale_notes": sum(
                metadata.get("context_status") == "stale"
                for metadata in document_metas
            ),
        }
