import unittest

from autarkic_systems.sean_fork_sjas_correlation import (
    load_correlation_map,
    validate_sean_fork_sjas_correlation,
)


class SeanForkSjasCorrelationTests(unittest.TestCase):
    def test_correlation_map_loads_and_validates(self):
        correlation = load_correlation_map()
        self.assertEqual(correlation["archive_branch"], "archive/sean-fork-full")
        self.assertGreaterEqual(len(correlation["translations"]), 10)

    def test_correlation_accepted_against_pin_and_witness(self):
        report = validate_sean_fork_sjas_correlation()
        self.assertTrue(report.accepted, report.failed_subjects)
        self.assertGreater(report.implemented_count, 8)


if __name__ == "__main__":
    unittest.main()
