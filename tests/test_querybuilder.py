"""Tests for querybuilder.build_select (pure SQL generation)."""

import unittest

import querybuilder
import schema_meta


class BuildSelectTests(unittest.TestCase):

    def setUp(self):
        self.students = schema_meta.get_source("Students")

    def test_minimal_select(self):
        sql, params = querybuilder.build_select(
            self.students, ["student_id"]
        )
        self.assertEqual(
            sql, "SELECT idstudents AS student_id\nFROM students"
        )
        self.assertEqual(params, ())

    def test_multiple_columns_alias_expressions(self):
        sql, _params = querybuilder.build_select(
            self.students, ["student_id", "last_name"]
        )
        self.assertIn("idstudents AS student_id", sql)
        self.assertIn("studentlastname AS last_name", sql)

    def test_comparison_operators(self):
        expected = {
            "=": "studentlastname = ?",
            "!=": "studentlastname <> ?",
            ">": "studentlastname > ?",
            ">=": "studentlastname >= ?",
            "<": "studentlastname < ?",
            "<=": "studentlastname <= ?",
        }
        for operator, clause in expected.items():
            with self.subTest(operator=operator):
                sql, params = querybuilder.build_select(
                    self.students,
                    ["student_id"],
                    conditions=[("last_name", operator, "x")],
                )
                self.assertIn(f"WHERE {clause}", sql)
                self.assertEqual(params, ("x",))

    def test_contains_wraps_value_in_wildcards(self):
        sql, params = querybuilder.build_select(
            self.students,
            ["student_id"],
            conditions=[("last_name", "contains", "mit")],
        )
        self.assertIn(
            "WHERE LOWER(studentlastname) LIKE LOWER(?)", sql
        )
        self.assertEqual(params, ("%mit%",))

    def test_starts_with_appends_wildcard(self):
        _sql, params = querybuilder.build_select(
            self.students,
            ["student_id"],
            conditions=[("last_name", "starts with", "Sm")],
        )
        self.assertEqual(params, ("Sm%",))

    def test_and_or_combinators(self):
        conditions = [
            ("last_name", "=", "Smith"),
            ("year_of_study", ">=", "2"),
        ]
        sql_and, params = querybuilder.build_select(
            self.students, ["student_id"], conditions=conditions
        )
        self.assertIn(
            "studentlastname = ? AND year_of_study >= ?", sql_and
        )
        self.assertEqual(params, ("Smith", "2"))
        sql_or, _params = querybuilder.build_select(
            self.students,
            ["student_id"],
            conditions=conditions,
            combinator="OR",
        )
        self.assertIn(
            "studentlastname = ? OR year_of_study >= ?", sql_or
        )

    def test_order_by_ascending_and_descending(self):
        sql, _params = querybuilder.build_select(
            self.students, ["student_id"], order_by="last_name"
        )
        self.assertTrue(sql.endswith("ORDER BY studentlastname"))
        sql, _params = querybuilder.build_select(
            self.students,
            ["student_id"],
            order_by="last_name",
            descending=True,
        )
        self.assertTrue(sql.endswith("ORDER BY studentlastname DESC"))

    def test_limit_accepts_int_and_numeric_string(self):
        for limit in (5, "5"):
            with self.subTest(limit=limit):
                sql, _params = querybuilder.build_select(
                    self.students, ["student_id"], limit=limit
                )
                self.assertTrue(sql.endswith("LIMIT 5"))

    def test_joined_source_from_clause(self):
        enrol = schema_meta.get_source("Enrolment details (joined)")
        sql, _params = querybuilder.build_select(
            enrol, ["student_id", "course_name"]
        )
        self.assertIn("FROM enrollments AS e", sql)
        self.assertIn("JOIN students AS s", sql)

    def test_rejects_empty_columns(self):
        with self.assertRaises(ValueError):
            querybuilder.build_select(self.students, [])

    def test_rejects_unknown_select_column(self):
        with self.assertRaises(ValueError):
            querybuilder.build_select(
                self.students, ["nope; DROP TABLE students"]
            )

    def test_rejects_unknown_filter_column(self):
        with self.assertRaises(ValueError):
            querybuilder.build_select(
                self.students,
                ["student_id"],
                conditions=[("evil", "=", "x")],
            )

    def test_rejects_unknown_operator(self):
        with self.assertRaises(ValueError):
            querybuilder.build_select(
                self.students,
                ["student_id"],
                conditions=[("last_name", "; --", "x")],
            )

    def test_rejects_unknown_sort_column(self):
        with self.assertRaises(ValueError):
            querybuilder.build_select(
                self.students, ["student_id"], order_by="evil"
            )

    def test_rejects_bad_combinator(self):
        with self.assertRaises(ValueError):
            querybuilder.build_select(
                self.students,
                ["student_id"],
                conditions=[("last_name", "=", "x")],
                combinator="AND 1=1",
            )

    def test_rejects_non_numeric_limit(self):
        with self.assertRaises(ValueError):
            querybuilder.build_select(
                self.students, ["student_id"], limit="abc"
            )

    def test_parameters_keep_condition_order(self):
        _sql, params = querybuilder.build_select(
            self.students,
            ["student_id"],
            conditions=[
                ("year_of_study", ">=", "2"),
                ("last_name", "contains", "a"),
            ],
        )
        self.assertEqual(params, ("2", "%a%"))


if __name__ == "__main__":
    unittest.main()
