import unittest

from autarkic_systems.formal_confidence import validate_formal_confidence_boundary


class FormalConfidenceBoundaryTests(unittest.TestCase):
    def test_boundary_integrated_with_proflog_not_blocked(self):
        report = validate_formal_confidence_boundary()
        self.assertTrue(report.accepted, report.failed_subjects)
        self.assertEqual(report.status, "integrated")
        self.assertEqual(report.target_id, "AS-FORMAL-CONFIDENCE-TARGET-001")


if __name__ == "__main__":
    unittest.main()
