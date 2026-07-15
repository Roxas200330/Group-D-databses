"""Tests for the query engine functions against the seeded schema."""

import unittest

import queries
import schema_meta
import support


class QueryFunctionTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.database = support.make_test_database()

    @classmethod
    def tearDownClass(cls):
        cls.database.close()

    # -- students_in_course -------------------------------------------

    def test_course_roster(self):
        _cols, rows = queries.students_in_course(
            self.database, "Databases and Information Systems",
            "Hopper",
        )
        self.assertEqual(len(rows), 14)
        self.assertEqual(
            {row[0] for row in rows},
            {1001, 1002, 1003, 1004, 1005, 1008, 1010,
             1011, 1015, 1017, 1020, 1022, 1024, 1028},
        )

    def test_course_roster_includes_in_progress_grade(self):
        _cols, rows = queries.students_in_course(
            self.database, "Databases and Information Systems",
            "Hopper",
        )
        osei = [row for row in rows if row[2] == "Osei"]
        self.assertEqual(len(osei), 1)
        self.assertIsNone(osei[0][4])

    def test_course_roster_is_case_insensitive(self):
        _cols, rows = queries.students_in_course(
            self.database, "databases and information systems",
            "hopper",
        )
        self.assertEqual(len(rows), 14)

    def test_course_roster_unknown_course_empty(self):
        _cols, rows = queries.students_in_course(
            self.database, "Basket Weaving", "Hopper"
        )
        self.assertEqual(rows, [])

    # -- unregistered_students ----------------------------------------

    def test_unregistered_current_semester(self):
        _cols, rows = queries.unregistered_students(
            self.database, "2026-S2"
        )
        self.assertEqual(
            {row[0] for row in rows},
            {1002, 1009, 1015, 1021, 1027},
        )

    def test_unregistered_includes_deferred_students(self):
        _cols, rows = queries.unregistered_students(
            self.database, "2026-S2"
        )
        self.assertIn(1021, {row[0] for row in rows})

    def test_unregistered_excludes_graduated(self):
        _cols, rows = queries.unregistered_students(
            self.database, "2026-S2"
        )
        self.assertNotIn(1010, {row[0] for row in rows})

    def test_unregistered_past_semester(self):
        _cols, rows = queries.unregistered_students(
            self.database, "2025-S1"
        )
        self.assertEqual(
            {row[0] for row in rows},
            {1004, 1005, 1006, 1007, 1009, 1011, 1012, 1014,
             1015, 1016, 1017, 1019, 1021, 1023, 1025, 1027,
             1028, 1029, 1030},
        )

    # -- lecturers_by_expertise ---------------------------------------

    def test_expertise_partial_match(self):
        _cols, rows = queries.lecturers_by_expertise(
            self.database, "machine"
        )
        self.assertEqual(
            {row[2] for row in rows}, {"Turing", "Lovelace"}
        )

    def test_expertise_matches_databases(self):
        _cols, rows = queries.lecturers_by_expertise(
            self.database, "data"
        )
        self.assertEqual(
            {row[2] for row in rows},
            {"Lovelace", "Hopper", "Liskov", "Ginsburg"},
        )

    def test_expertise_no_match(self):
        _cols, rows = queries.lecturers_by_expertise(
            self.database, "underwater basket weaving"
        )
        self.assertEqual(rows, [])

    # -- courses_by_department ----------------------------------------

    def test_courses_by_department(self):
        _cols, rows = queries.courses_by_department(
            self.database, "Computer Science"
        )
        self.assertEqual(
            {row[0] for row in rows},
            {101, 102, 103, 203, 204, 205},
        )

    def test_courses_by_other_department(self):
        _cols, rows = queries.courses_by_department(
            self.database, "Mathematics"
        )
        self.assertEqual({row[0] for row in rows}, {104, 105})

    def test_courses_unknown_department_empty(self):
        _cols, rows = queries.courses_by_department(
            self.database, "Astrology"
        )
        self.assertEqual(rows, [])

    # -- top_final_year_students --------------------------------------

    def test_final_year_averages_and_order(self):
        _cols, rows = queries.top_final_year_students(
            self.database, 70
        )
        self.assertEqual(
            [(row[0], row[5]) for row in rows],
            [(1013, 85.0), (1020, 82.0), (1008, 80.0),
             (1001, 78.0), (1017, 74.5), (1026, 72.0),
             (1003, 71.0)],
        )

    def test_final_year_excludes_low_average_and_graduated(self):
        _cols, rows = queries.top_final_year_students(
            self.database, 70
        )
        ids = {row[0] for row in rows}
        self.assertNotIn(1002, ids)  # average 61.7
        self.assertNotIn(1010, ids)  # graduated
        self.assertNotIn(1019, ids)  # average 69.0, just below
        self.assertNotIn(1028, ids)  # average exactly 70 (not > 70)

    def test_final_year_threshold_is_applied(self):
        _cols, rows = queries.top_final_year_students(
            self.database, 79
        )
        self.assertEqual(
            [row[0] for row in rows], [1013, 1020, 1008]
        )

    # -- advisor_contact ----------------------------------------------

    def test_advisor_contact_for_student(self):
        _cols, rows = queries.advisor_contact(self.database, 1001)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][4], "Turing")
        self.assertIn("a.turing@unisystem.ac.uk", rows[0][6])

    def test_advisor_contact_unknown_student_empty(self):
        _cols, rows = queries.advisor_contact(self.database, 4242)
        self.assertEqual(rows, [])

    # -- advisees_of_lecturer -----------------------------------------

    def test_advisees_case_insensitive(self):
        _cols, rows = queries.advisees_of_lecturer(
            self.database, "turing"
        )
        self.assertEqual(
            {row[0] for row in rows}, {1001, 1004, 1008}
        )

    def test_advisees_none_for_lecturer_without_students(self):
        _cols, rows = queries.advisees_of_lecturer(
            self.database, "Drucker"
        )
        self.assertEqual(rows, [])

    # -- publications_in_year -----------------------------------------

    def test_publications_exact_year_only(self):
        _cols, rows = queries.publications_in_year(
            self.database, 2025
        )
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row[4] == 2025 for row in rows))
        self.assertEqual(
            {row[1] for row in rows},
            {"Turing", "Feynman", "Keynes", "Ginsburg"},
        )

    def test_publications_excludes_other_years(self):
        _cols, rows = queries.publications_in_year(
            self.database, 2026
        )
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row[4] == 2026 for row in rows))

    def test_publications_empty_year(self):
        _cols, rows = queries.publications_in_year(
            self.database, 2020
        )
        self.assertEqual(rows, [])

    # -- all_rows -------------------------------------------------------

    def test_all_rows_case_insensitive_exact_match(self):
        _cols, rows = queries.all_rows(self.database, "students")
        self.assertEqual(len(rows), 30)

    def test_all_rows_unambiguous_prefix(self):
        _cols, rows = queries.all_rows(self.database, "Cour")
        self.assertEqual(len(rows), 24)

    def test_all_rows_ambiguous_prefix_raises(self):
        with self.assertRaises(ValueError) as ctx:
            queries.all_rows(self.database, "Enrolment")
        self.assertIn("ambiguous", str(ctx.exception))

    def test_all_rows_unknown_lists_valid_names(self):
        with self.assertRaises(ValueError) as ctx:
            queries.all_rows(self.database, "secrets")
        self.assertIn("Students", str(ctx.exception))

    def test_all_rows_returns_every_whitelisted_column(self):
        # "students" must resolve to the Students table by exact
        # match, even though "Students with advisors (joined)" also
        # starts with the same word.
        source = schema_meta.get_source("Students")
        expected = [alias for alias, _expr in source["columns"]]
        cols, _rows = queries.all_rows(self.database, "students")
        self.assertEqual(cols, expected)

    def test_all_rows_full_name_with_punctuation(self):
        _cols, rows = queries.all_rows(
            self.database, "Enrolments (raw)"
        )
        self.assertEqual(len(rows), 89)

    def test_all_rows_supports_joined_views(self):
        cols, rows = queries.all_rows(
            self.database, "students with advisors (joined)"
        )
        self.assertEqual(len(rows), 30)
        self.assertIn("advisor_last_name", cols)

    def test_all_rows_strips_surrounding_whitespace(self):
        _cols, rows = queries.all_rows(self.database, "  Students  ")
        self.assertEqual(len(rows), 30)

    # -- catalogue ------------------------------------------------------

    def test_catalogue_entries_are_complete(self):
        self.assertGreaterEqual(len(queries.CATALOGUE), 9)
        for entry in queries.CATALOGUE:
            with self.subTest(title=entry["title"]):
                self.assertTrue(entry["title"])
                self.assertTrue(callable(entry["runner"]))
                for prompt, converter in entry["params"]:
                    self.assertTrue(prompt)
                    self.assertTrue(callable(converter))

    def test_all_rows_is_on_the_menu(self):
        runners = [entry["runner"] for entry in queries.CATALOGUE]
        self.assertIn(queries.all_rows, runners)


if __name__ == "__main__":
    unittest.main()
