"""Tests for the db connection layer."""

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import db


class _StubCursor:
    """Records the SQL it is asked to execute."""

    description = (("x",),)

    def __init__(self, log):
        self.log = log

    def execute(self, sql, params):
        self.log.append((sql, params))

    def fetchall(self):
        return []

    def close(self):
        pass


class _StubConnection:
    def __init__(self):
        self.log = []

    def cursor(self):
        return _StubCursor(self.log)


class LoadConfigTests(unittest.TestCase):

    def test_defaults_without_config_file(self):
        config = db.load_config(path=Path("does-not-exist.ini"))
        self.assertEqual(config.get("database", "backend"), "sqlite")
        self.assertEqual(config.get("mysql", "host"), "localhost")
        self.assertEqual(config.getint("mysql", "port"), 3306)

    def test_config_file_read_as_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.ini"
            path.write_text(
                "[database]\nbackend = mysql\n"
                "[mysql]\npassword = pässwörd\n",
                encoding="utf-8",
            )
            config = db.load_config(path=path)
        self.assertEqual(config.get("database", "backend"), "mysql")
        self.assertEqual(
            config.get("mysql", "password"), "pässwörd"
        )


class DatabaseWrapperTests(unittest.TestCase):

    def test_mysql_backend_rewrites_placeholders(self):
        stub = _StubConnection()
        database = db.Database(stub, "mysql")
        database.run("SELECT a FROM t WHERE b = ? AND c = ?", (1, 2))
        sql, params = stub.log[0]
        self.assertEqual(sql, "SELECT a FROM t WHERE b = %s AND c = %s")
        self.assertEqual(params, (1, 2))

    def test_sqlite_backend_keeps_placeholders(self):
        connection = sqlite3.connect(":memory:")
        database = db.Database(connection, "sqlite")
        columns, rows = database.run("SELECT ? AS x", ("value",))
        database.close()
        self.assertEqual(columns, ["x"])
        self.assertEqual(rows, [("value",)])


class ConnectTests(unittest.TestCase):

    def _sqlite_config(self, db_path):
        config = db.load_config(path=Path("does-not-exist.ini"))
        config.set("sqlite", "path", str(db_path))
        return config

    def test_unknown_backend_raises(self):
        config = db.load_config(path=Path("does-not-exist.ini"))
        config.set("database", "backend", "oracle")
        with self.assertRaises(db.DatabaseError):
            db.connect(config)

    def test_sqlite_auto_creates_and_seeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            database = db.connect(self._sqlite_config(db_path))
            _cols, rows = database.run(
                "SELECT COUNT(*) FROM students"
            )
            database.close()
            self.assertTrue(db_path.exists())
            self.assertEqual(rows[0][0], 30)

    def test_sqlite_reconnect_does_not_reseed(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            first = db.connect(self._sqlite_config(db_path))
            first.close()
            second = db.connect(self._sqlite_config(db_path))
            _cols, rows = second.run("SELECT COUNT(*) FROM students")
            second.close()
            self.assertEqual(rows[0][0], 30)

    def test_missing_schema_script_cleans_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            missing = Path(tmp) / "missing.sql"
            with mock.patch.object(
                db, "SQLITE_SCHEMA_PATH", missing
            ):
                with self.assertRaises(db.DatabaseError):
                    db.connect(self._sqlite_config(db_path))
            self.assertFalse(db_path.exists())

    def test_broken_schema_script_cleans_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            broken = Path(tmp) / "broken.sql"
            broken.write_text("CREATE TABLE (", encoding="utf-8")
            with mock.patch.object(
                db, "SQLITE_SCHEMA_PATH", broken
            ):
                with self.assertRaises(db.DatabaseError):
                    db.connect(self._sqlite_config(db_path))
            self.assertFalse(db_path.exists())


if __name__ == "__main__":
    unittest.main()
