-- schema_sqlite.sql
-- SQLite translation of schema.sql.
-- Used by the zero-setup demo back end (config: backend = sqlite).
-- Keep this file in sync with the MySQL schema; the logical design is
-- identical, only dialect details differ (no CREATE DATABASE/USE, no
-- inline INDEX clauses, foreign keys as table constraints).

CREATE TABLE departments (
    DepartmentID INTEGER NOT NULL,
    DepartmentName VARCHAR(45) NOT NULL UNIQUE,
    Faculty VARCHAR(45) NOT NULL,
    PRIMARY KEY (DepartmentID)
);

CREATE TABLE programs (
    name VARCHAR(45) NOT NULL,
    degreeAwarded VARCHAR(45) NOT NULL,
    duration_years INTEGER NOT NULL,
    PRIMARY KEY (name)
);

CREATE TABLE lecturers (
    LecturerID INTEGER NOT NULL,
    lecturersfirstname VARCHAR(45) NOT NULL,
    lecturerslastname VARCHAR(45) NOT NULL,
    departmentID INTEGER NOT NULL,
    contact_info VARCHAR(255) NOT NULL,
    PRIMARY KEY (LecturerID),
    FOREIGN KEY (departmentID) REFERENCES departments (DepartmentID)
);

CREATE TABLE students (
    idstudents INTEGER NOT NULL,
    studentfirstname VARCHAR(45) NOT NULL,
    studentlastname VARCHAR(45) NOT NULL,
    dateofbirth DATE NOT NULL,
    contactinfo VARCHAR(245) NOT NULL,
    program_enrolled VARCHAR(245) NOT NULL,
    year_of_study INTEGER NOT NULL,
    graduation_status VARCHAR(45) NOT NULL,
    advisor_id INTEGER,
    PRIMARY KEY (idstudents),
    FOREIGN KEY (advisor_id) REFERENCES lecturers (LecturerID)
);

CREATE TABLE non_academic_staff (
    staffID INTEGER NOT NULL,
    firstname VARCHAR(45) NOT NULL,
    lastname VARCHAR(45) NOT NULL,
    job_title VARCHAR(45) NOT NULL,
    departmentID INTEGER NOT NULL,
    employment_type VARCHAR(45) NOT NULL,
    contact_details VARCHAR(45) NOT NULL,
    salary_information VARCHAR(45) NOT NULL,
    emergency_contact VARCHAR(245) NOT NULL,
    PRIMARY KEY (staffID),
    FOREIGN KEY (departmentID) REFERENCES departments (DepartmentID)
);

CREATE TABLE course (
    Course_code INTEGER NOT NULL,
    name VARCHAR(45) NOT NULL,
    description VARCHAR(245) NOT NULL,
    departmentID INTEGER NOT NULL,
    level INTEGER,
    credits INTEGER NOT NULL,
    schedule VARCHAR(45) NOT NULL,
    PRIMARY KEY (Course_code),
    FOREIGN KEY (departmentID) REFERENCES departments (DepartmentID)
);

CREATE TABLE researchprojects (
    ProjectTitle VARCHAR(45) NOT NULL,
    principalInvestigator VARCHAR(45) NOT NULL,
    PRIMARY KEY (ProjectTitle)
);

CREATE TABLE student_disciplinary_records (
    recordID INTEGER NOT NULL,
    idstudents INTEGER NOT NULL,
    incident_description VARCHAR(245) NOT NULL,
    PRIMARY KEY (recordID),
    FOREIGN KEY (idstudents) REFERENCES students (idstudents)
);

CREATE TABLE lecturer_qualifications (
    qualificationID INTEGER NOT NULL,
    LecturerID INTEGER NOT NULL,
    degree_name VARCHAR(45) NOT NULL,
    PRIMARY KEY (qualificationID),
    FOREIGN KEY (LecturerID) REFERENCES lecturers (LecturerID)
);

CREATE TABLE lecturer_expertise (
    LecturerID INTEGER NOT NULL,
    area_of_expertise VARCHAR(45) NOT NULL,
    PRIMARY KEY (LecturerID, area_of_expertise),
    FOREIGN KEY (LecturerID) REFERENCES lecturers (LecturerID)
);

CREATE TABLE lecturer_publications (
    publicationID INTEGER NOT NULL,
    LecturerID INTEGER NOT NULL,
    title VARCHAR(245) NOT NULL,
    publication_year INTEGER,
    PRIMARY KEY (publicationID),
    FOREIGN KEY (LecturerID) REFERENCES lecturers (LecturerID)
);

CREATE TABLE project_publications (
    pub_id INTEGER NOT NULL,
    project_title VARCHAR(245) NOT NULL,
    title VARCHAR(245) NOT NULL,
    PRIMARY KEY (pub_id),
    FOREIGN KEY (project_title)
        REFERENCES researchprojects (ProjectTitle)
);

CREATE TABLE course_materials (
    materialID INTEGER NOT NULL,
    course_code INTEGER NOT NULL,
    name VARCHAR(245) NOT NULL,
    PRIMARY KEY (materialID),
    FOREIGN KEY (course_code) REFERENCES course (Course_code)
);

CREATE TABLE department_research_areas (
    DepartmentID INTEGER NOT NULL,
    research_area VARCHAR(45) NOT NULL,
    PRIMARY KEY (DepartmentID, research_area),
    FOREIGN KEY (DepartmentID)
        REFERENCES departments (DepartmentID)
);

CREATE TABLE lecturer_comittees (
    lecturer_id INTEGER NOT NULL,
    comittee_name VARCHAR(45) NOT NULL,
    PRIMARY KEY (lecturer_id, comittee_name),
    FOREIGN KEY (lecturer_id) REFERENCES lecturers (LecturerID)
);

CREATE TABLE enrollments (
    student_id INTEGER NOT NULL,
    course_code INTEGER NOT NULL,
    lecturer_id INTEGER NOT NULL,
    semester VARCHAR(45) NOT NULL,
    grade DECIMAL(5,2),
    PRIMARY KEY (student_id, course_code, semester),
    FOREIGN KEY (student_id) REFERENCES students (idstudents),
    FOREIGN KEY (course_code) REFERENCES course (Course_code),
    FOREIGN KEY (lecturer_id) REFERENCES lecturers (LecturerID)
);

CREATE TABLE project_team_members (
    project_title VARCHAR(245) NOT NULL,
    lecturer_id INTEGER NOT NULL,
    PRIMARY KEY (project_title, lecturer_id),
    FOREIGN KEY (project_title)
        REFERENCES researchprojects (ProjectTitle),
    FOREIGN KEY (lecturer_id) REFERENCES lecturers (LecturerID)
);

CREATE TABLE program_course_requirements (
    program_name VARCHAR(245) NOT NULL,
    course_code INTEGER NOT NULL,
    PRIMARY KEY (program_name, course_code),
    FOREIGN KEY (program_name) REFERENCES programs (name),
    FOREIGN KEY (course_code) REFERENCES course (Course_code)
);

CREATE TABLE course_prerequisites (
    course_code INTEGER NOT NULL,
    prerequisite_course_code INTEGER NOT NULL,
    PRIMARY KEY (course_code, prerequisite_course_code),
    FOREIGN KEY (course_code) REFERENCES course (Course_code),
    FOREIGN KEY (prerequisite_course_code)
        REFERENCES course (Course_code)
);

CREATE TABLE student_organizations_registration (
    student_id INTEGER NOT NULL,
    organization_name VARCHAR(45) NOT NULL,
    PRIMARY KEY (student_id, organization_name),
    FOREIGN KEY (student_id) REFERENCES students (idstudents)
);
