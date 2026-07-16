# Design Notes — Supporting Evidence for the Report

## 1. System overview (citable facts)

- Normalized MySQL schema, 21 tables, designed in MySQL Workbench.
- ~400 rows of seed data engineered to exercise every query.
- Two interfaces sharing one query engine: a Tkinter GUI (standard
  queries + a visual query builder) and a CLI.
- 9 parameterised queries (brief requires at least 5), all executed
  from Python via DB-API parameter binding.
- Dual back end: SQLite (zero-setup demo/testing) and MySQL
  (production target) behind one connection layer.
- 110 unit tests (stdlib `unittest`), run in ~0.5 s; flake8/PEP-8
  clean with default settings; no third-party dependency needed to
  run the demo.

## 2. Design decisions and justification

**Layered architecture.** Interfaces (`main.py`, `gui.py`) contain no
SQL; the query engine (`queries.py`) contains no I/O; the connection
layer (`db.py`) is the only code that knows which DBMS is in use.
This mirrors the ANSI-SPARC separation of external, conceptual and
physical levels. Evidence it worked: the GUI was added, and later the
cascading dropdowns, without changing the query engine; when the
schema was normalized mid-project, only the engine and DDL changed —
neither interface was touched.

**Dual back end via DB-API 2.0.** All SQL is written once with `?`
placeholders; a single method rewrites them to `%s` for
mysql-connector. Justification: markers and teammates can run the
system with zero installation (SQLite ships with Python), while the
committed schema remains the designer's MySQL. The dialect edges
(DDL, placeholder style) are quarantined in two schema files and one
rewrite line; all query SQL stays in the portable subset both engines
share.

**Two-layer SQL injection defence.** Values are always bound
parameters, never string-formatted. Identifiers (tables/columns for
the query builder and table browser) can only come from a hardcoded
whitelist (`schema_meta.py`), because placeholders cannot substitute
identifiers. Tests attempt injection through both routes: a value of
`x' OR '1'='1` returns zero rows; a column name of
`nope; DROP TABLE students` is rejected before any SQL is built.

**Catalogue-driven interfaces.** Every query is declared once
(title, parameter prompts, converters, option providers, function).
Both interfaces render whatever the catalogue declares, so a new
query is one declaration and appears in both, and the two front ends
cannot drift apart.

**Normalized schema (collaboration story).** The Database Designer's
normalization replaced an impossible foreign key (INT `departmentID`
columns referencing a VARCHAR primary key — the types could never
join) with a surrogate `DepartmentID` key referenced by lecturers,
staff and courses. The Software Engineer's amendments were folded
directly into `schema.sql`: numeric `duration_years` (the final-year
report computes `year_of_study >= duration_years`, which handles
3-year BScs and 5-year MBBS with the same logic), a restored course
`level` (a brief attribute lost during normalization), and a UNIQUE
constraint on department names. A consolidated CREATE script was
chosen over a separate ALTER (migration) script because no deployed
database exists to migrate — worth stating as a deliberate decision.

**Numeric, nullable grades.** Originally `VARCHAR NOT NULL`, which
made `AVG()` impossible and could not represent an in-progress
course. `DECIMAL(5,2) NULL` fixes both: SQL's `AVG()` ignores NULLs,
so current-semester enrolments do not distort averages.

**Seed data designed for falsifiability.** Every query has rows that
match and rows that must not: a student averaging exactly 70.0
(excluded by the strict `> 70`), one at 69.0, a graduated student, a
deferred student, a failing grade, programme durations 1–5 years.
Demonstrating an absent row proves more than showing present ones.

**Testing strategy.** Every `src/` module has a dedicated test file.
Queries run against an in-memory SQLite copy of the real schema and
seed data; the GUI tests drive real Tk widgets headlessly (and skip
automatically without a display); the CLI is tested with scripted
`input()`; data-integrity tests assert invariants such as "every
course has a lecturer". The suite is fast enough to run after every
change, which is what made the mid-project schema swap safe — it
caught a missed query dependency within seconds.

## 3. Development narrative (MVP first)

1. **Review and plan.** Designer produced the Workbench schema; the
   engineer's review identified fixes needed for the required
   queries (advisor link, numeric grades, FK type mismatch) —
   evidence of role-based collaboration through source control.
2. **MVP.** A CLI with the four queries the original schema could
   already answer, over a self-seeding SQLite database — a walking
   skeleton proving the full stack end-to-end while schema fixes
   were still pending. SQLite was chosen deliberately as the
   iteration vehicle: no server, resettable by deleting one file.
3. **Full query set + dual back end** once the fixes were agreed;
   MySQL support added behind the same interface.
4. **GUI.** Tkinter window exceeding the "simple interface" brief:
   standard queries plus a query builder that shows its generated
   SQL. The engine was reused unchanged — the payoff of layering.
5. **Hardening.** Windows portability (pathlib, explicit UTF-8),
   3× seed data with edge cases, comprehensive test suite.
6. **Integration.** The designer's normalization was merged from
   `main` and the application layer adapted the same day, with the
   test suite as the safety net.
7. **UX iteration.** Live dropdowns for every enumerable parameter,
   then cascading filters (choosing a course narrows lecturers to
   those who teach it — the dropdown is literally the same join the
   query runs, i.e. the relational design surfaced as UX).

The theme to draw out: each increment was shippable and verified;
the cheap-to-run local stack (SQLite + tests) enabled fast iteration
toward the production target (MySQL) without rework.

## 4. Extension path: from MVP to production

**Stage 1 — shared departmental server (small step).** Point
`config.ini` at a shared MySQL instance. Add a least-privilege
database account (SELECT-only — the app never writes), and a
`course_lecturers` assignment table so teaching no longer depends on
enrolments existing (current known limitation).

**Stage 2 — multi-user web application.** Replace Tkinter with a web
front end (e.g. Flask/FastAPI + HTML). Because `queries.py` is pure
functions returning rows, it becomes the service layer of a REST API
almost unchanged; the catalogue becomes the API's endpoint
definitions. Add authentication and role-based access (student /
lecturer / registrar) — disciplinary records and contact details are
personal data, so GDPR-style access control becomes mandatory, not
optional.

**Stage 3 — cloud deployment.** Managed MySQL (e.g. AWS RDS),
containerised app (Docker), CI pipeline running the existing
`unittest` suite and flake8 on every push, automated backups and
monitoring. The API is stateless, so it scales horizontally.

**Stage 4 — enhanced functionality.** Write operations (enrolment as
a transaction, grade entry with validation), dashboards/reporting,
full-text search over courses and publications. At that scale an ORM
(SQLAlchemy) and a migration tool (Alembic) replace hand-written SQL
and consolidated DDL — the point where the migration-script
trade-off (section 2) reverses.

What survives every stage unchanged: the schema, the query logic and
the test suite. What gets replaced: the presentation layer. That
asymmetry is the strongest single argument for the layered design.

## 5. Known limitations

- Teaching is derived from enrolments; a course with no students has
  no lecturer (mitigated in seed data; proper fix is
  `course_lecturers`).
- The MySQL path is verified by construction and driver-level tests;
  live-server validation is the Database Designer's Workbench run.
- Single-user by design: no authentication, SQLite allows one
  writer, credentials sit in a git-ignored plaintext `config.ini`.
- Read-only application (no INSERT/UPDATE from the UI) — a scope
  decision matching the brief, not an oversight.

## 6. Evidence checklist for report and video

- ERD exported from the `.mwb` (confirm `duration_years`, `level`
  and the unique department name are mirrored in the model).
- Screenshots: both GUI tabs; the Generated SQL panel; a cascading
  dropdown before/after choosing a course; CLI `?` listing.
- Terminal capture: `python3 -m unittest -v` (110 passing) and a
  silent `flake8 src/ tests/` run.
- Video demo flow: quick start (one command) → two standard queries
  incl. one no-result and one boundary case (threshold 70 vs the
  student on exactly 70.0) → query builder with SQL panel →
  cascade demo → tests running.

## 7. Critical analysis: alternatives considered, costs accepted

Each decision below names the alternative we rejected, why, the cost
we knowingly accepted, and where the evidence sits in the repo.

**Tkinter vs a web front end (or PyQt).** A web app is the obvious
production shape, and PyQt looks more modern. We chose Tkinter
because it ships inside Python: the marker runs one command with no
server, browser stack, or licence questions. Cost accepted: a dated
look and a hard ceiling at single-user. Mitigation: the layering
means the front end is the *replaceable* part (section 4). Evidence:
the zero-install quick start in the README.

**Raw SQL vs an ORM (SQLAlchemy / Django ORM).** An ORM would give
us dialect portability and migrations for free. We rejected it
because this module assesses database competence — the SQL *is* the
deliverable — and because the GUI's "Generated SQL" panel makes the
queries inspectable, which an ORM would hide. Cost accepted: manual
dialect management. That cost proved small and containable: one
placeholder-rewrite line plus two DDL files. The honest caveat: at
production scale with write operations, this trade-off reverses.

**Static whitelist vs runtime introspection.** The query builder
could discover tables via `PRAGMA table_info` / `information_schema`
instead of the hand-written `schema_meta.py`. Introspection never
goes stale, but it is dialect-specific twice over, and it would
expose every column with no curation (or aliasing) at all. The
static whitelist is dialect-free, curated, and doubles as the
injection defence for identifiers. Cost accepted: manual sync with
the schema — again covered by the same integration test rather than
by discipline alone.

**Natural vs surrogate keys — deliberately inconsistent.**
Departments moved to a surrogate `DepartmentID` during
normalization; `programs` still uses its name as the primary key. A
fair self-critique: renaming a programme would cascade through
`students.program_enrolled`, so at production scale programmes
should get a surrogate key too. We left it as-is consciously —
schema stability days before delivery outweighed uniformity — and
that reasoning belongs in the report more than the inconsistency
hurts it.

**Teaching modelled through enrolments.** The schema has no
course–lecturer assignment table, so "who teaches X" is derived from
who is enrolled. We hit the consequence directly: a course with no
students ("Business Strategy") had no lecturer anywhere in the
system — an *existence dependency* created by deriving a
relationship instead of storing it. Short-term we fixed the data and
added an invariant test ("every course has a lecturer"); the correct
long-term fix is a `course_lecturers` table. This is the strongest
single piece of critical-analysis material in the project: a
modelling flaw, discovered through use, diagnosed, mitigated, with
the proper remedy identified and scoped.


**stdlib `unittest` vs pytest.** Pytest is terser and more popular;
we stayed with `unittest` to preserve the zero-dependency guarantee:
the entire system — app, both interfaces, and test suite — runs on a
bare Python install. One principle applied uniformly is easier to
defend than a per-tool judgement call.

## 8. Extensibility: what next, in priority order

1. **`course_lecturers` assignment table** — removes the known
   modelling flaw; small schema change plus one JOIN change in two
   queries and the cascade providers.
2. **Live MySQL validation + CI** — run the designer's Workbench
   pass on `schema.sql`; add a GitHub Actions workflow running
   `python -m unittest` and `flake8` on every push. The suite is
   fast (~0.5 s) precisely so CI is trivial.
3. **Naming cleanup** — `contact_info` (lecturers) vs `contactinfo`
   (students) survived the merge; unify while the codebase is small.
4. **Write operations** — enrolment as a transaction (seat checks,
   prerequisite validation), grade entry with range constraints;
   introduces the first need for COMMIT/ROLLBACK handling in `db.py`.
5. **Authentication and roles** — prerequisite for any multi-user
   deployment given the personal data held (contact details,
   disciplinary records).
6. **Then the production ladder in section 4** — web front end over
   the unchanged engine, managed cloud database, ORM + migrations at
   the point write-heavy complexity justifies them.

## 9. Retrospective: what we would do differently

- **Share schema changes as reviewed migrations from day one.** The
  fix list and the designer's normalization solved the same flaw two
  different ways in parallel (name-keyed vs surrogate-keyed
  departments). A single reviewed change would have prevented the
  one integration incident of the project.
- **Agree naming conventions before writing DDL** — the
  `contact_info`/`contactinfo` split is harmless but visible, and a
  five-minute convention would have prevented it.
- **Stand up CI at the first commit, not after delivery.** Every
  quality gate used locally (tests, flake8) was CI-ready the whole
  time; automating it earlier would have protected the shared
  branches, not just the local checkout.
- **What we would keep unchanged:** the walking-skeleton MVP, the
  zero-dependency rule, and testing against real schema and data
  from the first week — all three repeatedly converted risky changes
  (schema swap, 3× data growth) into same-day, verified work.
