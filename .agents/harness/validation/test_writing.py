"""Check formatting detection, technical-content exclusions, and CLI preservation."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HARNESS = Path(__file__).resolve().parents[1]
SCRIPT = HARNESS.parent / "skills/humanizer/scripts/check_writing.py"
spec = importlib.util.spec_from_file_location("writing_check", SCRIPT)
writing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(writing)


class WritingTests(unittest.TestCase):
    def test_canned_update_and_decorative_formatting_are_reported(self):
        content = "Great question!\n\n## The result\n\n**Outcome:** Faster!\n\n---\n\n✅ Done.\n\nBottom line: let's dive in."
        rules = {item["rule"] for item in writing.check(content)}
        self.assertEqual(rules, {"canned-phrase", "decorative-heading", "bold-label", "horizontal-rule", "decorative-emoji"})

    def test_plain_update_keeps_facts_uncertainty_and_source(self):
        content = "The five fixture runs measured 310–318 ms, down from 420–431 ms. Correctness passed; the field test has not run.\n\nThe [run log](https://example.test/runs/14) contains the samples."
        self.assertEqual(writing.check(content), [])

    def test_document_structure_is_allowed_without_ignoring_filler(self):
        self.assertEqual(writing.check("# Release record\n\nMeasured on a fixed workload.\n\n---\n", "document"), [])
        self.assertTrue(writing.check("# Release record\n\nBottom line: done.", "document"))

    def test_code_quotes_frontmatter_and_link_targets_are_excluded(self):
        content = "---\ntitle: Great question\n---\n\n> Bottom line: quoted source.\n\n```text\n## Great question\n**Label:** Let's dive in.\n```\n\n~~~text\nBottom line\n~~~\n\nRead `let's dive in` in the [fixture](https://example.test/great-question).\n\n[fixture]: https://example.test/bottom-line\n"
        self.assertEqual(writing.check(content), [])

    def test_exact_repetition_is_reported_without_a_length_cap(self):
        paragraph = "The baseline and candidate used the same fixed workload and machine."
        self.assertEqual(writing.check(paragraph + "\n\n" + paragraph)[0]["rule"], "repeated-paragraph")
        detailed = "\n\n".join(f"Trial {index} used workload {index} and returned its separate latency distribution." for index in range(80))
        self.assertEqual(writing.check(detailed), [])

    def test_meaningful_lists_and_technical_terms_pass(self):
        content = "1. Measure the baseline.\n2. Run the candidate.\n3. Compare their distributions.\n\nThe robust standard error is 0.12."
        self.assertEqual(writing.check(content), [])

    def test_cli_never_modifies_original_prose_and_reports_missing_input(self):
        with tempfile.TemporaryDirectory(prefix="writing-test-", dir=HARNESS / "validation") as directory:
            root = Path(directory).resolve()
            self.assertTrue(root.is_relative_to((HARNESS / "validation").resolve()))
            path = root / "draft.md"
            content = "Great question!\n\nLatency was 420 ms. Field validation is pending.\n"
            path.write_text(content, encoding="utf-8")
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["findings"][0]["line"], 1)
            self.assertEqual(path.read_bytes(), before)
            result = subprocess.run([sys.executable, str(SCRIPT), str(root / "missing")], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("error", json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main(verbosity=2)
