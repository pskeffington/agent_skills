"""Study-neutral regression fixtures for the scientific reporting source screen."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".agents/skills/scientific-reporting-qa/scripts/report_source_audit.py"
SPEC = importlib.util.spec_from_file_location("report_source_audit", SOURCE)
audit_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_module)
audit = audit_module.audit


class ReportSourceAuditTests(unittest.TestCase):
    def test_clean_rmarkdown(self):
        source = (
            "# Methods\n\n"
            "\\[\nx = 1\n\\]\n\n"
            "```{r analysis, echo=TRUE}\n"
            "x <- 1\n"
            "```\n"
        )
        result = audit(source)
        self.assertEqual(result["status"], "source_screen_pass")
        self.assertEqual(result["chunks"], 1)
        self.assertEqual(result["math_open"], 1)

    def test_duplicate_chunks(self):
        source = "```{r x}\n1\n```\n```{r x}\n2\n```\n"
        self.assertIn("duplicate_chunk", self.kinds(source))

    def test_unclosed_fence(self):
        self.assertIn("unclosed_fence", self.kinds("```{r x}\n1\n"))

    def test_unbalanced_display_math(self):
        self.assertIn("display_math_mismatch", self.kinds("\\[\nx=1\n"))

    def test_escaped_tex_command(self):
        source = r"\\clearpage" + "\n"
        self.assertIn("possible_escaped_tex", self.kinds(source))

    def test_malformed_p_value(self):
        self.assertIn("malformed_p_value", self.kinds("The p-value is = .042\n"))

    def test_forbidden_transition(self):
        self.assertIn("house_style_word", self.kinds("Overall, the change was noted.\n"))

    def test_authorial_first_person(self):
        self.assertIn("possible_first_person", self.kinds("We calculated the estimate.\n"))

    @staticmethod
    def kinds(source):
        return {item["kind"] for item in audit(source)["issues"]}


if __name__ == "__main__":
    unittest.main()
