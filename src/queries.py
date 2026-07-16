"""Query engine for the university record system.

Each public function runs one report against the database and returns
``(column_names, rows)``. Functions take a :class:`db.Database` plus
plain-Python parameters, and never touch ``input()``/``print()`` --
this keeps them directly unit-testable for the Tester role.

All SQL uses DB-API placeholders (never string formatting) so user
input can never be interpreted as SQL.

``CATALOGUE`` at the bottom is the menu definition consumed by
``main.py``: title, parameter prompts and the function to call.
"""

import querybuilder
import schema_meta

STUDENTS_IN_COURSE_SQL = """
    SELECT s.idstudents AS student_id,
           s.studentfirstname AS first_name,
           s.studentlastname AS last_name,
           e.semester,
           e.grade
    FROM enrollments AS e
    JOIN students AS s ON s.idstudents = e.student_id
    JOIN course AS c ON c.Course_code = e.course_code
    JOIN lecturers AS l ON l.LecturerID = e.lecturer_id
    WHERE LOWER(c.name) = LOWER(?)
      AND LOWER(l.lecturerslastname) = LOWER(?)
    ORDER BY e.semester, s.studentlastname
"""

UNREGISTERED_STUDENTS_SQL = """
    SELECT s.idstudents AS student_id,
           s.studentfirstname AS first_name,
           s.studentlastname AS last_name,
           s.program_enrolled,
           s.year_of_study,
           s.contactinfo
    FROM students AS s
    WHERE s.graduation_status <> 'Graduated'
      AND NOT EXISTS (
          SELECT 1
          FROM enrollments AS e
          WHERE e.student_id = s.idstudents
            AND e.semester = ?
      )
    ORDER BY s.studentlastname
"""

LECTURERS_BY_EXPERTISE_SQL = """
    SELECT l.LecturerID AS lecturer_id,
           l.lecturersfirstname AS first_name,
           l.lecturerslastname AS last_name,
           d.DepartmentName AS department,
           x.area_of_expertise,
           l.contact_info
    FROM lecturer_expertise AS x
    JOIN lecturers AS l ON l.LecturerID = x.LecturerID
    JOIN departments AS d ON d.DepartmentID = l.departmentID
    WHERE LOWER(x.area_of_expertise) LIKE LOWER(?)
    ORDER BY l.lecturerslastname
"""

COURSES_BY_DEPARTMENT_SQL = """
    SELECT DISTINCT c.Course_code AS course_code,
           c.name AS course_name,
           l.lecturersfirstname AS lecturer_first_name,
           l.lecturerslastname AS lecturer_last_name
    FROM enrollments AS e
    JOIN course AS c ON c.Course_code = e.course_code
    JOIN lecturers AS l ON l.LecturerID = e.lecturer_id
    JOIN departments AS d ON d.DepartmentID = l.departmentID
    WHERE LOWER(d.DepartmentName) = LOWER(?)
    ORDER BY c.Course_code
"""

TOP_FINAL_YEAR_STUDENTS_SQL = """
    SELECT s.idstudents AS student_id,
           s.studentfirstname AS first_name,
           s.studentlastname AS last_name,
           s.program_enrolled,
           s.year_of_study,
           ROUND(AVG(e.grade), 1) AS average_grade
    FROM students AS s
    JOIN programs AS p ON p.name = s.program_enrolled
    JOIN enrollments AS e ON e.student_id = s.idstudents
    WHERE s.year_of_study >= p.duration_years
      AND s.graduation_status <> 'Graduated'
      AND e.grade IS NOT NULL
    GROUP BY s.idstudents, s.studentfirstname, s.studentlastname,
             s.program_enrolled, s.year_of_study
    HAVING AVG(e.grade) > ?
    ORDER BY average_grade DESC
"""

ADVISOR_CONTACT_SQL = """
    SELECT s.idstudents AS student_id,
           s.studentfirstname AS student_first_name,
           s.studentlastname AS student_last_name,
           l.lecturersfirstname AS advisor_first_name,
           l.lecturerslastname AS advisor_last_name,
           d.DepartmentName AS department,
           l.contact_info AS advisor_contact
    FROM students AS s
    JOIN lecturers AS l ON l.LecturerID = s.advisor_id
    JOIN departments AS d ON d.DepartmentID = l.departmentID
    WHERE s.idstudents = ?
"""

ADVISEES_OF_LECTURER_SQL = """
    SELECT s.idstudents AS student_id,
           s.studentfirstname AS first_name,
           s.studentlastname AS last_name,
           s.program_enrolled,
           s.year_of_study,
           s.graduation_status
    FROM students AS s
    JOIN lecturers AS l ON l.LecturerID = s.advisor_id
    WHERE LOWER(l.lecturerslastname) = LOWER(?)
    ORDER BY s.studentlastname
"""

PUBLICATIONS_IN_YEAR_SQL = """
    SELECT l.lecturersfirstname AS first_name,
           l.lecturerslastname AS last_name,
           d.DepartmentName AS department,
           p.title,
           p.publication_year
    FROM lecturer_publications AS p
    JOIN lecturers AS l ON l.LecturerID = p.LecturerID
    JOIN departments AS d ON d.DepartmentID = l.departmentID
    WHERE p.publication_year = ?
    ORDER BY l.lecturerslastname, p.title
"""


def students_in_course(database, course_name, lecturer_surname):
    """Students enrolled in *course_name* taught by *lecturer_surname*.

    Covers the suggested query "Find all students enrolled in a
    specific course taught by a particular lecturer".
    """
    return database.run(
        STUDENTS_IN_COURSE_SQL, (course_name, lecturer_surname)
    )


def unregistered_students(database, semester):
    """Non-graduated students with no enrolment in *semester*.

    Covers "Identify students who haven't registered for any courses
    in the current semester".
    """
    return database.run(UNREGISTERED_STUDENTS_SQL, (semester,))


def lecturers_by_expertise(database, area):
    """Lecturers whose expertise matches *area* (substring match).

    Covers "Search for lecturers with expertise in a particular
    research area".
    """
    return database.run(LECTURERS_BY_EXPERTISE_SQL, (f"%{area}%",))


def courses_by_department(database, department):
    """Courses taught by lecturers belonging to *department*.

    Covers "List all courses taught by lecturers in a specific
    department". Teaching is recorded on enrolments, hence DISTINCT.
    """
    return database.run(COURSES_BY_DEPARTMENT_SQL, (department,))


def top_final_year_students(database, threshold=70):
    """Final-year students whose average grade exceeds *threshold*.

    Covers "List all students with an average grade above 70% who are
    in their final year of studies". Final year means year_of_study
    has reached the programme's duration_years; graduated students and
    ungraded (in-progress) enrolments are excluded.
    """
    return database.run(TOP_FINAL_YEAR_STUDENTS_SQL, (threshold,))


def advisor_contact(database, student_id):
    """Contact details of the faculty advisor for *student_id*.

    Covers "Retrieve the contact information for the faculty advisor
    of a specific student".
    """
    return database.run(ADVISOR_CONTACT_SQL, (student_id,))


def advisees_of_lecturer(database, lecturer_surname):
    """Students advised by the lecturer named *lecturer_surname*.

    Covers "Retrieve the names of students advised by a specific
    lecturer".
    """
    return database.run(ADVISEES_OF_LECTURER_SQL, (lecturer_surname,))


def publications_in_year(database, year):
    """Lecturer publications published in exactly *year*.

    Covers "Generate a report on the publications of lecturers in the
    past year": pass the year of interest and only publications from
    that specific year are returned.
    """
    return database.run(PUBLICATIONS_IN_YEAR_SQL, (year,))


def _match_source(name):
    """Resolve a user-typed name to a whitelisted data source name.

    Matching is case-insensitive; an unambiguous prefix is accepted
    (e.g. "cour" -> "Courses"). Raises ValueError with the list of
    valid names when nothing (or more than one source) matches.
    """
    wanted = name.strip().lower()
    names = schema_meta.SOURCE_NAMES
    for candidate in names:
        if candidate.lower() == wanted:
            return candidate
    partial = [c for c in names if c.lower().startswith(wanted)]
    if len(partial) == 1:
        return partial[0]
    if partial:
        raise ValueError(
            f"'{name}' is ambiguous; matches: {', '.join(partial)}"
        )
    raise ValueError(
        f"Unknown table '{name}'. Choose from: {', '.join(names)}"
    )


def all_rows(database, source_name):
    """Every row and column of one table (or pre-joined view).

    Lets users browse the raw contents of the database. The name is
    validated against the schema_meta whitelist, so arbitrary SQL can
    never be injected through this parameter.
    """
    source = schema_meta.get_source(_match_source(source_name))
    aliases = [alias for alias, _expr in source["columns"]]
    sql, params = querybuilder.build_select(source, aliases)
    return database.run(sql, params)


def _option_query(sql):
    """Return an option provider that lists a column's values.

    Providers feed the optional parameter dropdowns in the GUI (and
    the ``?`` listing in the CLI). They run against the live database
    so the choices always reflect the current data. *context* maps
    the query's other parameter prompts to their current raw text;
    providers built here list independent values and ignore it.
    """
    def provider(database, _context=None):
        _columns, rows = database.run(sql)
        return [str(row[0]) for row in rows if row[0] is not None]
    return provider


course_names = _option_query(
    "SELECT DISTINCT name FROM course ORDER BY name"
)
lecturer_surnames = _option_query(
    "SELECT DISTINCT lecturerslastname FROM lecturers "
    "ORDER BY lecturerslastname"
)
semesters = _option_query(
    "SELECT DISTINCT semester FROM enrollments ORDER BY semester"
)
expertise_areas = _option_query(
    "SELECT DISTINCT area_of_expertise FROM lecturer_expertise "
    "ORDER BY area_of_expertise"
)
department_names = _option_query(
    "SELECT DepartmentName FROM departments ORDER BY DepartmentName"
)
student_ids = _option_query(
    "SELECT idstudents FROM students ORDER BY idstudents"
)
publication_years = _option_query(
    "SELECT DISTINCT publication_year FROM lecturer_publications "
    "ORDER BY publication_year DESC"
)


def table_names(_database, _context=None):
    """Whitelisted table/view names for the browse query."""
    return list(schema_meta.SOURCE_NAMES)


LECTURERS_FOR_COURSE_SQL = """
    SELECT DISTINCT l.lecturerslastname
    FROM enrollments AS e
    JOIN lecturers AS l ON l.LecturerID = e.lecturer_id
    JOIN course AS c ON c.Course_code = e.course_code
    WHERE LOWER(c.name) = LOWER(?)
    ORDER BY l.lecturerslastname
"""

COURSES_FOR_LECTURER_SQL = """
    SELECT DISTINCT c.name
    FROM enrollments AS e
    JOIN course AS c ON c.Course_code = e.course_code
    JOIN lecturers AS l ON l.LecturerID = e.lecturer_id
    WHERE LOWER(l.lecturerslastname) = LOWER(?)
    ORDER BY c.name
"""


def lecturer_surnames_for_course(database, context=None):
    """Lecturer surnames, narrowed to the chosen course (if any).

    Cascading provider for the course-roster query: once a course is
    selected, only lecturers who actually teach it are offered. With
    no course chosen yet, every surname is offered.
    """
    course = (context or {}).get("Course name", "").strip()
    if not course:
        return lecturer_surnames(database)
    _columns, rows = database.run(
        LECTURERS_FOR_COURSE_SQL, (course,)
    )
    return [row[0] for row in rows]


def course_names_for_lecturer(database, context=None):
    """Course names, narrowed to the chosen lecturer (if any).

    Mirror of :func:`lecturer_surnames_for_course` so the filtering
    works in both directions.
    """
    surname = (context or {}).get("Lecturer surname", "").strip()
    if not surname:
        return course_names(database)
    _columns, rows = database.run(
        COURSES_FOR_LECTURER_SQL, (surname,)
    )
    return [row[0] for row in rows]


# Menu definition used by main.py and gui.py. Each parameter is a
# tuple of (prompt, converter applied to the raw input, optional
# option provider used for dropdowns / the CLI "?" listing).
CATALOGUE = (
    {
        "title": ("Students in a specific course taught by a "
                  "particular lecturer"),
        "params": (
            ("Course name", str, course_names_for_lecturer),
            ("Lecturer surname", str, lecturer_surnames_for_course),
        ),
        "runner": students_in_course,
    },
    {
        "title": "Students not registered in a given semester",
        "params": (
            ("Semester", str, semesters),
        ),
        "runner": unregistered_students,
    },
    {
        "title": "Lecturers with expertise in a research area",
        "params": (
            ("Research area", str, expertise_areas),
        ),
        "runner": lecturers_by_expertise,
    },
    {
        "title": "Courses taught by lecturers in a department",
        "params": (
            ("Department", str, department_names),
        ),
        "runner": courses_by_department,
    },
    {
        "title": ("Final-year students with an average grade above a "
                  "threshold"),
        "params": (
            ("Grade threshold in percent (e.g. 70)", float, None),
        ),
        "runner": top_final_year_students,
    },
    {
        "title": "Faculty advisor contact details for a student",
        "params": (
            ("Student ID", int, student_ids),
        ),
        "runner": advisor_contact,
    },
    {
        "title": "Students advised by a specific lecturer",
        "params": (
            ("Lecturer surname", str, lecturer_surnames),
        ),
        "runner": advisees_of_lecturer,
    },
    {
        "title": "Lecturer publications report for a specific year",
        "params": (
            ("Publication year", int, publication_years),
        ),
        "runner": publications_in_year,
    },
    {
        "title": "Show all rows in a chosen table",
        "params": (
            ("Table or view name", str, table_names),
        ),
        "runner": all_rows,
    },
)
