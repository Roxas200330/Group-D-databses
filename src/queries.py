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
           l.department,
           x.area_of_expertise,
           l.contactinfo
    FROM lecturer_expertise AS x
    JOIN lecturers AS l ON l.LecturerID = x.LecturerID
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
    WHERE LOWER(l.department) = LOWER(?)
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
           l.department,
           l.contactinfo AS advisor_contact
    FROM students AS s
    JOIN lecturers AS l ON l.LecturerID = s.advisor_id
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
           l.department,
           p.title,
           p.publication_year
    FROM lecturer_publications AS p
    JOIN lecturers AS l ON l.LecturerID = p.LecturerID
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


# Menu definition used by main.py. Each parameter is a tuple of
# (prompt shown to the user, converter applied to the raw input).
CATALOGUE = (
    {
        "title": ("Students in a specific course taught by a "
                  "particular lecturer"),
        "params": (
            ("Course name (e.g. Databases and Information Systems)",
             str),
            ("Lecturer surname (e.g. Hopper)", str),
        ),
        "runner": students_in_course,
    },
    {
        "title": "Students not registered in a given semester",
        "params": (
            ("Semester (e.g. 2026-S2)", str),
        ),
        "runner": unregistered_students,
    },
    {
        "title": "Lecturers with expertise in a research area",
        "params": (
            ("Research area (e.g. Machine Learning)", str),
        ),
        "runner": lecturers_by_expertise,
    },
    {
        "title": "Courses taught by lecturers in a department",
        "params": (
            ("Department (e.g. Computer Science)", str),
        ),
        "runner": courses_by_department,
    },
    {
        "title": ("Final-year students with an average grade above a "
                  "threshold"),
        "params": (
            ("Grade threshold in percent (e.g. 70)", float),
        ),
        "runner": top_final_year_students,
    },
    {
        "title": "Faculty advisor contact details for a student",
        "params": (
            ("Student ID (e.g. 1001)", int),
        ),
        "runner": advisor_contact,
    },
    {
        "title": "Students advised by a specific lecturer",
        "params": (
            ("Lecturer surname (e.g. Turing)", str),
        ),
        "runner": advisees_of_lecturer,
    },
    {
        "title": "Lecturer publications report for a specific year",
        "params": (
            ("Publication year (e.g. 2026)", int),
        ),
        "runner": publications_in_year,
    },
)
