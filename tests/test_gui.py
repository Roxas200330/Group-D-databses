"""Tests for the Tkinter GUI.

These tests drive the real widgets programmatically. They are
skipped automatically when no display is available (e.g. headless
CI), so the rest of the suite still runs everywhere.
"""

import unittest
from unittest import mock

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:  # pragma: no cover - depends on installation
    tk = None
    ttk = None

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

    def test_parameter_dropdowns_offer_valid_values(self):
        tab = self.app.standard_tab
        tab.listbox.selection_clear(0, "end")
        tab.listbox.selection_set(0)
        tab._on_select()
        course_field = tab.entries[0][2]
        self.assertIsInstance(course_field, ttk.Combobox)
        self.assertIn(
            "Databases and Information Systems",
            course_field["values"],
        )

    def test_cascading_dropdowns_filter_each_other(self):
        tab = self.app.standard_tab
        tab.listbox.selection_clear(0, "end")
        tab.listbox.selection_set(0)
        tab._on_select()
        course_field = tab.entries[0][2]
        lecturer_field = tab.entries[1][2]
        # selection events are wired on both dropdowns
        self.assertTrue(course_field.bind("<<ComboboxSelected>>"))
        course_field.set("Linear Algebra")
        tab._refresh_options()
        self.assertEqual(
            set(lecturer_field["values"]), {"Johnson", "Noether"}
        )
        # the user's chosen course text is never touched
        self.assertEqual(course_field.get(), "Linear Algebra")

    def test_free_numeric_parameter_stays_plain_entry(self):
        tab = self.app.standard_tab
        tab.listbox.selection_clear(0, "end")
        tab.listbox.selection_set(4)  # grade threshold query
        tab._on_select()
        field = tab.entries[0][2]
        self.assertNotIsInstance(field, ttk.Combobox)

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

    # -- results pane -------------------------------------------------

    def _run_first_standard_query(self):
        tab = self.app.standard_tab
        tab.listbox.selection_clear(0, "end")
        tab.listbox.selection_set(0)
        tab._on_select()
        tab.entries[0][2].insert(
            0, "Databases and Information Systems"
        )
        tab.entries[1][2].insert(0, "Hopper")
        tab._run()

    def test_clear_button_empties_results(self):
        results = self.app.results
        self.assertEqual(
            str(results.clear_button["state"]), "disabled"
        )
        self._run_first_standard_query()
        self.assertEqual(
            str(results.clear_button["state"]), "normal"
        )
        results.clear_button.invoke()
        self.assertEqual(self._tree_rows(), [])
        self.assertFalse(results.tree["columns"])
        self.assertEqual(
            results.status["text"], "Run a query to see results."
        )
        self.assertEqual(
            str(results.clear_button["state"]), "disabled"
        )

    def test_results_are_centred(self):
        self._run_first_standard_query()
        tree = self.app.results.tree
        self.assertTrue(tree["columns"])
        for name in tree["columns"]:
            self.assertEqual(
                str(tree.heading(name)["anchor"]), "center"
            )
            self.assertEqual(
                str(tree.column(name)["anchor"]), "center"
            )

    def test_click_to_sort_columns(self):
        builder = self.app.builder_tab
        builder.source_var.set("Enrolment details (joined)")
        builder._on_source_change()
        builder._run()
        results = self.app.results
        tree = results.tree

        def grades():
            return [float(row[-1]) for row in self._tree_rows()
                    if row[-1] != "-"]

        self.assertTrue(tree.heading("grade")["command"])
        results._sort("grade")
        self.assertEqual(grades(), sorted(grades()))
        self.assertIn("▲", tree.heading("grade")["text"])
        results._sort("grade")
        self.assertEqual(grades(), sorted(grades(), reverse=True))
        self.assertIn("▼", tree.heading("grade")["text"])

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
