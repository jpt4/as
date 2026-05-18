import unittest

from autarkic_systems.universal_cell import Cell, step_fixed_cell, step_stem_cell


EMPTY = ("_", "_", "_")
STATUS = "recipient-write-buffer-command-message-appended"


class RecipientWriteBufferCommandExecutionTests(unittest.TestCase):
    def test_fixed_cell_appends_delivered_write_buffer_zero_from_upstream(self):
        cell = Cell(
            role="wire",
            memory="right",
            upstream=("write-buf-zero", "_", "_"),
            buffer=(1,),
        )

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, STATUS)
        self.assertEqual(result.cell.role, "wire")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.upstream, EMPTY)
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, EMPTY)
        self.assertEqual(result.cell.automail, "_")
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, ())
        self.assertEqual(result.cell.buffer, (1, 0))

    def test_fixed_cell_appends_direct_write_buffer_one(self):
        cell = Cell(
            role="proc",
            memory="left",
            input=("_", "write-buf-one", "_"),
            buffer=(0,),
        )

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, STATUS)
        self.assertEqual(result.cell.role, "proc")
        self.assertEqual(result.cell.memory, "left")
        self.assertEqual(result.cell.upstream, EMPTY)
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.buffer, (0, 1))

    def test_stem_cell_appends_write_buffer_and_preserves_command_state(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=("_", "_", "write-buf-one"),
            self_mailbox="proc-r-init",
            control=(0, 1, 0),
            buffer=(1, 0),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, STATUS)
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, EMPTY)
        self.assertEqual(result.cell.automail, "_")
        self.assertEqual(result.cell.self_mailbox, "proc-r-init")
        self.assertEqual(result.cell.control, (0, 1, 0))
        self.assertEqual(result.cell.buffer, (1, 0, 1))

    def test_recipient_write_buffer_preserves_full_buffer_boundary(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=("write-buf-one", "_", "_"),
            control=(0, 0, 1),
            buffer=(1, 0, 1, 0, 1),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-buffer-full")
        self.assertEqual(result.cell, cell)

    def test_standard_signal_command_message_remains_rejected(self):
        cell = Cell(role="wire", memory="right", input=("standard-signal", "_", "_"))

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, "rejected-input")
        self.assertEqual(result.cell.input, EMPTY)

    def test_multi_command_message_conflict_still_rejects(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=("wire-r-init", "write-buf-one", "_"),
            control=(0, 0, 1),
            buffer=(1,),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "rejected-input")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.control, (0, 0, 1))
        self.assertEqual(result.cell.buffer, (1,))


if __name__ == "__main__":
    unittest.main()
