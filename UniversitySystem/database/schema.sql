CREATE DATABASE IF NOT EXISTS unisystem;
USE unisystem;


CREATE TABLE `unisystem`.`students` (
  `idstudents` INT NOT NULL,
  `studentfirstname` VARCHAR(45) NOT NULL,
  `studentlastname` VARCHAR(45) NOT NULL,
  `dateofbirth` DATE NOT NULL,
  `contactinfo` VARCHAR(245) NOT NULL,
  `program_enrolled` VARCHAR(245) NOT NULL,
  `year_of_study` INT NOT NULL,
  `graduation_status` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idstudents`));


CREATE TABLE `unisystem`.`lecturers` (
  `LecturerID` INT NOT NULL,
  `department` VARCHAR(45) NOT NULL,
  `lecturersfirstname` VARCHAR(45) NOT NULL,
  `lecturerslastname` VARCHAR(45) NOT NULL,
  `departmentID` INT NOT NULL,
  PRIMARY KEY (`LecturerID`));


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
  PRIMARY KEY (`staffID`));

  CREATE TABLE `unisystem`.`course` (
  `Course_code` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(245) NOT NULL,
  `department_level` INT NOT NULL,
  `credits` INT NOT NULL,
  `schedule` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Course_code`));


CREATE TABLE `unisystem`.`departments` (
  `DepartmentName` VARCHAR(45) NOT NULL,
  `Faculty` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`DepartmentName`));


CREATE TABLE `unisystem`.`programs` (
  `name` VARCHAR(45) NOT NULL,
  `degreeAwarded` VARCHAR(45) NOT NULL,
  `duration` VARCHAR(45) NOT NULL,
  `programscol` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`name`));


CREATE TABLE `unisystem`.`researchprojects` (
  `ProjectTitle` VARCHAR(45) NOT NULL,
  `principalInvestigator` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`ProjectTitle`));


--foreign keys/junction tables
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
  `department_name` VARCHAR(45) NOT NULL,
  `research_area` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`department_name`, `research_area`),
  CONSTRAINT `department_name`
    FOREIGN KEY (`department_name`)
    REFERENCES `unisystem`.`departments` (`DepartmentName`)
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



