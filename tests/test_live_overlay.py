"""Tests for the live lexical overlay (index.live_lexical): keyword search and cited
text track the live vault while embeddings stay those of the last sync."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import write_config

from vault_spider import cli, settings
from vault_spider.index.store import IndexStore
from vault_spider.retrieval.evidence import build_evidence
from vault_spider.retrieval.searcher import Searcher

FRESH = "xylophonic"  # appears only in notes written after the sync


def _store(chroma: Path, provider) -> IndexStore:
    return IndexStore(chroma_db_path=str(chroma), collection_name="vault_notes", provider=provider)


@pytest.fixture
def synced(tmp_path, tiny_vault, fake_provider):
    """A vault synced once, then a fresh store opened on the snapshot."""
    _store(tmp_path / "chroma", fake_provider).sync(str(tiny_vault))
    fake_provider.embed_calls.clear()
    store = _store(tmp_path / "chroma", fake_provider)
    return tiny_vault, store, fake_provider


def _note_ids(store: IndexStore, granularity: str = "document") -> set:
    return {m["note_id"] for m in store.metadatas[granularity]}


def _search_paths(store, query, granularity="document"):
    result = Searcher(store, granularity=granularity).hybrid_search(
        query, mode="fast", granularity=granularity, n_results=10
    )
    return [row["metadata"]["path"] for row in result.rows]


def test_overlay_on_an_unchanged_vault_is_a_noop(synced):
    vault, store, provider = synced
    before = {g: list(store.ids[g]) for g in ("document", "section")}

    report = store.apply_live_overlay(str(vault))

    assert report == {"applied": True, "notes": 5, "added": 0, "changed": 0, "removed": 0}
    assert {g: sorted(store.ids[g]) for g in before} == {g: sorted(v) for g, v in before.items()}
    assert not any("index_state" in m for m in store.metadatas["section"])
    assert provider.embed_calls == []


def test_new_note_is_keyword_searchable_without_embedding(synced):
    vault, store, provider = synced
    (vault / "fresh.md").write_text(
        f"---\ntitle: Fresh idea\n---\n# Plan\nThe {FRESH} plan for tomorrow.\n", encoding="utf-8"
    )
    chroma_count = store.collection.count()

    report = store.apply_live_overlay(str(vault))

    assert report["added"] == 1
    assert "fresh.md" in _search_paths(store, FRESH)[:1]
    assert "fresh.md" in _search_paths(store, FRESH, granularity="mixed")[:1]
    assert provider.embed_calls == [[FRESH]]  # only the query; no note was embedded
    assert store.collection.count() == chroma_count  # Chroma never written
    states = {m["index_state"] for m in store.metadatas["section"] if m["path"] == "fresh.md"}
    assert states == {"unembedded"}


def test_new_note_why_says_it_is_not_embedded_yet(synced):
    vault, store, _ = synced
    (vault / "fresh.md").write_text(f"The {FRESH} plan.\n", encoding="utf-8")
    store.apply_live_overlay(str(vault))
    row = next(
        r for r in Searcher(store).hybrid_search(FRESH, mode="fast", n_results=10).rows
        if r["metadata"]["path"] == "fresh.md"
    )
    assert build_evidence(row)["why"].endswith("; not embedded yet (keyword match only)")


def test_edited_note_uses_live_text_and_keeps_entry_ids(synced):
    vault, store, _ = synced
    doc_id = next(i for i, m in zip(store.ids["document"], store.metadatas["document"])
                  if m["path"] == "note_updated.md")
    path = vault / "note_updated.md"
    path.write_text(path.read_text(encoding="utf-8") + f"\nNow mentions {FRESH}.\n", encoding="utf-8")

    report = store.apply_live_overlay(str(vault))

    assert report["changed"] == 1
    index = store.ids["document"].index(doc_id)  # same id: the old vector still matches it
    assert FRESH in store.source_documents["document"][index]
    assert store.metadatas["document"][index]["index_state"] == "edited"
    assert "note_updated.md" in _search_paths(store, FRESH)[:1]


def test_deleted_note_is_dropped_even_from_dense_hits(synced):
    vault, store, _ = synced
    (vault / "note_plain.md").unlink()

    report = store.apply_live_overlay(str(vault))

    assert report["removed"] == 1
    assert all(m["path"] != "note_plain.md" for g in ("document", "section")
               for m in store.metadatas[g])
    # The vector is still in Chroma, but the searcher only ranks ids in the views.
    assert "note_plain.md" not in _search_paths(store, "plain body beta")


def test_moved_note_with_an_id_is_an_edit(tmp_path, tiny_vault, fake_provider):
    (tiny_vault / "with_id.md").write_text("---\nid: STABLE\n---\nMovable body.\n", encoding="utf-8")
    _store(tmp_path / "chroma", fake_provider).sync(str(tiny_vault))
    store = _store(tmp_path / "chroma", fake_provider)
    (tiny_vault / "Archive").mkdir()
    (tiny_vault / "with_id.md").rename(tiny_vault / "Archive" / "with_id.md")

    report = store.apply_live_overlay(str(tiny_vault))

    assert (report["added"], report["changed"], report["removed"]) == (0, 1, 0)
    assert {m["path"] for m in store.metadatas["document"] if m["note_id"] == "STABLE"} == {
        "Archive/with_id.md"
    }


def test_moved_note_without_an_id_is_a_new_note(synced):
    """Its id derives from its path, exactly as sync sees it: one removed, one added."""
    vault, store, _ = synced
    (vault / "Archive").mkdir()
    (vault / "note_a.md").rename(vault / "Archive" / "note_a.md")
    report = store.apply_live_overlay(str(vault))
    assert (report["added"], report["changed"], report["removed"]) == (1, 0, 1)


def test_overlay_keeps_exclusions_and_first_duplicate_id(synced):
    vault, store, _ = synced
    (vault / "z_secret.md").write_text(f"{FRESH} #secret\n", encoding="utf-8")
    (vault / ".hidden").mkdir()
    (vault / ".hidden" / "h.md").write_text(f"{FRESH} hidden\n", encoding="utf-8")
    (vault / "a_first.md").write_text(f"---\nid: DUP\n---\n{FRESH} first\n", encoding="utf-8")
    (vault / "b_second.md").write_text(f"---\nid: DUP\n---\n{FRESH} second\n", encoding="utf-8")

    report = store.apply_live_overlay(str(vault))

    assert report["added"] == 1
    paths = {m["path"] for m in store.metadatas["document"]}
    assert "a_first.md" in paths
    assert not paths & {"z_secret.md", ".hidden/h.md", "b_second.md"}


def test_overlay_rebuilds_bm25(synced):
    vault, store, _ = synced
    store.granularity_data("document")  # build BM25 over the snapshot
    (vault / "fresh.md").write_text(f"{FRESH}\n", encoding="utf-8")
    store.apply_live_overlay(str(vault))
    _, ids, _, bm25 = store.granularity_data("document")
    assert len(bm25.doc_len) == len(ids) == 6


def test_unchanged_entries_keep_snapshot_metadata(synced):
    """Snapshot entries (e.g. with note summaries) are reused, not rebuilt."""
    vault, store, _ = synced
    store.metadatas["section"][0]["context"] = "summary from the source machine"
    marked = store.ids["section"][0]
    (vault / "fresh.md").write_text(f"{FRESH}\n", encoding="utf-8")

    store.apply_live_overlay(str(vault))

    index = store.ids["section"].index(marked)
    assert store.metadatas["section"][index]["context"] == "summary from the source machine"


def test_sync_ignores_the_overlay(synced):
    """The overlay is query-time only: sync still embeds from the files and Chroma."""
    vault, store, provider = synced
    (vault / "fresh.md").write_text(f"{FRESH}\n", encoding="utf-8")
    store.apply_live_overlay(str(vault))
    result = store.sync(str(vault))
    assert result["added_notes"] == 1
    assert provider.embed_calls  # the new note was embedded by sync, not by the overlay


def test_imputation_puts_keyword_rank_one_at_the_best_semantic_score():
    import pandas as pd

    semantic = pd.Series({"a": 0.9, "b": 0.5, "c": 0.1, "new": 0.0})
    keyword = pd.Series({"a": 0.0, "b": 1.0, "c": 2.0, "new": 9.0})
    imputed = Searcher.impute_unembedded_semantic(semantic, keyword, ["new"])
    assert imputed["new"] == 0.9 and semantic["new"] == 0.0  # input untouched
    keyword_last = pd.Series({"a": 3.0, "b": 2.0, "c": 1.0, "new": 0.5})
    assert Searcher.impute_unembedded_semantic(semantic, keyword_last, ["new"])["new"] == 0.1
    assert Searcher.impute_unembedded_semantic(semantic, keyword, []) is semantic


def test_reported_semantic_score_of_a_new_note_stays_zero(synced):
    vault, store, _ = synced
    (vault / "fresh.md").write_text(f"The {FRESH} plan.\n", encoding="utf-8")
    store.apply_live_overlay(str(vault))
    result = Searcher(store).hybrid_search(FRESH, mode="fast", n_results=10)
    top = result.rows[0]
    assert top["metadata"]["path"] == "fresh.md" and top["semantic"] == 0.0
    assert result.debug_info["unembedded_candidates"] == 1


# -- settings and CLI ------------------------------------------------------------


def test_live_lexical_defaults_on_and_validates(isolated_config):
    assert settings.live_lexical_enabled() is True
    write_config(isolated_config, "index:\n  live_lexical: false\n")
    assert settings.live_lexical_enabled() is False
    write_config(isolated_config, "index:\n  live_lexical: sometimes\n")
    with pytest.raises(settings.ConfigError, match="live_lexical"):
        settings.live_lexical_enabled()


def _run(capsys, argv):
    code = cli.main(argv)
    return code, json.loads(capsys.readouterr().out)


@pytest.fixture
def cli_env(tmp_path, tiny_vault, fake_provider, monkeypatch, isolated_config, capsys):
    monkeypatch.setattr(cli, "get_provider", lambda: fake_provider)
    write_config(isolated_config, f"vault:\n  root: {tiny_vault}\n")
    chroma = str(tmp_path / "chroma")
    assert _run(capsys, ["--chroma-path", chroma, "sync"])[0] == 0
    (tiny_vault / "fresh.md").write_text(f"# Fresh\nThe {FRESH} plan.\n", encoding="utf-8")
    return chroma, isolated_config, tiny_vault


def test_cli_retrieve_finds_new_note_and_reports_overlay(cli_env, capsys):
    chroma, _, _ = cli_env
    code, envelope = _run(capsys, ["--chroma-path", chroma, "retrieve", "--query", FRESH])
    assert code == 0
    assert envelope["result"]["candidates"][0]["path"] == "fresh.md"
    overlay = envelope["meta"]["live_overlay"]
    assert overlay["applied"] is True and overlay["added"] == 1 and "timing_ms" in overlay


def test_cli_synthesize_can_cite_a_new_note(cli_env, capsys, fake_provider):
    chroma, _, _ = cli_env
    code, envelope = _run(
        capsys, ["--chroma-path", chroma, "synthesize", "--query", FRESH, "--mode", "fast"]
    )
    assert code == 0
    assert envelope["meta"]["live_overlay"]["added"] == 1
    sources = envelope["result"]["retrieval"]["candidates"]
    assert any(c["path"] == "fresh.md" and FRESH in c["excerpt"] for c in sources)


def test_cli_overlay_can_be_disabled(cli_env, capsys):
    chroma, config_dir, vault = cli_env
    write_config(config_dir, f"vault:\n  root: {vault}\nindex:\n  live_lexical: false\n")
    code, envelope = _run(capsys, ["--chroma-path", chroma, "retrieve", "--query", FRESH])
    assert code == 0
    assert envelope["meta"]["live_overlay"] == {
        "applied": False, "reason": "disabled (index.live_lexical: false)"}
    assert all(c["path"] != "fresh.md" for c in envelope["result"]["candidates"])


def test_cli_overlay_failure_falls_back_to_the_snapshot(cli_env, capsys):
    chroma, config_dir, _ = cli_env
    write_config(config_dir, "vault:\n  root: /nonexistent/vault\n")
    code, envelope = _run(capsys, ["--chroma-path", chroma, "retrieve", "--query", "alpha"])
    assert code == 0 and envelope["ok"] is True
    overlay = envelope["meta"]["live_overlay"]
    assert overlay["applied"] is False and "not found" in overlay["reason"]


# -- web app ---------------------------------------------------------------------


def test_web_state_reapplies_overlay_only_when_the_vault_changes(synced, monkeypatch):
    from vault_spider.web.state import AppState

    vault, store, provider = synced
    state = AppState(vault_root=str(vault), provider=provider, store=store,
                     searcher=Searcher(store, provider=provider))
    calls = []
    original = store.apply_live_overlay
    monkeypatch.setattr(store, "apply_live_overlay", lambda root: calls.append(root) or original(root))

    state.ensure_fresh_lexical()
    state.ensure_fresh_lexical()
    assert len(calls) == 1

    (vault / "fresh.md").write_text(f"{FRESH}\n", encoding="utf-8")
    state.ensure_fresh_lexical()
    assert len(calls) == 2
    assert "fresh.md" in {m["path"] for m in state.store.metadatas["document"]}
