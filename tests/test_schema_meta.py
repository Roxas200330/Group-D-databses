"""Tests for the query-builder whitelist in schema_meta."""

import re
import unittest

import querybuilder
import schema_meta
import support

IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")


class SchemaMetaTests(unittest.TestCase):

    def test_source_names_match_sources(self):
        self.assertEqual(
            schema_meta.SOURCE_NAMES,
            tuple(s["name"] for s in schema_meta.SOURCES),
        )

    def test_get_source_roundtrip(self):
        for name in schema_meta.SOURCE_NAMES:
            with self.subTest(source=name):
                self.assertEqual(
                    schema_meta.get_source(name)["name"], name
                )

    def test_get_source_unknown_raises(self):
        with self.assertRaises(ValueError):
            schema_meta.get_source("Secret table")

    def test_every_source_is_well_formed(self):
        for source in schema_meta.SOURCES:
            with self.subTest(source=source["name"]):
                aliases = [a for a, _e in source["columns"]]
                self.assertTrue(source["from_clause"].strip())
                self.assertTrue(aliases)
                self.assertEqual(len(aliases), len(set(aliases)))
                for alias in aliases:
                    self.assertRegex(alias, IDENTIFIER)


class SchemaMetaIntegrationTests(unittest.TestCase):
    """Every whitelisted source must run against the real schema."""

    @classmethod
    def setUpClass(cls):
        cls.database = support.make_test_database()

    @classmethod
    def tearDownClass(cls):
        cls.database.close()

    def test_all_sources_and_columns_execute(self):
        for source in schema_meta.SOURCES:
            with self.subTest(source=source["name"]):
                aliases = [a for a, _e in source["columns"]]
                sql, params = querybuilder.build_select(
                    source, aliases, limit=1
                )
                columns, _rows = self.database.run(sql, params)
                self.assertEqual(columns, aliases)

    def test_every_source_has_seed_data(self):
        for source in schema_meta.SOURCES:
            with self.subTest(source=source["name"]):
                aliases = [a for a, _e in source["columns"]]
                sql, params = querybuilder.build_select(
                    source, aliases[:1]
                )
                _cols, rows = self.database.run(sql, params)
                self.assertGreater(len(rows), 0)


if __name__ == "__main__":
    unittest.main()
