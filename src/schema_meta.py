"""Whitelisted data sources for the custom query builder.

This module to be kept in sync with schema.sql / schema_sqlite.sql.
"""

SOURCES = (
    {
        "name": "Students",
        "from_clause": "students",
        "columns": (
            ("student_id", "idstudents"),
            ("first_name", "studentfirstname"),
            ("last_name", "studentlastname"),
            ("date_of_birth", "dateofbirth"),
            ("contact_info", "contactinfo"),
            ("program", "program_enrolled"),
            ("year_of_study", "year_of_study"),
            ("graduation_status", "graduation_status"),
            ("advisor_id", "advisor_id"),
        ),
    },
    {
        "name": "Lecturers",
        "from_clause": "lecturers",
        "columns": (
            ("lecturer_id", "LecturerID"),
            ("first_name", "lecturersfirstname"),
            ("last_name", "lecturerslastname"),
            ("department", "department"),
            ("contact_info", "contactinfo"),
        ),
    },
    {
        "name": "Courses",
        "from_clause": "course",
        "columns": (
            ("course_code", "Course_code"),
            ("name", "name"),
            ("description", "description"),
            ("level", "department_level"),
            ("credits", "credits"),
            ("schedule", "schedule"),
        ),
    },
    {
        "name": "Departments",
        "from_clause": "departments",
        "columns": (
            ("department_name", "DepartmentName"),
            ("faculty", "Faculty"),
        ),
    },
    {
        "name": "Programs",
        "from_clause": "programs",
        "columns": (
            ("name", "name"),
            ("degree_awarded", "degreeAwarded"),
            ("duration_years", "duration_years"),
        ),
    },
    {
        "name": "Non-academic staff",
        "from_clause": "non_academic_staff",
        "columns": (
            ("staff_id", "staffID"),
            ("first_name", "firstname"),
            ("last_name", "lastname"),
            ("job_title", "job_title"),
            ("department", "department"),
            ("employment_type", "employment_type"),
            ("contact_details", "contact_details"),
            ("salary_information", "salary_information"),
        ),
    },
    {
        "name": "Research projects",
        "from_clause": "researchprojects",
        "columns": (
            ("project_title", "ProjectTitle"),
            ("principal_investigator", "principalInvestigator"),
        ),
    },
    {
        "name": "Enrolments (raw)",
        "from_clause": "enrollments",
        "columns": (
            ("student_id", "student_id"),
            ("course_code", "course_code"),
            ("lecturer_id", "lecturer_id"),
            ("semester", "semester"),
            ("grade", "grade"),
        ),
    },
    {
        "name": "Enrolment details (joined)",
        "from_clause": (
            "enrollments AS e\n"
            "    JOIN students AS s ON s.idstudents = e.student_id\n"
            "    JOIN course AS c ON c.Course_code = e.course_code\n"
            "    JOIN lecturers AS l ON l.LecturerID = e.lecturer_id"
        ),
        "columns": (
            ("student_id", "s.idstudents"),
            ("student_first_name", "s.studentfirstname"),
            ("student_last_name", "s.studentlastname"),
            ("program", "s.program_enrolled"),
            ("course_code", "c.Course_code"),
            ("course_name", "c.name"),
            ("lecturer_last_name", "l.lecturerslastname"),
            ("semester", "e.semester"),
            ("grade", "e.grade"),
        ),
    },
    {
        "name": "Students with advisors (joined)",
        "from_clause": (
            "students AS s\n"
            "    JOIN lecturers AS l ON l.LecturerID = s.advisor_id"
        ),
        "columns": (
            ("student_id", "s.idstudents"),
            ("student_first_name", "s.studentfirstname"),
            ("student_last_name", "s.studentlastname"),
            ("program", "s.program_enrolled"),
            ("year_of_study", "s.year_of_study"),
            ("advisor_first_name", "l.lecturersfirstname"),
            ("advisor_last_name", "l.lecturerslastname"),
            ("advisor_department", "l.department"),
            ("advisor_contact", "l.contactinfo"),
        ),
    },
    {
        "name": "Publications with lecturers (joined)",
        "from_clause": (
            "lecturer_publications AS p\n"
            "    JOIN lecturers AS l ON l.LecturerID = p.LecturerID"
        ),
        "columns": (
            ("lecturer_first_name", "l.lecturersfirstname"),
            ("lecturer_last_name", "l.lecturerslastname"),
            ("department", "l.department"),
            ("title", "p.title"),
            ("publication_year", "p.publication_year"),
        ),
    },
)

SOURCE_NAMES = tuple(source["name"] for source in SOURCES)


def get_source(name):
    """Return the source dict whose display name is *name*."""
    for source in SOURCES:
        if source["name"] == name:
            return source
    raise ValueError(f"Unknown data source: {name}")
