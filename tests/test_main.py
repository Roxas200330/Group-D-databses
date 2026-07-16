"""Tests for the command-line interface (main.py).

The interactive layer is driven headlessly: ``input()`` is patched
with a scripted sequence of answers and stdout is captured, so the
real prompt loop runs without a keyboard. Database access goes to an
in-memory seeded copy, never the real demo database file.
"""

import contextlib
import io
import sqlite3
import unittest
from unittest import mock

import db
import main
import queries
import support


def run_with_input(func, inputs, *args, **kwargs):
    """Run *func* with scripted input(); return (result, output).

    Raises StopIteration if *func* asks for more input than scripted,
    which doubles as a guard against unexpected extra prompts.
    """
    buffer = io.StringIO()
    with mock.patch("builtins.input", side_effect=inputs):
        with contextlib.redirect_stdout(buffer):
            result = func(*args, **kwargs)
    return result, buffer.getvalue()


class PromptParametersTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.database = support.make_test_database()

    @classmethod
    def tearDownClass(cls):
        cls.database.close()

    def test_empty_input_cancels(self):
        result, output = run_with_input(
            main.prompt_parameters,
            [""],
            (("Name", str, None),),
            self.database,
        )
        self.assertIsNone(result)
        self.assertIn("Cancelled", output)

    def test_invalid_number_reprompts_then_succeeds(self):
        result, output = run_with_input(
            main.prompt_parameters,
            ["abc", "1001"],
            (("Student ID", int, None),),
            self.database,
        )
        self.assertEqual(result, [1001])
        self.assertIn("Please enter a valid int", output)

    def test_values_are_converted_in_order(self):
        result, _output = run_with_input(
            main.prompt_parameters,
            ["Hopper", "72.5"],
            (("Surname", str, None), ("Threshold", float, None)),
            self.database,
        )
        self.assertEqual(result, ["Hopper", 72.5])

    def test_question_mark_lists_options(self):
        result, output = run_with_input(
            main.prompt_parameters,
            ["?", "Law"],
            (("Department", str, queries.department_names),),
            self.database,
        )
        self.assertEqual(result, ["Law"])
        self.assertIn("Options:", output)
        self.assertIn("Biology", output)
        self.assertIn("Medicine", output)

    def test_question_mark_listing_cascades(self):
        # Uses the real course-roster parameter specs: after the
        # course is entered, "?" must list only its lecturers.
        result, output = run_with_input(
            main.prompt_parameters,
            ["Linear Algebra", "?", "Noether"],
            queries.CATALOGUE[0]["params"],
            self.database,
        )
        self.assertEqual(result, ["Linear Algebra", "Noether"])
        self.assertIn("Options: Johnson, Noether", output)


class RunChoiceTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.database = support.make_test_database()

    @classmethod
    def tearDownClass(cls):
        cls.database.close()

    def test_runs_query_and_prints_table(self):
        _result, output = run_with_input(
            main.run_choice,
            ["Databases and Information Systems", "Hopper"],
            self.database,
            queries.CATALOGUE[0],
        )
        self.assertIn("(enter ? to list valid values)", output)
        self.assertIn("(14 rows)", output)

    def test_no_options_tip_for_free_text_parameters(self):
        _result, output = run_with_input(
            main.run_choice,
            ["70"],
            self.database,
            queries.CATALOGUE[4],  # grade threshold (no options)
        )
        self.assertNotIn("enter ? to list", output)
        self.assertIn("(7 rows)", output)

    def test_unknown_table_prints_friendly_error(self):
        _result, output = run_with_input(
            main.run_choice,
            ["secrets"],
            self.database,
            queries.CATALOGUE[8],  # show all rows in a chosen table
        )
        self.assertIn("Error: Unknown table 'secrets'", output)


class MainLoopTests(unittest.TestCase):

    def _run_main(self, inputs, database=None):
        if database is None:
            database = support.make_test_database()
        with mock.patch.object(
            main.db, "connect", return_value=database
        ):
            return run_with_input(main.main, inputs)

    def test_menu_lists_queries_and_exit(self):
        _result, output = self._run_main(["0"])
        self.assertIn("0. Exit", output)
        self.assertIn(queries.CATALOGUE[0]["title"], output)

    def test_exit_returns_zero(self):
        result, output = self._run_main(["0"])
        self.assertEqual(result, 0)
        self.assertIn("Goodbye.", output)

    def test_invalid_menu_choices_reprompt(self):
        result, output = self._run_main(["99", "abc", "0"])
        self.assertEqual(result, 0)
        self.assertEqual(
            output.count("Please enter a number between 0 and 9."),
            2,
        )

    def test_keyboard_interrupt_exits_cleanly_and_closes_db(self):
        database = support.make_test_database()
        buffer = io.StringIO()
        with mock.patch.object(
            main.db, "connect", return_value=database
        ):
            with mock.patch(
                "builtins.input", side_effect=KeyboardInterrupt
            ):
                with contextlib.redirect_stdout(buffer):
                    result = main.main()
        self.assertEqual(result, 0)
        self.assertIn("Goodbye.", buffer.getvalue())
        with self.assertRaises(sqlite3.ProgrammingError):
            database.run("SELECT 1")

    def test_connection_failure_reports_and_returns_one(self):
        with mock.patch.object(
            main.db, "connect",
            side_effect=db.DatabaseError("server unavailable"),
        ):
            result, output = run_with_input(main.main, [])
        self.assertEqual(result, 1)
        self.assertIn("Error: server unavailable", output)


if __name__ == "__main__":
    unittest.main()
