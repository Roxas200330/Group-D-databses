CREATE DATABASE IF NOT EXISTS unisystem;
USE unisystem;


CREATE TABLE `unisystem`.`departments` (
  `DepartmentID` INT NOT NULL AUTO_INCREMENT,
  `DepartmentName` VARCHAR(45) NOT NULL,
  `Faculty` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`DepartmentID`),
  UNIQUE INDEX `DepartmentName_UNIQUE` (`DepartmentName` ASC) VISIBLE);


CREATE TABLE `unisystem`.`lecturers` (
  `LecturerID` INT NOT NULL,
  `lecturersfirstname` VARCHAR(45) NOT NULL,
  `lecturerslastname` VARCHAR(45) NOT NULL,
  `departmentID` INT NOT NULL,
  `contact_info` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`LecturerID`),
  INDEX `departmentID_idx` (`departmentID` ASC) VISIBLE,
  CONSTRAINT `FK_lecturers_departments`
    FOREIGN KEY (`departmentID`)
    REFERENCES `unisystem`.`departments` (`DepartmentID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);


CREATE TABLE `unisystem`.`students` (
  `idstudents` INT NOT NULL,
  `studentfirstname` VARCHAR(45) NOT NULL,
  `studentlastname` VARCHAR(45) NOT NULL,
  `dateofbirth` DATE NOT NULL,
  `contactinfo` VARCHAR(245) NOT NULL,
  `program_enrolled` VARCHAR(245) NOT NULL,
  `year_of_study` INT NOT NULL,
  `graduation_status` VARCHAR(45) NOT NULL,
  `advisor_id` INT NULL,
  PRIMARY KEY (`idstudents`),
  INDEX `advisor_id_idx` (`advisor_id` ASC) VISIBLE,
  CONSTRAINT `FK_students_advisors`
    FOREIGN KEY (`advisor_id`)
    REFERENCES `unisystem`.`lecturers` (`LecturerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
);


  CREATE TABLE `unisystem`.`non_academic_staff` (
  `staffID` INT NOT NULL,
  `firstname` VARCHAR(45) NOT NULL,
  `lastname` VARCHAR(45) NOT NULL,
  `job_title` VARCHAR(45) NOT NULL,
  `departmentID` INT NOT NULL,
  `employment_type` VARCHAR(45) NOT NULL,
  `contact_details` VARCHAR(45) NOT NULL,
  `salary_information` VARCHAR(45) NOT NULL,
  `emergency_contact` VARCHAR(245) NOT NULL,
  PRIMARY KEY (`staffID`),
  INDEX `departmentID_idx` (`departmentID` ASC) VISIBLE,
  CONSTRAINT `FK_non_academic_staff_departments`
    FOREIGN KEY (`departmentID`)
    REFERENCES `unisystem`.`departments` (`DepartmentID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
  );


  CREATE TABLE `unisystem`.`course` (
  `Course_code` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(245) NOT NULL,
  `departmentID` INT NOT NULL,
  `level` INT NULL,
  `credits` INT NOT NULL,
  `schedule` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Course_code`),
  INDEX `departmentID_idx` (`departmentID` ASC) VISIBLE,
  CONSTRAINT `FK_course_departments`
    FOREIGN KEY (`departmentID`)
    REFERENCES `unisystem`.`departments` (`DepartmentID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
  );


CREATE TABLE `unisystem`.`programs` (
  `name` VARCHAR(45) NOT NULL,
  `degreeAwarded` VARCHAR(45) NOT NULL,
  `duration_years` INT NOT NULL,
  PRIMARY KEY (`name`));


CREATE TABLE `unisystem`.`researchprojects` (
  `ProjectTitle` VARCHAR(45) NOT NULL,
  `principalInvestigator` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`ProjectTitle`));


CREATE TABLE `unisystem`.`student_disciplinary_records` (
  `recordID` INT NOT NULL,
  `idstudents` INT NOT NULL,
  `incident_description` VARCHAR(245) NOT NULL,
  PRIMARY KEY (`recordID`),
  INDEX `idstudents_idx` (`idstudents` ASC) VISIBLE,
  CONSTRAINT `FK_disciplinary_records`
    FOREIGN KEY (`idstudents`)
    REFERENCES `unisystem`.`students` (`idstudents`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);



CREATE TABLE `unisystem`.`lecturer_qualifications` (
  `qualificationID` INT NOT NULL,
  `LecturerID` INT NOT NULL,
  `degree_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`qualificationID`),
  INDEX `LecturerID_idx` (`LecturerID` ASC) VISIBLE,
  CONSTRAINT `FK_lecturer_qualifications_lecturers`
    FOREIGN KEY (`LecturerID`)
    REFERENCES `unisystem`.`lecturers` (`LecturerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


CREATE TABLE `unisystem`.`lecturer_expertise` (
  `LecturerID` INT NOT NULL,
  `area_of_expertise` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`LecturerID`, `area_of_expertise`),
  CONSTRAINT `FK_lecturer_expertise_lecturers`
    FOREIGN KEY (`LecturerID`)
    REFERENCES `unisystem`.`lecturers` (`LecturerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


CREATE TABLE `unisystem`.`lecturer_publications` (
  `publicationID` INT NOT NULL,
  `LecturerID` INT NOT NULL,
  `title` VARCHAR(245) NOT NULL,
  `publication_year` YEAR NULL,
  PRIMARY KEY (`publicationID`),
  INDEX `FK_lecturer_publications_lecturers_idx` (`LecturerID` ASC) VISIBLE,
  CONSTRAINT `FK_lecturer_publications_lecturers`
    FOREIGN KEY (`LecturerID`)
    REFERENCES `unisystem`.`lecturers` (`LecturerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


CREATE TABLE `unisystem`.`project_publications` (
  `pub_id` INT NOT NULL,
  `project_title` VARCHAR(245) NOT NULL,
  `title` VARCHAR(245) NOT NULL,
  PRIMARY KEY (`pub_id`),
  INDEX `project_title_idx` (`project_title` ASC) VISIBLE,
  CONSTRAINT `project_title`
    FOREIGN KEY (`project_title`)
    REFERENCES `unisystem`.`researchprojects` (`ProjectTitle`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


CREATE TABLE `unisystem`.`course_materials` (
  `materialID` INT NOT NULL,
  `course_code` INT NOT NULL,
  `name` VARCHAR(245) NOT NULL,
  PRIMARY KEY (`materialID`),
  INDEX `course_code_idx` (`course_code` ASC) VISIBLE,
  CONSTRAINT `course_code`
    FOREIGN KEY (`course_code`)
    REFERENCES `unisystem`.`course` (`Course_code`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


CREATE TABLE `unisystem`.`department_research_areas` (
  `DepartmentID` INT NOT NULL,
  `research_area` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`DepartmentID`, `research_area`),
  CONSTRAINT `FK_department_research_areas_departments`
    FOREIGN KEY (`DepartmentID`)
    REFERENCES `unisystem`.`departments` (`DepartmentID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


CREATE TABLE `unisystem`.`lecturer_comittees` (
  `lecturer_id` INT NOT NULL,
  `comittee_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`lecturer_id`, `comittee_name`),
  CONSTRAINT `FK_lecturer_comittees_lecturers`
    FOREIGN KEY (`lecturer_id`)
    REFERENCES `unisystem`.`lecturers` (`LecturerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


CREATE TABLE `unisystem`.`enrollments` (
  `student_id` INT NOT NULL,
  `course_code` INT NOT NULL,
  `lecturer_id` INT NOT NULL,
  `semester` VARCHAR(45) NOT NULL,
  `grade` DECIMAL(5,2) NULL,
  PRIMARY KEY (`student_id`, `course_code`, `semester`),
  INDEX `FK_course_code_courses_idx` (`course_code` ASC) VISIBLE,
  INDEX `FK_lecturer_id_lecturers_idx` (`lecturer_id` ASC) VISIBLE,
  CONSTRAINT `FK_student_id_students`
    FOREIGN KEY (`student_id`)
    REFERENCES `unisystem`.`students` (`idstudents`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_course_code_courses`
    FOREIGN KEY (`course_code`)
    REFERENCES `unisystem`.`course` (`Course_code`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_lecturer_id_lecturers`
    FOREIGN KEY (`lecturer_id`)
    REFERENCES `unisystem`.`lecturers` (`LecturerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


CREATE TABLE `unisystem`.`project_team_members` (
  `project_title` VARCHAR(245) NOT NULL,
  `lecturer_id` INT NOT NULL,
  PRIMARY KEY (`project_title`, `lecturer_id`),
  INDEX `FK_project_team_members_lecturer_id_idx` (`lecturer_id` ASC) VISIBLE,
  CONSTRAINT `FK_project_title_research_projects`
    FOREIGN KEY (`project_title`)
    REFERENCES `unisystem`.`researchprojects` (`ProjectTitle`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_project_team_members_lecturers`
    FOREIGN KEY (`lecturer_id`)
    REFERENCES `unisystem`.`lecturers` (`LecturerID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);



CREATE TABLE `unisystem`.`program_course_requirements` (
  `program_name` VARCHAR(245) NOT NULL,
  `course_code` INT NOT NULL,
  PRIMARY KEY (`program_name`, `course_code`),
  INDEX `FK_program_course_requirements_course_code_courses_idx` (`course_code` ASC) VISIBLE,
  INDEX `FK_program_requirements_program_name_programs_idx` (`program_name` ASC) VISIBLE,
  CONSTRAINT `FK_program_course_requirements_program_name_programs`
    FOREIGN KEY (`program_name`)
    REFERENCES `unisystem`.`programs` (`name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_program_course_requirements_course_code_courses`
    FOREIGN KEY (`course_code`)
    REFERENCES `unisystem`.`course` (`Course_code`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);


CREATE TABLE `unisystem`.`course_prerequisites` (
  `course_code` INT NOT NULL,
  `prerequisite_course_code` INT NOT NULL,
  PRIMARY KEY (`course_code`, `prerequisite_course_code`),
  INDEX `FK_course_prerequisites_prerequisites_course_code_course_idx` (`prerequisite_course_code` ASC) VISIBLE,
  CONSTRAINT `FK_course_prerequisites_course_code_course`
    FOREIGN KEY (`course_code`)
    REFERENCES `unisystem`.`course` (`Course_code`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `FK_course_prerequisites_required`
    FOREIGN KEY (`prerequisite_course_code`)
    REFERENCES `unisystem`.`course` (`Course_code`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);



CREATE TABLE `unisystem`.`student_organizations_registration` (
  `student_id` INT NOT NULL,
  `organization_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`student_id`, `organization_name`),
  CONSTRAINT `FK_student_organizations_registration_student_id_students`
    FOREIGN KEY (`student_id`)
    REFERENCES `unisystem`.`students` (`idstudents`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);






