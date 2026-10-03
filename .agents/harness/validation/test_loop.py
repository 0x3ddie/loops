"""Exercise loop gates and recovery using synthetic evidence in isolated projects."""
import copy
from datetime import timedelta
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HARNESS = Path(__file__).resolve().parents[1]
SCRIPT = HARNESS.parent / "skills/work-improvement-loop/scripts/loop.py"
spec = importlib.util.spec_from_file_location("work_loop", SCRIPT)
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="loop-test-", dir=HARNESS / "validation")
        self.project = Path(self.temp.name).resolve()
        self.assertTrue(self.project.is_relative_to((HARNESS / "validation").resolve()))
        self.addCleanup(self.temp.cleanup)
        self.count = 0
        (self.project / "evaluate.py").write_text("# Synthetic evaluator fixture\n", encoding="utf-8")
        self.contract = {
            "schema_version": 1, "objective": "Reduce fixture latency", "scope": "Fixture only",
            "context": "Fixed fixture workload", "metric": {"name": "latency", "unit": "ms", "direction": "lower", "minimum_gain": 10},
            "minimum_samples": 3, "required_checks": ["correctness", "cost"], "protected_files": ["evaluate.py"],
            "maximum_candidates": 3, "deadline_utc": (loop.now() + timedelta(hours=1)).isoformat(),
            "release": {"mode": "offline"}, "regression_limit": {"current": 120, "margin": 5}}
        self.folder = self.project / ".agent-work/loops/test"

    def write(self, name, value):
        (self.project / name).write_text(json.dumps(value, allow_nan=False), encoding="utf-8")
        return name

    def start(self, flagged=False):
        if flagged:
            self.contract["release"] = {"mode": "flagged", "flag": "fixture", "field_context": "Synthetic cohort", "maximum_observations": 2, "rollback": "Restore fixture control"}
        return loop.initialize(self.project, "test", self.write("contract.json", self.contract))

    def evidence(self):
        self.count += 1
        name = f"raw-{self.count}.txt"
        (self.project / name).write_text(f"Synthetic test evidence {self.count}; no live measurement.\n", encoding="utf-8")
        return [name]

    def measured(self, revision="base", samples=None, field=False):
        return {"revision": revision, "context": "Synthetic cohort" if field else self.contract["context"],
                "metric": "latency", "unit": "ms", "samples": samples or [100, 101, 102],
                "checks": {"correctness": True, "cost": True}, "artifacts": self.evidence(),
                "hypothesis": "A smaller fixture implementation should be faster"}

    def record(self, kind, report):
        self.count += 1
        return loop.record(self.project, "test", kind, self.write(f"report-{self.count}.json", report))

    def candidate(self):
        self.record("baseline", self.measured())
        return self.record("candidate", self.measured("candidate", [70, 71, 72]))

    def review(self, passed=True, revision="candidate"):
        return self.record("review", {"revision": revision, "passed": passed, "reviewer": "Fixture reviewer", "notes": "Synthetic review", "artifacts": self.evidence()})

    def release(self):
        self.release_intent()
        return self.release_receipt()

    def release_intent(self):
        return self.record("release_intent", {"revision": "candidate", "flag": "fixture", "authorization": "Synthetic test, no release", "notes": "Fixture target and recovery", "artifacts": self.evidence()})

    def release_receipt(self):
        return self.record("release", {"revision": "candidate", "flag": "fixture", "deployment_id": "test-only", "authorization": "Synthetic test, no release", "artifacts": self.evidence()})

    def field(self, samples):
        return self.record("field", {"control": self.measured(field=True), "candidate": self.measured("candidate", samples, field=True)})

    def rollback(self, recovered=True):
        return self.record("rollback", {"revision": "candidate", "flag": "fixture", "recovered": recovered, "notes": "Synthetic recovery", "artifacts": self.evidence()})

    def ratchet(self, threshold=77):
        return self.record("ratchet", {"revision": "candidate", "threshold": threshold, "checks": {"correctness": True, "cost": True}, "artifacts": self.evidence()})

    def current(self):
        return loop.read_json(self.folder / "state.json")

    def assert_rejected_unchanged(self, action):
        before = (self.folder / "state.json").read_bytes()
        with self.assertRaises((loop.LoopError, KeyError)):
            action()
        self.assertEqual((self.folder / "state.json").read_bytes(), before)

    def test_offline_completion_and_immutable_closed_run(self):
        self.start()
        self.assertEqual(self.candidate()["phase"], "review")
        self.assertEqual(self.review()["phase"], "ratchet")
        state = self.ratchet()
        self.assertEqual(state["events"][-1]["decision"], "local_verified")
        self.assertEqual(state["accepted_threshold"], 77)
        self.assertEqual(loop.integrity(self.project, state), [])
        self.assert_rejected_unchanged(lambda: self.record("halt", {"reason": "Late mutation"}))

    def test_flagged_completion_requires_review_release_and_field(self):
        self.start(True)
        self.candidate()
        self.assert_rejected_unchanged(self.release)
        self.review()
        self.assert_rejected_unchanged(self.ratchet)
        self.release()
        self.assert_rejected_unchanged(self.ratchet)
        self.assertEqual(self.field([70, 71, 72])["phase"], "ratchet")
        self.assertEqual(self.ratchet()["events"][-1]["decision"], "field_verified")

    def test_quality_failure_rejects_a_faster_candidate(self):
        self.start()
        self.record("baseline", self.measured())
        report = self.measured("bad", [1, 2, 3])
        report["checks"]["correctness"] = False
        state = self.record("candidate", report)
        self.assertEqual(state["phase"], "candidate")
        self.assertEqual(state["attempts"], 1)
        self.assertNotIn("candidate", state)

    def test_contract_context_types_samples_and_artifacts_are_required(self):
        self.start()
        bad = [dict(context="different"), dict(unit="seconds"), dict(samples=[1, 2]),
               dict(samples=[1, 2, True]), dict(checks={"correctness": "true", "cost": True}),
               dict(artifacts=[]), dict(artifacts=["missing.txt"])]
        for changes in bad:
            with self.subTest(changes=changes):
                report = self.measured()
                report.update(changes)
                self.assert_rejected_unchanged(lambda: self.record("baseline", report))

    def test_wrong_revision_cannot_review_or_observe(self):
        self.start(True)
        self.candidate()
        self.assert_rejected_unchanged(lambda: self.review(revision="unmeasured"))
        self.review()
        self.release()
        report = {"control": self.measured("other", field=True), "candidate": self.measured("candidate", [70, 71, 72], field=True)}
        self.assert_rejected_unchanged(lambda: self.record("field", report))

    def test_regression_requires_verified_recovery_before_new_candidate(self):
        self.start(True)
        self.candidate()
        self.review()
        self.release()
        self.assertEqual(self.field([130, 131, 132])["phase"], "rollback")
        self.assert_rejected_unchanged(lambda: self.record("candidate", self.measured("new", [50, 51, 52])))
        state = self.rollback(False)
        self.assertTrue(state["live"])
        self.assertEqual(state["phase"], "rollback")
        state = self.rollback()
        self.assertFalse(state["live"])
        self.assertEqual(state["phase"], "candidate")

    def test_inconclusive_field_observation_budget_rolls_back(self):
        self.start(True)
        self.candidate()
        self.review()
        self.release()
        self.assertEqual(self.field([100, 101, 103])["phase"], "field")
        self.assertEqual(self.field([100, 101, 103])["phase"], "rollback")

    def test_halt_preserves_live_recovery_obligation_after_deadline(self):
        self.start(True)
        self.candidate()
        self.review()
        self.release()
        with patch.object(loop, "now", return_value=loop.now() + timedelta(days=1)):
            self.assertEqual(self.record("halt", {"reason": "Stop the fixture"})["phase"], "rollback")
            self.assertEqual(self.rollback()["phase"], "stopped")

    def test_deadline_and_candidate_budget_cannot_be_bypassed(self):
        self.contract["maximum_candidates"] = 1
        self.start()
        self.record("baseline", self.measured())
        with patch.object(loop, "now", return_value=loop.now() + timedelta(days=1)):
            self.assert_rejected_unchanged(lambda: self.record("candidate", self.measured("new")))
        self.assertEqual(self.record("candidate", self.measured("new"))["phase"], "stopped")

    def test_interrupted_release_cannot_close_without_external_reconciliation(self):
        self.start(True)
        self.candidate()
        self.review()
        self.assert_rejected_unchanged(self.release_receipt)
        self.release_intent()
        self.assertEqual(self.current()["phase"], "release_pending")
        self.record("halt", {"reason": "Release receipt missing after interruption"})
        self.assertEqual(self.current()["phase"], "rollback")
        self.assertEqual(self.rollback()["phase"], "stopped")

    def test_late_receipt_can_record_an_already_started_release(self):
        self.start(True)
        self.candidate()
        self.review()
        with patch.object(loop, "now", return_value=loop.now() + timedelta(days=1)):
            self.assert_rejected_unchanged(self.release_intent)
        self.release_intent()
        with patch.object(loop, "now", return_value=loop.now() + timedelta(days=1)):
            self.assertEqual(self.release_receipt()["phase"], "field")

    def test_evaluator_and_raw_evidence_changes_block_progress_but_allow_recovery(self):
        self.start(True)
        self.candidate()
        self.review()
        self.release()
        state = self.current()
        artifact = state["baseline"]["artifacts"][0]
        (self.project / artifact).write_text("changed", encoding="utf-8")
        (self.project / "evaluate.py").write_text("changed", encoding="utf-8")
        self.assertEqual(len(loop.integrity(self.project, state)), 2)
        self.assert_rejected_unchanged(lambda: self.field([70, 71, 72]))
        self.record("halt", {"reason": "Evidence corruption"})
        recovered = self.rollback()
        self.assertEqual(recovered["phase"], "stopped")
        self.assertEqual(len(recovered["events"][-1]["integrity_issues"]), 2)

    def test_no_overwrite_traversal_or_lock_stealing(self):
        self.start()
        before = (self.folder / "state.json").read_bytes()
        with self.assertRaises(FileExistsError):
            self.start()
        self.assert_rejected_unchanged(lambda: loop.record(self.project, "test", "baseline", "../outside.json"))
        with loop.locked(self.folder):
            self.assert_rejected_unchanged(lambda: self.record("baseline", self.measured()))
            self.assertTrue((self.folder / ".lock").exists())
        self.assertEqual((self.folder / "state.json").read_bytes(), before)

    def test_threshold_cannot_weaken_or_ignore_headroom(self):
        self.start()
        self.candidate()
        self.review()
        self.assert_rejected_unchanged(lambda: self.ratchet(119))
        state = copy.deepcopy(self.current())
        state["contract"]["regression_limit"]["current"] = 77
        with self.assertRaises(loop.LoopError):
            loop.threshold(state)

    def test_higher_is_better_and_noise_is_inconclusive(self):
        contract = copy.deepcopy(self.contract)
        contract["metric"]["direction"] = "higher"
        self.assertEqual(loop.compare(contract, {"samples": [100, 101, 102]}, {"samples": [120, 121, 122]}), "improved")
        self.assertEqual(loop.compare(contract, {"samples": [100, 101, 102]}, {"samples": [90, 110, 115]}), "inconclusive")
        state = {"contract": contract, "candidate": {"samples": [140, 141, 142]}}
        self.assertEqual(loop.threshold(state), 135)

    def test_cli_reports_bad_json_without_traceback_and_status_is_read_only(self):
        self.start()
        before = (self.folder / "state.json").read_bytes()
        cmd = [sys.executable, str(SCRIPT), "status", "--project", str(self.project), "--run", "test"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["phase"], "baseline")
        self.assertEqual((self.folder / "state.json").read_bytes(), before)
        for raw in ('[]', '{"value":NaN}', '{"x":1,"x":2}'):
            (self.project / "bad.json").write_text(raw, encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), "record", "--project", str(self.project), "--run", "test", "--kind", "baseline", "--evidence", "bad.json"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("error", json.loads(result.stdout))
            self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
