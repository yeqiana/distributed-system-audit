"""Verify fixed inputs and recorded synthetic observations against execution."""

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


FIXTURES = Path(__file__).resolve().parents[1] / "evals/fixtures"
spec = importlib.util.spec_from_file_location("synthetic_scenarios", FIXTURES / "scenarios.py")
scenarios = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scenarios)
prepare_spec = importlib.util.spec_from_file_location("prepare_evaluation", FIXTURES.parents[1] / "scripts/prepare_behavior_eval.py")
preparation = importlib.util.module_from_spec(prepare_spec)
prepare_spec.loader.exec_module(preparation)


class FixtureTests(unittest.TestCase):
    def test_workspace_preparation_is_isolated_and_preserves_dirty_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            output = preparation.prepare(Path(directory) / "run")
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(11, len(manifest["cases"]))
            for case_id, case in manifest["cases"].items():
                for name, digest in case["input_hashes"].items():
                    self.assertEqual(digest, preparation.digest(output / case_id / name))
            workspace = output / "E07/workspace"
            status = subprocess.run(["git", "status", "--porcelain"], cwd=workspace, capture_output=True, text=True, check=True).stdout
            self.assertEqual(" M worker.py\n", status)
            self.assertTrue((workspace / "existing_smoke.py").is_file())
            self.assertEqual(status, manifest["cases"]["E07"]["git_status_before"])

    def test_workspace_preparation_rejects_source_tree(self):
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            preparation.prepare(preparation.ROOT / ".eval-runs/rejected")

    def test_recorded_observations_are_reproducible(self):
        recorded = json.loads((FIXTURES / "observations.json").read_text(encoding="utf-8"))
        self.assertEqual(recorded, scenarios.observe())

    def test_models_exercise_positive_and_negative_evidence(self):
        observed = scenarios.observe()
        self.assertEqual("A-result", observed["lease_plain"]["steps"][-1]["row"]["result"])
        self.assertEqual(0, observed["lease_guarded"]["steps"][-1]["affected"])
        self.assertEqual("B-result", observed["lease_guarded"]["steps"][-1]["row"]["result"])
        self.assertEqual({"SENT": 99, "PENDING": 1}, observed["delivery"]["receipt_counts"])
        self.assertFalse(observed["read_health"]["reader_valid"])
        self.assertTrue(observed["read_health"]["reconcile_healthy"])
        self.assertEqual((3, 0), (observed["outbox"]["fact_count"], observed["outbox"]["event_count"]))
        self.assertEqual([1, 0], observed["lease_free"]["completion_updates"])
        self.assertEqual(1, observed["lease_free"]["effect_count"])

    def test_all_cases_have_fixed_inputs_without_embedded_scores(self):
        fixtures = json.loads((FIXTURES / "cases.json").read_text(encoding="utf-8"))
        self.assertEqual([f"E{i:02}" for i in range(1, 12)], [case["id"] for case in fixtures["cases"]])
        observed = scenarios.observe()
        for case in fixtures["cases"]:
            self.assertTrue(case["request"])
            self.assertIsInstance(case["artifacts"], dict)
            self.assertNotIn("expected", case)
            if "observation" in case:
                self.assertIn(case["observation"], observed)
            for name in [*case["artifacts"], *case.get("baseline_files", {}), *case.get("workspace_files", {})]:
                self.assertEqual(Path(name).name, name)


if __name__ == "__main__":
    unittest.main()
