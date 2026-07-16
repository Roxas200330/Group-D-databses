# University Record Management System

A record management system for a university: a MySQL database designed
in MySQL Workbench, plus Python graphical and command-line interfaces
that execute parameterised SQL queries against it.

## Project structure

```
UniversitySystem/
    uniSystemModel.mwb        MySQL Workbench model (ERD source)
    database/
        schema.sql            MySQL schema (Database Designer)
        schema_sqlite.sql     SQLite translation for the demo back end
        dummy_data.sql        Dummy data (portable MySQL/SQLite SQL)
src/
    main.py                   CLI entry point (menu loop)
    gui.py                    Tkinter GUI (standard queries + builder)
    db.py                     Connection layer (SQLite or MySQL)
    queries.py                Query engine: SQL + one function per query
    querybuilder.py           SELECT generator for the query builder
    schema_meta.py            Whitelisted tables/columns for the builder
    display.py                Text-table result formatting
tests/                        Unit tests (python3 -m unittest -v)
config.ini.example            Configuration template
requirements.txt              Python dependencies
docs/                         Report, meeting minutes
```

## Quick start (no installation needed)

Requires Python 3.9+ (with tkinter, included in standard installers).
From the repository root:

```
python3 src/gui.py     # graphical interface
python3 src/main.py    # command-line interface
```

On first run either interface creates and seeds a local SQLite
database (`UniversitySystem/database/university.db`) from the schema
and dummy data. Delete that file to reset the data.

## Graphical interface

`src/gui.py` opens a window with two tabs above a shared results
table:

- **Standard queries** — the nine predefined reports. Pick a query,
  fill in its parameters and press *Run query*. Parameters with a
  known set of valid values (courses, lecturers, departments,
  semesters, ...) offer an editable dropdown filled live from the
  database — pick from the list or type freely. Related dropdowns
  cascade: picking a course narrows the lecturer list to those who
  teach it, and vice versa (blank means unfiltered).
- **Query builder** — compose your own query: choose a data source
  (a table, or a ready-joined view such as *Enrolment details*),
  select columns, add up to three filters (combined with AND/OR),
  set sorting and an optional row limit. The generated SQL is shown
  in the *Generated SQL* panel for transparency.

The builder is safe by construction: table and column names can only
come from the whitelist in `src/schema_meta.py`, and everything typed
by the user is passed to the database as a bound parameter, never
spliced into the SQL text.

## Running against MySQL

1. Create and populate the database (MySQL 8):

   ```
   mysql -u <user> -p < UniversitySystem/database/schema.sql
   mysql -u <user> -p unisystem < UniversitySystem/database/dummy_data.sql
   ```

2. Install the driver: `pip install -r requirements.txt`
3. `cp config.ini.example config.ini`, set `backend = mysql` and fill
   in your credentials (config.ini is git-ignored).
4. `python3 src/gui.py` (or `src/main.py`)

## Available queries

1. Students in a specific course taught by a particular lecturer
2. Students not registered in a given semester
3. Lecturers with expertise in a research area
4. Courses taught by lecturers in a department
5. Final-year students with an average grade above a threshold
6. Faculty advisor contact details for a student
7. Students advised by a specific lecturer
8. Lecturer publications report for a specific year
9. Show all rows in a chosen table (browse any whitelisted table
   or joined view, e.g. Students, Courses, Enrolments (raw))

All queries use DB-API parameter binding (no string-built SQL), and the
query functions in `src/queries.py` are pure (no I/O), so they can be
unit-tested directly.

Useful demo inputs with the dummy data: course *Databases and
Information Systems* + lecturer *Hopper*; semester *2026-S2*;
department *Computer Science*; student ID *1001*; advisor *Turing*;
threshold *70*; publication year *2025*. In the CLI, enter `?` at any
prompt that announces it to list the valid values; in the GUI the
same parameters appear as dropdowns.

## Running the tests

The test suite uses only the standard library (`unittest`). From the
repository root:

```
python3 -m unittest -v      # macOS / Linux
py -m unittest -v           # Windows
```

It covers the query engine (against an in-memory copy of the real
schema and dummy data), the query-builder SQL generation and its
whitelist/injection defences, the connection layer, result
formatting, the CLI prompt loop (driven with scripted input) and the
GUI (the GUI tests skip themselves automatically on machines without
a display). Every module in src/ has a dedicated test file.

## Windows notes

Everything works on Windows without changes:

- Use `py` (or `python`) wherever this README says `python3`, e.g.
  `py src\gui.py` — forward slashes also work: `py src/gui.py`.
- tkinter and SQLite ship with the standard python.org installer. If
  the GUI reports tkinter missing, re-run the installer and tick the
  "tcl/tk and IDLE" option.
- All file paths in the code use `pathlib`, and all files are read
  with explicit UTF-8 encoding, so path separators and legacy code
  pages (cp1252) are non-issues.

## Code standards

Python code follows PEP-8 (checked with `flake8`, 79-character lines):

```
python3 -m flake8 src/ tests/
```
