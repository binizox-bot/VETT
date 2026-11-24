"""Regression tests for the J-gate tooling (04_verify/scripts). Offline, no model, no network.

The headline test is ``test_pretty_printed_variant_is_detected``: verifier (t8) showed that the
first C2 implementation parsed files line by line and ``break``-ed on the first failure, so a
**pretty-printed** ``{"t2_choice_template_version": "...choice.v9"}`` was silently skipped and
J8 stayed PASS.  That hole must never reopen, so the exact sample is reproduced here.

Run:
    cd VETT_R28_DIFFICULTY_20261112\\04_verify
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERIFY_ROOT = HERE.parent
sys.path.insert(0, str(VERIFY_ROOT / "scripts"))

import j_gate as g  # noqa: E402


def _tree(files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp(prefix="jg_test_"))
    for name, text in files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


class C2VariantScanTests(unittest.TestCase):
    """C2 must be a real double channel: raw bytes + JSON structure."""

    def test_pretty_printed_variant_is_detected(self):
        """t8 F4 regression: pretty JSON, variant suffix v9 (no 'choice.v1' substring)."""
        root = _tree({"t14_main/config.json": json.dumps(
            {"t2_choice_template_version": "T2.naturalness_pair.choice.v9"}, indent=2)})
        result = g.scan_variant_under(root)
        self.assertEqual(result["hit_files"], [],
                         "raw scan must not match: the string is choice.v9, not choice.v1")
        wheres = [h["where"] for h in result["structural_hits"]]
        self.assertIn("key:t2_choice_template_version", wheres)
        self.assertTrue(any(w.startswith("value:T2.naturalness_pair.choice") for w in wheres))
        self.assertEqual(result["unauditable"], [])

    def test_compact_variant_is_detected(self):
        root = _tree({"t14_main/c.json": '{"t2_choice_template_version":"choice"}'})
        self.assertTrue(g.scan_variant_under(root)["structural_hits"])

    def test_nested_pretty_variant_is_detected(self):
        root = _tree({"t14_main/n.json": json.dumps(
            {"a": {"b": {"t2_choice_template_version": "choice"}}}, indent=2)})
        wheres = [h["where"] for h in g.scan_variant_under(root)["structural_hits"]]
        self.assertIn("key:t2_choice_template_version", wheres)

    def test_jsonl_variant_is_detected(self):
        root = _tree({"t14_main/x.jsonl": '{"ok":1}\n{"t2_choice_template_version":"choice"}\n'})
        self.assertTrue(any(h["where"].startswith("key:") for h in
                            g.scan_variant_under(root)["structural_hits"]))

    def test_raw_token_hit(self):
        root = _tree({"t14_main/y.json": '{"note": "switched to T2.naturalness_pair.choice.v1"}'})
        result = g.scan_variant_under(root)
        self.assertEqual(len(result["hit_files"]), 1)
        self.assertTrue(result["structural_hits"])

    def test_prose_choice_is_not_a_hit(self):
        """R28 dossiers legitimately contain 'a choice between Stumped and Run out'."""
        root = _tree({"t14_main/p.json": json.dumps(
            {"degraded_text": "the wicket event required a choice between Stumped and Run out"},
            indent=2)})
        result = g.scan_variant_under(root)
        self.assertEqual(result["hit_files"], [])
        self.assertEqual(result["structural_hits"], [])
        self.assertEqual(len(result["prose_mentions"]), 1)

    def test_unparsable_file_is_reported_not_dropped(self):
        root = _tree({"t14_main/broken.json": "{not json"})
        result = g.scan_variant_under(root)
        self.assertEqual(len(result["unauditable"]), 1)
        self.assertIn("t14_main", result["unauditable"][0])

    def test_known_limit_fully_split_field_is_not_detected(self):
        """F6 characterisation test (verifier t8): C2 cannot see a token split *inside*.

        If this ever starts failing, C2 was hardened -> update J_GATE.md §17 item 10 and the
        captain ruling (the limit is documented, not silently fixed).
        """
        root = _tree({"t14_main/c.json": json.dumps(
            {"a": "T2.naturalness_pair.cho", "b": "ice.v9"}, indent=2)})
        result = g.scan_variant_under(root)
        self.assertEqual(result["structural_hits"], [])
        self.assertEqual(result["hit_files"], [])

    def test_named_split_is_caught(self):
        """The form the captain first named IS caught: the prefix alone matches the shape."""
        root = _tree({"t14_main/c.json": json.dumps(
            {"prefix": "T2.naturalness_pair.choice", "suffix": ".v9"}, indent=2)})
        self.assertTrue(g.scan_variant_under(root)["structural_hits"])

    def test_non_json_suffixes_are_ignored(self):
        root = _tree({"t14_main/notes.txt": "t2_choice_template_version choice"})
        result = g.scan_variant_under(root)
        self.assertEqual(result["hit_files"], [])
        self.assertEqual(result["structural_hits"], [])


class LiveTreeTests(unittest.TestCase):
    """The real production tree must be clean *for the right reasons*."""

    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((VERIFY_ROOT / "J_GATE.json").read_text(encoding="utf-8"))
        cls.j8 = cls.report["items"]["J8_template_hygiene"]

    def test_c2_clean(self):
        self.assertEqual(self.j8["variant_files_under_runs"], [])
        self.assertEqual(self.j8["structural_hit_count"], 0)

    def test_no_unauditable_production_file(self):
        self.assertEqual(self.j8["unauditable_production"], [])

    def test_c1_c3_c4_c5(self):
        self.assertEqual(self.j8["main_ledger_variant_entries"], 0)
        self.assertEqual(self.j8["main_annotation_variant_entries"], 0)
        self.assertTrue(self.j8["config_field"]["ok"])
        self.assertTrue(self.j8["cache_hit_provenance"]["ok"])
        self.assertEqual(self.j8["quarantine"]["verified"], self.j8["quarantine"]["files_listed"])
        self.assertEqual(self.j8["quarantine"]["referenced_by"], [])

    def test_j8_pass_and_no_blocking(self):
        self.assertEqual(self.j8["verdict"], "PASS")
        self.assertEqual(self.report["ruling"]["blocking"], [])


class PatternCoverageTests(unittest.TestCase):

    def test_namespace_audit_blocks_every_measured_prefix(self):
        import reaudit_packets as rp
        audit = rp.namespace_audit()
        self.assertGreaterEqual(len(audit), 13)
        misses = {k: v for k, v in audit.items() if v != "BLOCKED"}
        self.assertEqual(misses, {})

    def test_named_injections_blocked(self):
        import reaudit_packets as rp
        selftest = rp.self_test()
        misses = {k: v for k, v in selftest.items() if v not in ("BLOCKED", "PASS")}
        self.assertEqual(misses, {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
