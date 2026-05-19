import unittest

from autarkic_systems.project_status import build_project_status_report


class ProjectStatusSlimTests(unittest.TestCase):
    def test_report_accepts_with_proflog_integration(self):
        report = build_project_status_report()
        self.assertTrue(report["proflog_integration"]["accepted"])
        self.assertTrue(report["formal_confidence"]["accepted"])
        self.assertEqual(report["formal_confidence"]["status"], "integrated")


if __name__ == "__main__":
    unittest.main()
