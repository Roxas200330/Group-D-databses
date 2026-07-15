"""Tests for the Tkinter GUI.

These tests drive the real widgets programmatically. They are
skipped automatically when no display is available (e.g. headless
CI), so the rest of the suite still runs everywhere.
"""

import unittest
from unittest import mock

try:
    import tkinter as tk
except ImportError:  # pragma: no cover - depends on installation
    tk = None

import queries
import support

if tk is not None:
    import gui


def _tk_available():
    if tk is None:
        return False
    try:
        root = tk.Tk()
    except tk.TclError:
        return False
    root.destroy()
    return True


@unittest.skipUnless(_tk_available(), "tkinter display not available")
class GuiTests(unittest.TestCase):

    def setUp(self):
        self.database = support.make_test_database()
        self.app = gui.App(self.database)
        self.app.withdraw()
        self.addCleanup(self.app._on_close)
        self.dialogs = []
        for name in ("showerror", "showwarning", "showinfo"):
            patcher = mock.patch.object(
                gui.messagebox, name, side_effect=self._recorder(name)
            )
            patcher.start()
            self.addCleanup(patcher.stop)

    def _recorder(self, kind):
        def record(*args, **kwargs):
            self.dialogs.append((kind, args))
        return record

    def _tree_rows(self):
        tree = self.app.results.tree
        return [tree.item(item)["values"]
                for item in tree.get_children()]

    # -- standard queries tab -----------------------------------------

    def test_parameter_fields_match_catalogue(self):
        tab = self.app.standard_tab
        for index, entry in enumerate(queries.CATALOGUE):
            with self.subTest(title=entry["title"]):
                tab.listbox.selection_clear(0, "end")
                tab.listbox.selection_set(index)
                tab._on_select()
                self.assertEqual(
                    len(tab.entries), len(entry["params"])
                )

    def test_standard_query_shows_results(self):
        tab = self.app.standard_tab
        tab.listbox.selection_clear(0, "end")
        tab.listbox.selection_set(0)
        tab._on_select()
        tab.entries[0][2].insert(
            0, "Databases and Information Systems"
        )
        tab.entries[1][2].insert(0, "Hopper")
        tab._run()
        rows = self._tree_rows()
        self.assertEqual(len(rows), 14)
        osei = [row for row in rows if row[2] == "Osei"]
        self.assertEqual(osei[0][4], "-")

    def test_missing_parameter_warns(self):
        tab = self.app.standard_tab
        tab.listbox.selection_clear(0, "end")
        tab.listbox.selection_set(0)
        tab._on_select()
        tab._run()
        self.assertEqual(self.dialogs[-1][0], "showwarning")

    def test_invalid_number_shows_error(self):
        tab = self.app.standard_tab
        tab.listbox.selection_clear(0, "end")
        tab.listbox.selection_set(5)  # advisor contact (int ID)
        tab._on_select()
        tab.entries[0][2].insert(0, "not-a-number")
        tab._run()
        self.assertEqual(self.dialogs[-1][0], "showerror")

    def test_unknown_table_shows_error(self):
        tab = self.app.standard_tab
        tab.listbox.selection_clear(0, "end")
        tab.listbox.selection_set(8)  # show all rows in a table
        tab._on_select()
        tab.entries[0][2].insert(0, "secrets")
        tab._run()
        self.assertEqual(self.dialogs[-1][0], "showerror")
        self.assertIn("Unknown table", self.dialogs[-1][1][1])

    # -- query builder tab --------------------------------------------

    def test_builder_filter_sort_and_preview(self):
        builder = self.app.builder_tab
        builder.source_var.set("Enrolment details (joined)")
        builder._on_source_change()
        column_box, operator_box, value_field = builder.conditions[0]
        column_box.set("grade")
        operator_box.set(">=")
        value_field.insert(0, "70")
        builder.order_box.set("grade")
        builder.descending_var.set(True)
        builder._run()
        rows = self._tree_rows()
        self.assertEqual(len(rows), 45)
        grades = [float(row[-1]) for row in rows]
        self.assertEqual(grades, sorted(grades, reverse=True))
        preview = builder.preview.get("1.0", "end")
        self.assertIn("SELECT", preview)
        self.assertIn("-- parameters", preview)

    def test_builder_no_columns_shows_error(self):
        builder = self.app.builder_tab
        builder.columns_list.selection_clear(0, "end")
        builder._run()
        self.assertEqual(self.dialogs[-1][0], "showerror")
        self.assertIn("at least one column", self.dialogs[-1][1][1])

    def test_builder_bad_limit_shows_error(self):
        builder = self.app.builder_tab
        builder.limit_field.insert(0, "lots")
        builder._run()
        self.assertEqual(self.dialogs[-1][0], "showerror")
        self.assertIn("whole number", self.dialogs[-1][1][1])

    def test_source_change_resets_filters(self):
        builder = self.app.builder_tab
        column_box, _operator_box, value_field = builder.conditions[0]
        column_box.set("last_name")
        value_field.insert(0, "Smith")
        builder.source_var.set("Courses")
        builder._on_source_change()
        self.assertEqual(column_box.get(), "")
        self.assertEqual(value_field.get(), "")
        selected = builder.columns_list.curselection()
        self.assertEqual(
            len(selected), builder.columns_list.size()
        )


if __name__ == "__main__":
    unittest.main()
