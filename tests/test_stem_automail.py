import unittest

from autarkic_systems.universal_cell import Cell, step_stem_cell


EMPTY = ("_", "_", "_")


class StemAutomailTests(unittest.TestCase):
    def test_wr_automail_reconfigures_stem_to_right_wire(self):
        result = step_stem_cell(Cell(role="stem", memory="right", automail="wr"))

        self.assertEqual(result.status, "automail-reconfigured")
        self.assertEqual(result.cell.role, "wire")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.automail, "_")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, EMPTY)

    def test_wl_automail_reconfigures_stem_to_left_wire(self):
        result = step_stem_cell(Cell(role="stem", memory="right", automail="wl"))

        self.assertEqual(result.status, "automail-reconfigured")
        self.assertEqual(result.cell.role, "wire")
        self.assertEqual(result.cell.memory, "left")
        self.assertEqual(result.cell.automail, "_")

    def test_pr_automail_reconfigures_stem_to_right_processor(self):
        result = step_stem_cell(Cell(role="stem", memory="left", automail="pr"))

        self.assertEqual(result.status, "automail-reconfigured")
        self.assertEqual(result.cell.role, "proc")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.automail, "_")

    def test_pl_automail_reconfigures_stem_to_left_processor(self):
        result = step_stem_cell(Cell(role="stem", memory="right", automail="pl"))

        self.assertEqual(result.status, "automail-reconfigured")
        self.assertEqual(result.cell.role, "proc")
        self.assertEqual(result.cell.memory, "left")
        self.assertEqual(result.cell.automail, "_")

    def test_stem_without_automail_is_idle(self):
        cell = Cell(role="stem", memory="right")

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "idle")
        self.assertEqual(result.cell, cell)

    def test_occupied_output_blocks_automail_without_consuming_it(self):
        cell = Cell(role="stem", memory="right", automail="wr", output=(1, "_", "_"))

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "blocked-output")
        self.assertEqual(result.cell, cell)

    def test_step_stem_rejects_fixed_role(self):
        with self.assertRaises(ValueError):
            step_stem_cell(Cell(role="wire", memory="right"))

    def test_invalid_automail_is_rejected(self):
        with self.assertRaises(ValueError):
            Cell(role="stem", memory="right", automail="bad")


if __name__ == "__main__":
    unittest.main()
