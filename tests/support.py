"""Shared helpers for the test suite."""

import sqlite3

import db


def make_test_database():
    """Return an in-memory SQLite database seeded with dummy data.

    Uses the same schema and data scripts as the application, so
    tests exercise the real schema without touching files on disk.
    """
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    for script in (db.SQLITE_SCHEMA_PATH, db.DUMMY_DATA_PATH):
        connection.executescript(script.read_text(encoding="utf-8"))
    return db.Database(connection, "sqlite")
