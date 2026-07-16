"""Tests for display.format_table."""

import unittest

import display


class FormatTableTests(unittest.TestCase):

    def test_no_rows_returns_message(self):
        result = display.format_table(["a", "b"], [])
        self.assertEqual(result, "No results found.")

    def test_single_row_layout(self):
        text = display.format_table(["id", "name"], [(1, "Alice")])
        lines = text.splitlines()
        self.assertEqual(lines[0], "id | name ")
        self.assertEqual(lines[1], "---+------")
        self.assertEqual(lines[2], "1  | Alice")
        self.assertEqual(lines[3], "(1 row)")

    def test_footer_pluralises(self):
        text = display.format_table(["x"], [(1,), (2,)])
        self.assertTrue(text.endswith("(2 rows)"))

    def test_none_rendered_as_dash(self):
        text = display.format_table(["grade"], [(None,)])
        lines = text.splitlines()
        self.assertEqual(lines[2].rstrip(), "-")

    def test_wide_value_stretches_column(self):
        text = display.format_table(
            ["h"], [("a much longer value",)]
        )
        lines = text.splitlines()
        self.assertEqual(len(lines[1]), len("a much longer value"))

    def test_column_count_matches_headers(self):
        text = display.format_table(
            ["a", "b", "c"], [(1, 2, 3)]
        )
        self.assertEqual(text.splitlines()[0].count("|"), 2)


if __name__ == "__main__":
    unittest.main()
