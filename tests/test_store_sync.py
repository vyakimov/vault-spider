"""Tests for vault_spider.index.store.IndexStore.sync against a real Chroma db."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from vault_spider.corpus.loader import load_notes
from vault_spider.index.reader import DatabaseReader
from vault_spider.index.store import IndexStore
from vault_spider.llm.openrouter import OpenRouterError


def build_store(chroma_dir: Path, provider) -> IndexStore:
    return IndexStore(
        chroma_db_path=str(chroma_dir),
        collection_name="vault_notes",
        provider=provider,
    )


SOURCE_ID = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
TARGET_ID = "01ARZ3NDEKTSV4RRFFQ69G5FAW"


def write_link_vault(vault: Path, target_title: str = "Old target") -> None:
    vault.mkdir(exist_ok=True)
    (vault / "source.md").write_text(
        "---\n"
        f"id: {SOURCE_ID}\n"
        "title: Source\n"
        "date: 2024-01-01\n"
        "---\n"
        "See [[Old target]].\n",
        encoding="utf-8",
    )
    (vault / "target.md").write_text(
        "---\n"
        f"id: {TARGET_ID}\n"
        f"title: {target_title}\n"
        "date: 2024-01-01\n"
        "---\n"
        "Target body.\n",
        encoding="utf-8",
    )


def document_metadata(store: IndexStore, note_id: str) -> dict[str, object]:
    return next(
        metadata
        for metadata in store.metadatas["document"]
        if metadata.get("note_id") == note_id
    )


def test_initial_sync_adds_doc_and_section_entries(tmp_path, tiny_vault, fake_provider):
    store = build_store(tmp_path / "chroma", fake_provider)
    result = store.sync(str(tiny_vault))

    assert result["added_notes"] == 5  # note_secret is skipped
    assert result["updated_notes"] == 0
    assert result["deleted_notes"] == 0

    # One document entry per note, several section entries.
    assert len(store.metadatas["document"]) == 5
    assert len(store.metadatas["section"]) >= 5
    assert result["total_entries"] == store.collection.count()
    assert result["total_entries"] == (
        len(store.metadatas["document"]) + len(store.metadatas["section"])
    )
    assert result["graph_status"] == "ok"
    assert result["graph_nodes"] == 5
    assert result["graph_edges"] == 0
    assert result["graph_schema_version"] == 1


def test_secret_note_absent(tmp_path, tiny_vault, fake_provider):
    store = build_store(tmp_path / "chroma", fake_provider)
    store.sync(str(tiny_vault))
    titles = {m.get("title") for m in store.metadatas["document"]}
    assert "Secret note" not in titles


def test_editing_reembeds_only_that_note(tmp_path, tiny_vault, fake_provider):
    store = build_store(tmp_path / "chroma", fake_provider)
    store.sync(str(tiny_vault))
    fake_provider.embed_calls.clear()

    (tiny_vault / "note_plain.md").write_text(
        "Completely different plain content now.", encoding="utf-8"
    )
    result = store.sync(str(tiny_vault))

    assert result["updated_notes"] == 1
    assert result["unchanged"] == 4
    assert result["added_notes"] == 0
    # A single embed call containing only the edited note's entries (1 doc + 1 section).
    assert len(fake_provider.embed_calls) == 1
    assert len(fake_provider.embed_calls[0]) == 2


def test_deleting_a_file_removes_its_entries(tmp_path, tiny_vault, fake_provider):
    store = build_store(tmp_path / "chroma", fake_provider)
    store.sync(str(tiny_vault))

    (tiny_vault / "note_big.md").unlink()
    result = store.sync(str(tiny_vault))

    assert result["deleted_notes"] == 1
    titles = {m.get("title") for m in store.metadatas["document"]}
    assert "Big note" not in titles


def test_second_sync_is_noop(tmp_path, tiny_vault, fake_provider):
    store = build_store(tmp_path / "chroma", fake_provider)
    store.sync(str(tiny_vault))
    fake_provider.embed_calls.clear()

    result = store.sync(str(tiny_vault))
    assert result["unchanged"] == 5
    assert result["added_notes"] == 0
    assert result["updated_notes"] == 0
    assert result["deleted_notes"] == 0
    # No entries added -> no embedding work.
    assert fake_provider.embed_calls == []


def test_rehydrate_on_new_store_instance(tmp_path, tiny_vault, fake_provider):
    build_store(tmp_path / "chroma", fake_provider).sync(str(tiny_vault))

    fresh = build_store(tmp_path / "chroma", fake_provider)
    assert len(fresh.metadatas["document"]) == 5
    assert fresh.bm25["document"] is None
    assert fresh.bm25["section"] is None

    fresh.granularity_data("document")
    assert fresh.bm25["document"] is not None
    assert fresh.bm25["section"] is None

    fresh.granularity_data("section")
    assert fresh.bm25["document"] is not None
    assert fresh.bm25["section"] is not None


def test_graph_persists_and_rehydrates_with_symmetric_neighbors(
    tmp_path, fake_provider
):
    vault = tmp_path / "vault"
    write_link_vault(vault)
    chroma = tmp_path / "chroma"

    store = build_store(chroma, fake_provider)
    result = store.sync(str(vault))
    assert result["graph_records_changed"] == 2
    assert json.loads(document_metadata(store, SOURCE_ID)["graph_outgoing"]) == [
        TARGET_ID
    ]
    assert all(
        "graph_outgoing" not in metadata
        for metadata in store.metadatas["section"]
    )

    fresh = build_store(chroma, fake_provider)
    assert fresh.graph_status == "ok"
    assert fresh.graph_outgoing == {SOURCE_ID: {TARGET_ID}, TARGET_ID: set()}
    assert fresh.graph_incoming == {SOURCE_ID: set(), TARGET_ID: {SOURCE_ID}}
    assert fresh.graph_neighbors(SOURCE_ID) == {TARGET_ID}
    assert fresh.graph_neighbors(TARGET_ID) == {SOURCE_ID}
    assert fresh.graph_degree(SOURCE_ID) == 1
    stats = fresh.get_collection_stats()
    assert {
        key: stats[key]
        for key in (
            "graph_status",
            "graph_nodes",
            "graph_edges",
            "graph_schema_version",
        )
    } == {
        "graph_status": "ok",
        "graph_nodes": 2,
        "graph_edges": 1,
        "graph_schema_version": 1,
    }


def test_metadata_only_edge_change_updates_unchanged_linking_document(
    tmp_path, fake_provider
):
    vault = tmp_path / "vault"
    write_link_vault(vault)
    store = build_store(tmp_path / "chroma", fake_provider)
    store.sync(str(vault))
    source_before = dict(document_metadata(store, SOURCE_ID))

    write_link_vault(vault, target_title="New target")
    result = store.sync(str(vault))

    assert result["updated_notes"] == 1
    assert result["unchanged"] == 1
    assert result["graph_records_changed"] == 1
    source_after = dict(document_metadata(store, SOURCE_ID))
    assert json.loads(source_after["graph_outgoing"]) == []
    assert {
        key: value for key, value in source_after.items() if key != "graph_outgoing"
    } == {
        key: value for key, value in source_before.items() if key != "graph_outgoing"
    }
    assert store.graph_neighbors(SOURCE_ID) == set()


def test_graph_hash_mismatch_is_stale_and_disables_neighbors(
    tmp_path, fake_provider
):
    vault = tmp_path / "vault"
    write_link_vault(vault)
    chroma = tmp_path / "chroma"
    store = build_store(chroma, fake_provider)
    store.sync(str(vault))
    metadata = dict(store.collection.metadata or {})
    metadata["graph_snapshot_hash"] = "not-the-snapshot-hash"
    store.collection.modify(metadata=metadata)

    fresh = build_store(chroma, fake_provider)
    assert fresh.graph_status == "stale"
    assert fresh.graph_outgoing[SOURCE_ID] == {TARGET_ID}
    assert fresh.graph_neighbors(SOURCE_ID) == set()
    assert fresh.graph_degree(SOURCE_ID) == 0
    assert fresh.get_collection_stats()["graph_status"] == "stale"


def test_absent_graph_metadata_is_missing_and_ordinary_sync_backfills(
    tmp_path, fake_provider
):
    vault = tmp_path / "vault"
    write_link_vault(vault)
    chroma = tmp_path / "chroma"
    store = build_store(chroma, fake_provider)

    legacy_entries = []
    for note in load_notes(str(vault)):
        for entry_id, document, metadata in store._entries_for_note(note, set()):
            metadata.pop("graph_outgoing", None)
            legacy_entries.append((entry_id, document, metadata))
    legacy_documents = [entry[1] for entry in legacy_entries]
    store.collection.add(
        ids=[entry[0] for entry in legacy_entries],
        documents=legacy_documents,
        metadatas=[entry[2] for entry in legacy_entries],
        embeddings=fake_provider.embed_texts(legacy_documents),
    )

    missing = build_store(chroma, fake_provider)
    assert missing.graph_status == "missing"
    assert missing.graph_schema_version is None
    assert missing.graph_neighbors(SOURCE_ID) == set()

    fake_provider.embed_calls.clear()
    result = missing.sync(str(vault))
    assert result["graph_status"] == "ok"
    assert result["graph_records_changed"] == 2
    assert result["added_notes"] == result["updated_notes"] == 0
    assert fake_provider.embed_calls == []


def test_dry_run_reports_pending_graph_records_without_writing(
    tmp_path, fake_provider
):
    vault = tmp_path / "vault"
    write_link_vault(vault)
    chroma = tmp_path / "chroma"
    store = build_store(chroma, fake_provider)
    store.sync(str(vault))
    before_entries = store.collection.get(include=["documents", "metadatas"])
    before_collection_metadata = dict(store.collection.metadata or {})

    write_link_vault(vault, target_title="New target")
    dry = store.sync(str(vault), dry_run=True)

    assert dry["graph_records_changed"] == 1
    assert dry["graph_status"] == "ok"
    assert store.collection.get(include=["documents", "metadatas"]) == before_entries
    assert store.collection.metadata == before_collection_metadata


def test_graph_collection_metadata_preserves_embedding_model(
    tmp_path, fake_provider
):
    vault = tmp_path / "vault"
    write_link_vault(vault)
    store = build_store(tmp_path / "chroma", fake_provider)

    store.sync(str(vault))

    assert store.collection.metadata["embedding_model"] == fake_provider.embedding_model


def test_moving_a_note_updates_path_metadata(tmp_path, tiny_vault, fake_provider):
    # A frontmatter id keeps note_id stable across the move; only the path changes.
    (tiny_vault / "note_moved.md").write_text(
        "---\nid: 01ARZ3NDEKTSV4RRFFQ69G5FAV\ntitle: Movable\n---\nSame body.\n",
        encoding="utf-8",
    )
    store = build_store(tmp_path / "chroma", fake_provider)
    store.sync(str(tiny_vault))
    fake_provider.embed_calls.clear()

    archive = tiny_vault / "Archive"
    archive.mkdir()
    (tiny_vault / "note_moved.md").rename(archive / "note_moved.md")
    result = store.sync(str(tiny_vault))

    assert result["updated_notes"] == 1
    assert result["deleted_notes"] == 0
    assert result["added_notes"] == 0
    paths = {m.get("path") for m in store.metadatas["document"]}
    assert "Archive/note_moved.md" in paths
    assert "note_moved.md" not in paths
    assert len(fake_provider.embed_calls) == 1
    assert len(fake_provider.embed_calls[0]) == 1


def test_section_embeddings_are_reused_for_small_edits(
    tmp_path, tiny_vault, fake_provider
):
    store = build_store(tmp_path / "chroma", fake_provider)
    store.sync(str(tiny_vault))
    initial_count = store.collection.count()
    fake_provider.embed_calls.clear()

    note = tiny_vault / "note_a.md"
    note.write_text(
        note.read_text(encoding="utf-8") + "Changed detail marker.\n",
        encoding="utf-8",
    )
    result = store.sync(str(tiny_vault))

    assert result["updated_notes"] == 1
    assert len(fake_provider.embed_calls) == 1
    embedded = fake_provider.embed_calls[0]
    assert len(embedded) == 2
    assert all("Changed detail marker." in text for text in embedded)
    assert not any("# Overview\nAlpha overview paragraph." == text for text in embedded)
    assert store.collection.count() == initial_count
    assert store.granularity_data("section")[3] is not None


def test_duplicate_frontmatter_ids_skip_later_note(tmp_path, fake_provider):
    vault = tmp_path / "dupvault"
    vault.mkdir()
    (vault / "a.md").write_text(
        "---\nid: 01ARZ3NDEKTSV4RRFFQ69G5FAV\ntitle: First\n---\nBody A.\n",
        encoding="utf-8",
    )
    (vault / "b.md").write_text(
        "---\nid: 01ARZ3NDEKTSV4RRFFQ69G5FAV\ntitle: Second\n---\nBody B.\n",
        encoding="utf-8",
    )

    store = build_store(tmp_path / "chroma", fake_provider)
    result = store.sync(str(vault))

    assert result["added_notes"] == 1
    assert len(result["warnings"]) == 1
    assert "duplicate note id" in result["warnings"][0]
    assert "b.md" in result["warnings"][0]
    titles = {m.get("title") for m in store.metadatas["document"]}
    assert titles == {"First"}


def test_dry_run_predicts_sync_without_mutation(
    tmp_path, tiny_vault, fake_provider
):
    store = build_store(tmp_path / "chroma", fake_provider)
    store.sync(str(tiny_vault))
    initial_count = store.collection.count()
    fake_provider.embed_calls.clear()

    (tiny_vault / "note_plain.md").write_text("Changed beta body.\n", encoding="utf-8")
    (tiny_vault / "note_code.md").unlink()
    (tiny_vault / "note_new.md").write_text("A newly added note.\n", encoding="utf-8")

    dry = store.sync(str(tiny_vault), dry_run=True)

    assert dry["would_add"] == ["note_new.md"]
    assert dry["would_update"] == ["note_plain.md"]
    assert dry["would_delete"] == ["note_code.md"]
    assert (dry["added_notes"], dry["updated_notes"], dry["deleted_notes"]) == (1, 1, 1)
    assert dry["dry_run"] is True
    assert fake_provider.embed_calls == []
    assert store.collection.count() == initial_count

    real = store.sync(str(tiny_vault))

    assert (real["added_notes"], real["updated_notes"], real["deleted_notes"]) == (1, 1, 1)
    assert real["dry_run"] is False


def test_dry_run_with_reset_is_refused(tmp_path, tiny_vault, fake_provider):
    """A dry run must never be destructive; reset would drop the collection."""
    store = build_store(tmp_path / "chroma", fake_provider)
    store.sync(str(tiny_vault))
    count = store.collection.count()

    with pytest.raises(ValueError):
        store.sync(str(tiny_vault), reset=True, dry_run=True)

    assert store.collection.count() == count


def test_embedding_failure_leaves_existing_index_intact(
    tmp_path, tiny_vault, fake_provider, monkeypatch
):
    store = build_store(tmp_path / "chroma", fake_provider)
    store.sync(str(tiny_vault))

    def snapshot():
        payload = store.collection.get(include=["documents", "metadatas"])
        documents = payload.get("documents") or []
        metadatas = payload.get("metadatas") or []
        return {
            entry_id: (document, metadata)
            for entry_id, document, metadata in zip(
                payload["ids"], documents, metadatas
            )
        }

    before = snapshot()
    (tiny_vault / "note_plain.md").write_text(
        "This update cannot be embedded right now.\n", encoding="utf-8"
    )

    def fail(*args, **kwargs):
        raise OpenRouterError("temporary provider failure")

    monkeypatch.setattr(fake_provider, "embed_texts", fail)

    with pytest.raises(OpenRouterError, match="temporary provider failure"):
        store.sync(str(tiny_vault))

    assert snapshot() == before
    fresh = build_store(tmp_path / "chroma", fake_provider)
    assert fresh.graph_status == "ok"
    assert len(fresh.metadatas["document"]) == 5
    assert fresh.granularity_data("document")[3] is not None


def test_stats_reports_the_graph_through_the_read_only_reader(
    tmp_path, fake_provider
):
    """`vault-spider stats` is served by DatabaseReader, not IndexStore.

    The graph fields have to be judged there too, by the same rules — otherwise the
    one command anyone uses to check whether expansion is live silently omits it.
    """
    vault = tmp_path / "vault"
    write_link_vault(vault)
    chroma = tmp_path / "chroma"
    store = build_store(chroma, fake_provider)
    store.sync(str(vault))

    reader = DatabaseReader(str(chroma), "vault_notes")
    stats = reader.get_collection_stats()

    assert stats["graph_status"] == "ok"
    assert stats["graph_schema_version"] == 1
    assert stats["graph_nodes"] == store.get_collection_stats()["graph_nodes"]
    assert stats["graph_edges"] == store.get_collection_stats()["graph_edges"]
    assert stats["graph_edges"] == 1


def test_stats_reports_a_pre_graph_index_as_missing(tmp_path, fake_provider):
    """An index built before this feature must read as `missing`, never as an error."""
    vault = tmp_path / "vault"
    write_link_vault(vault)
    chroma = tmp_path / "chroma"
    store = build_store(chroma, fake_provider)
    store.sync(str(vault))
    # Strip the collection-level graph metadata the way an older build would have left it.
    store.collection.modify(metadata=store._collection_metadata())

    stats = DatabaseReader(str(chroma), "vault_notes").get_collection_stats()

    assert stats["graph_status"] == "missing"
    assert stats["graph_schema_version"] is None
