"""Database connection layer for the university record system.

Supports two interchangeable back ends, selected in ``config.ini``:

* ``sqlite`` : zero-setup demo mode using the Python
  standard library. The database file is created automatically from
  ``schema_sqlite.sql`` + ``dummy_data.sql`` on first run.
* ``mysql`` : the team's production DBMS, via mysql-connector-python.
  The schema must already exist.

Query code is written once with ``?`` placeholders (DB-API "qmark"
style); this module rewrites them to ``%s`` for the MySQL driver.
"""

import configparser
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = REPO_ROOT / "UniversitySystem" / "database"
SQLITE_SCHEMA_PATH = DATABASE_DIR / "schema_sqlite.sql"
DUMMY_DATA_PATH = DATABASE_DIR / "dummy_data.sql"
DEFAULT_SQLITE_PATH = DATABASE_DIR / "university.db"
CONFIG_PATH = REPO_ROOT / "config.ini"


class DatabaseError(Exception):
    """Raised when a connection cannot be established or configured."""


class Database:
    """Thin wrapper around a DB-API connection.

    Normalises placeholder style across back ends so the query module
    stays back-end agnostic. Note: queries must not contain a literal
    ``?`` outside of a placeholder position.
    """

    def __init__(self, connection, backend):
        self.connection = connection
        self.backend = backend

    def run(self, sql, params=()):
        """Execute *sql* with *params*; return (column_names, rows)."""
        if self.backend == "mysql":
            sql = sql.replace("?", "%s")
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params)
            columns = [item[0] for item in cursor.description]
            rows = cursor.fetchall()
        finally:
            cursor.close()
        return columns, rows

    def close(self):
        """Close the underlying connection."""
        self.connection.close()


def load_config(path=CONFIG_PATH):
    """Read config.ini if present; fall back to SQLite defaults."""
    parser = configparser.ConfigParser()
    parser.read_dict({
        "database": {"backend": "sqlite"},
        "sqlite": {"path": str(DEFAULT_SQLITE_PATH)},
        "mysql": {
            "host": "localhost",
            "port": "3306",
            "user": "root",
            "password": "",
            "database": "unisystem",
        },
    })
    if Path(path).exists():
        # Explicit encoding: Windows would otherwise use the legacy
        # locale code page (e.g. cp1252) and mangle non-ASCII values.
        parser.read(path, encoding="utf-8")
    return parser


def connect(config=None):
    """Create a :class:`Database` for the configured back end."""
    if config is None:
        config = load_config()
    backend = config.get("database", "backend").strip().lower()
    if backend == "sqlite":
        return _connect_sqlite(config)
    if backend == "mysql":
        return _connect_mysql(config)
    raise DatabaseError(
        f"Unknown backend {backend!r} in config.ini "
        "(expected 'sqlite' or 'mysql')."
    )


def _connect_sqlite(config):
    """Open the SQLite database, creating and seeding it if missing."""
    db_path = Path(config.get("sqlite", "path"))
    if not db_path.is_absolute():
        db_path = REPO_ROOT / db_path
    first_run = not db_path.exists()
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    if first_run:
        try:
            _initialise_sqlite(connection)
        except Exception:
            connection.close()
            db_path.unlink(missing_ok=True)
            raise
    return Database(connection, "sqlite")


def _initialise_sqlite(connection):
    """Build schema and load dummy data into a fresh SQLite file."""
    for script in (SQLITE_SCHEMA_PATH, DUMMY_DATA_PATH):
        try:
            sql = script.read_text(encoding="utf-8")
        except OSError as exc:
            raise DatabaseError(
                f"Cannot read {script.name}: {exc}"
            ) from exc
        try:
            connection.executescript(sql)
        except sqlite3.Error as exc:
            raise DatabaseError(
                f"Failed to initialise the demo database from "
                f"{script.name}: {exc}"
            ) from exc
    connection.commit()


def _connect_mysql(config):
    """Connect to the MySQL server described in config.ini."""
    try:
        import mysql.connector
    except ImportError as exc:
        raise DatabaseError(
            "The MySQL back end needs mysql-connector-python. "
            "Install it with: pip install -r requirements.txt"
        ) from exc
    try:
        connection = mysql.connector.connect(
            host=config.get("mysql", "host"),
            port=config.getint("mysql", "port"),
            user=config.get("mysql", "user"),
            password=config.get("mysql", "password"),
            database=config.get("mysql", "database"),
        )
    except mysql.connector.Error as exc:
        raise DatabaseError(f"Could not connect to MySQL: {exc}") from exc
    return Database(connection, "mysql")
