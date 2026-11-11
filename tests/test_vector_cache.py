"""Tests for vectors shared through the vault (vector_cache.py, sync export/import)."""

from __future__ import annotations

import json
import math
from array import array
from pathlib import Path

import pytest
from conftest import FakeProvider, write_config

from vault_spider import cli, settings
from vault_spider.index import vector_cache
from vault_spider.index.store import IndexStore
from vault_spider.index.vector_cache import VectorCache, VectorCacheError

H1, H2, H3 = ("1" * 64), ("2" * 64), ("a" + "3" * 63)
CACHE_DIR = "_vault-spider/vectors"


def _unit(*values):
    norm = math.sqrt(sum(v * v for v in values))
    return [v / norm for v in values]


# -- the file format -------------------------------------------------------------


def test_export_writes_content_addressed_files_and_manifest(tmp_path):
    cache = vector_cache.for_export(tmp_path, "google/gemini-embedding-2", 3)
    report = cache.export({H1: _unit(1, 2, 3), H3: _unit(3, 2, 1)}, extra={"note": "x"})

    assert report == {"written": 2, "deleted": 0, "total": 2}
    assert cache.directory == tmp_path / "google_gemini-embedding-2"
    assert (cache.directory / "11" / f"{H1}.vec").stat().st_size == 12
    assert (cache.directory / "a3" / f"{H3}.vec").is_file()
    manifest = json.loads((cache.directory / "manifest.json").read_text())
    assert manifest == {"format_version": 1, "embedding_model": "google/gemini-embedding-2",
                        "dimensions": 3, "dtype": "float32-le", "note": "x"}
    assert cache.get(H1) == pytest.approx(_unit(1, 2, 3), abs=1e-6)
    assert not (tmp_path / ".staging").exists() or not any((tmp_path / ".staging").iterdir())


def test_export_never_rewrites_unchanged_vectors(tmp_path):
    cache = vector_cache.for_export(tmp_path, "m", 3)
    cache.export({H1: _unit(1, 2, 3), H2: _unit(1, 1, 1)}, extra={})
    first = cache.path_for(H1).stat().st_mtime_ns
    manifest_mtime = (cache.directory / "manifest.json").stat().st_mtime_ns

    report = cache.export({H1: _unit(1, 2, 3), H3: _unit(2, 2, 1)}, extra={})

    assert report == {"written": 1, "deleted": 1, "total": 2}
    assert cache.path_for(H1).stat().st_mtime_ns == first
    assert not cache.path_for(H2).exists() and not (cache.directory / "22").exists()
    assert (cache.directory / "manifest.json").stat().st_mtime_ns == manifest_mtime


def test_export_rejects_inconsistent_dimensions(tmp_path):
    with pytest.raises(VectorCacheError, match="dimensions"):
        vector_cache.for_export(tmp_path, "m", 3).export({H1: [1.0, 0.0]}, extra={})


@pytest.mark.parametrize(
    "payload",
    [
        array("f", [1.0, 0.0]).tobytes(),  # partially synced / wrong length
        array("f", [float("nan"), 0.0, 1.0]).tobytes(),
        array("f", [0.0, 0.0, 0.0]).tobytes(),
        b"",
    ],
)
def test_invalid_files_read_as_missing(tmp_path, payload):
    cache = VectorCache(tmp_path / "m", "m", 3)
    path = cache.path_for(H1)
    path.parent.mkdir(parents=True)
    path.write_bytes(payload)
    assert cache.get(H1) is None


def test_get_rejects_non_hash_names(tmp_path):
    assert VectorCache(tmp_path, "m", 3).get("../../etc/passwd") is None


def test_for_import_finds_the_matching_model(tmp_path):
    vector_cache.for_export(tmp_path, "model-a", 3).export({H1: _unit(1, 2, 3)}, extra={})
    vector_cache.for_export(tmp_path, "model-b", 2).export({H1: _unit(1, 2)}, extra={})

    cache, manifest = vector_cache.for_import(tmp_path, "model-b")
    assert cache is not None and cache.dimensions == 2 and manifest["embedding_model"] == "model-b"

    missing, info = vector_cache.for_import(tmp_path, "model-c")
    assert missing is None and sorted(info["available_models"]) == ["model-a", "model-b"]

    aliased, _ = vector_cache.for_import(
        tmp_path, "alias-of-a", lambda exported, local: (exported, local) == ("model-a", "alias-of-a")
    )
    assert aliased is not None and aliased.model == "model-a"


def test_for_import_without_any_export(tmp_path):
    assert vector_cache.for_import(tmp_path / "absent", "m") == (None, {"available_models": []})


def test_for_import_rejects_two_matching_exports(tmp_path):
    vector_cache.for_export(tmp_path, "model-a", 3).export({H1: _unit(1, 2, 3)}, extra={})
    vector_cache.for_export(tmp_path, "model-b", 3).export({H1: _unit(1, 2, 3)}, extra={})
    with pytest.raises(VectorCacheError, match="more than one"):
        vector_cache.for_import(tmp_path, "either", lambda exported, local: True)


def test_for_import_rejects_unknown_format_versions(tmp_path):
    vector_cache.for_export(tmp_path, "m", 3).export({H1: _unit(1, 2, 3)}, extra={})
    manifest = tmp_path / "m" / "manifest.json"
    data = json.loads(manifest.read_text())
    data["format_version"] = 99
    manifest.write_text(json.dumps(data))
    with pytest.raises(VectorCacheError, match="format_version"):
        vector_cache.for_import(tmp_path, "m")


# -- sync: export on one machine, offline import on another ------------------------


def _store(chroma: Path, provider) -> IndexStore:
    return IndexStore(chroma_db_path=str(chroma), collection_name="vault_notes", provider=provider)


@pytest.fixture
def exported(tmp_path, tiny_vault):
    """The embedding machine: synced and exported into the vault."""
    source = FakeProvider()
    store = _store(tmp_path / "source-chroma", source)
    store.sync(str(tiny_vault))
    report = store.export_vectors(str(tiny_vault / CACHE_DIR))
    return tiny_vault, store, report


def _import_cache(vault: Path, model: str = "fake-embed") -> VectorCache:
    cache, _ = vector_cache.for_import(vault / CACHE_DIR, model)
    assert cache is not None
    return cache


def _vectors_by_id(store: IndexStore) -> dict:
    payload = store.collection.get(include=["embeddings"])
    return {i: list(e) for i, e in zip(payload["ids"], payload["embeddings"])}


def test_export_covers_every_index_entry(exported):
    vault, store, report = exported
    assert report["total"] == store.collection.count() and report["written"] == report["total"]
    manifest = json.loads((vault / CACHE_DIR / "fake-embed" / "manifest.json").read_text())
    assert manifest["contextual_state"] == "off" and manifest["chunk_schema_version"] >= 1


def test_offline_import_rebuilds_the_index_without_embedding(exported, tmp_path):
    vault, source_store, _ = exported
    importer = FakeProvider()
    store = _store(tmp_path / "laptop-chroma", importer)

    result = store.sync(str(vault), vector_cache=_import_cache(vault), offline=True)

    assert importer.embed_calls == []
    assert result["added_notes"] == 5
    assert result["vector_cache"]["pending_notes"] == 0
    source, imported = _vectors_by_id(source_store), _vectors_by_id(store)
    assert source.keys() == imported.keys()
    for entry_id, vector in source.items():
        assert imported[entry_id] == pytest.approx(vector, abs=1e-6)


def test_note_waits_until_all_its_vectors_have_arrived(exported, tmp_path):
    vault, source_store, _ = exported
    importer = FakeProvider()
    store = _store(tmp_path / "laptop-chroma", importer)
    store.sync(str(vault), vector_cache=_import_cache(vault), offline=True)
    before = {m["path"]: m["content_hash"] for m in store.metadatas["document"]}

    # The note syncs to this machine before its new vectors do.
    note = vault / "note_updated.md"
    note.write_text(note.read_text(encoding="utf-8") + "\n## Added\nBrand new section.\n",
                    encoding="utf-8")
    (vault / "brand_new.md").write_text("# New\nNo vectors for me yet.\n", encoding="utf-8")
    (vault / "note_plain.md").unlink()

    result = store.sync(str(vault), vector_cache=_import_cache(vault), offline=True)

    assert importer.embed_calls == []
    assert result["vector_cache"]["pending"] == ["brand_new.md", "note_updated.md"]
    assert result["deleted_notes"] == 1 and result["added_notes"] == 0
    after = {m["path"]: m["content_hash"] for m in store.metadatas["document"]}
    assert after["note_updated.md"] == before["note_updated.md"]  # old version kept whole
    assert "brand_new.md" not in after and "note_plain.md" not in after

    # The embedding machine catches up and exports; the next import completes both.
    source_store.sync(str(vault))
    source_store.export_vectors(str(vault / CACHE_DIR))
    result = store.sync(str(vault), vector_cache=_import_cache(vault), offline=True)

    assert importer.embed_calls == []
    assert result["vector_cache"]["pending_notes"] == 0
    assert (result["added_notes"], result["updated_notes"]) == (1, 1)
    assert _vectors_by_id(store).keys() == _vectors_by_id(source_store).keys()


def test_offline_sync_without_an_export_embeds_nothing(tmp_path, tiny_vault):
    importer = FakeProvider()
    result = _store(tmp_path / "chroma", importer).sync(str(tiny_vault), offline=True)
    assert importer.embed_calls == []
    assert result["added_notes"] == 0 and result["vector_cache"]["pending_notes"] == 5


def test_reset_import_rebuilds_from_the_cache(exported, tmp_path):
    vault, source_store, _ = exported
    store = _store(tmp_path / "laptop-chroma", FakeProvider())
    store.sync(str(vault), vector_cache=_import_cache(vault), offline=True)
    result = store.sync(str(vault), reset=True, vector_cache=_import_cache(vault), offline=True)
    assert result["added_notes"] == 5 and store.collection.count() == source_store.collection.count()


def test_vector_files_are_not_notes(exported):
    from vault_spider.corpus.loader import load_notes

    vault, _, _ = exported
    assert all(not note.path.startswith("_vault-spider/") for note in load_notes(str(vault)))


# -- settings and CLI --------------------------------------------------------------


def test_vector_cache_settings(isolated_config):
    assert settings.vector_cache_mode() == "off"
    assert settings.vector_cache_dir() == CACHE_DIR
    write_config(isolated_config, "index:\n  vector_cache_mode: sideways\n")
    with pytest.raises(settings.ConfigError, match="vector_cache_mode"):
        settings.vector_cache_mode()


def _run(capsys, argv):
    code = cli.main(argv)
    return code, json.loads(capsys.readouterr().out)


def test_cli_export_then_import(capsys, tmp_path, tiny_vault, monkeypatch, isolated_config):
    source, importer = FakeProvider(), FakeProvider()
    write_config(isolated_config, "index:\n  vector_cache_mode: export\n")
    monkeypatch.setattr(cli, "get_provider", lambda: source)
    code, envelope = _run(capsys, ["--chroma-path", str(tmp_path / "a"), "sync", "--root", str(tiny_vault)])
    assert code == 0
    export = envelope["result"]["vector_export"]
    assert export["written"] == export["total"] > 0 and envelope["meta"]["vector_cache_mode"] == "export"

    write_config(isolated_config, "index:\n  vector_cache_mode: import\n")
    monkeypatch.setattr(cli, "get_provider", lambda: importer)
    code, envelope = _run(capsys, ["--chroma-path", str(tmp_path / "b"), "sync", "--root", str(tiny_vault)])
    assert code == 0 and importer.embed_calls == []
    report = envelope["result"]["vector_cache"]
    assert report["export_found"] is True and report["pending_notes"] == 0
    assert envelope["result"]["added_notes"] == 5


def test_cli_import_without_export_warns(capsys, tmp_path, tiny_vault, monkeypatch, isolated_config,
                                         fake_provider):
    write_config(isolated_config, "index:\n  vector_cache_mode: import\n")
    monkeypatch.setattr(cli, "get_provider", lambda: fake_provider)
    code, envelope = _run(capsys, ["--chroma-path", str(tmp_path / "b"), "sync", "--root", str(tiny_vault)])
    assert code == 0 and fake_provider.embed_calls == []
    assert envelope["result"]["vector_cache"]["export_found"] is False
    assert any("no vector export" in w for w in envelope["result"]["warnings"])


def test_cli_import_refuses_contextual_mismatch(capsys, tmp_path, tiny_vault, monkeypatch,
                                                isolated_config, fake_provider):
    vector_cache.for_export(tiny_vault / CACHE_DIR, "fake-embed", 3).export(
        {H1: _unit(1, 2, 3)}, extra={"contextual_state": "on"})
    write_config(isolated_config, "index:\n  vector_cache_mode: import\n")
    monkeypatch.setattr(cli, "get_provider", lambda: fake_provider)
    code, envelope = _run(capsys, ["--chroma-path", str(tmp_path / "b"), "sync", "--root", str(tiny_vault)])
    assert code == 1 and envelope["error"]["type"] == "config_mismatch"


def test_cli_import_refuses_summary_generation(capsys, tiny_vault, isolated_config):
    write_config(isolated_config, "index:\n  vector_cache_mode: import\n  contextual: true\n")
    code, envelope = _run(capsys, ["sync", "--root", str(tiny_vault), "--contextualize"])
    assert code == 1 and envelope["error"]["type"] == "invalid_arguments"


def test_cli_import_accepts_an_equivalent_model_name(capsys, tmp_path, tiny_vault, monkeypatch,
                                                     isolated_config):
    source, importer = FakeProvider(), FakeProvider()
    source.embedding_model = "provider-a/embed"
    importer.embedding_model = "embed_on_b"
    write_config(isolated_config, "index:\n  vector_cache_mode: export\n")
    monkeypatch.setattr(cli, "get_provider", lambda: source)
    assert _run(capsys, ["--chroma-path", str(tmp_path / "a"), "sync", "--root", str(tiny_vault)])[0] == 0

    write_config(isolated_config, "index:\n  vector_cache_mode: import\n")
    monkeypatch.setattr(cli, "get_provider", lambda: importer)
    _, envelope = _run(capsys, ["--chroma-path", str(tmp_path / "b"), "sync", "--root", str(tiny_vault)])
    assert envelope["result"]["vector_cache"]["export_found"] is False  # different names, no group

    write_config(isolated_config, "index:\n  vector_cache_mode: import\n  embedding_model_equivalents:\n"
                                  "    - [provider-a/embed, embed_on_b]\n")
    _, envelope = _run(capsys, ["--chroma-path", str(tmp_path / "b"), "sync", "--root", str(tiny_vault)])
    assert envelope["result"]["vector_cache"]["export_found"] is True
    assert envelope["result"]["added_notes"] == 5 and importer.embed_calls == []
