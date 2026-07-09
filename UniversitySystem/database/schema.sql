CREATE DATABASE IF NOT EXISTS UniversitySystem;
USE UniversitySystem;


CREATE TABLE `unisystem`.`students` (
  `idstudents` INT NOT NULL,
  `studentfirstname` VARCHAR(45) NOT NULL,
  `studentlastnane` VARCHAR(45) NOT NULL,
  `dateofbirth` INT NOT NULL,
  `contactinfo` VARCHAR(245) NOT NULL,
  `program enrolled` VARCHAR(245) NOT NULL,
  `year of study` INT NOT NULL,
  `graduation status` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idstudents`));


CREATE TABLE `unisystem`.`lecturers` (
  `LecturerID` INT NOT NULL,
  `department` VARCHAR(45) NOT NULL,
  `lecturersfirstname` VARCHAR(45) NOT NULL,
  `lecturerslastname` VARCHAR(45) NOT NULL,
  `departmentID` INT NOT NULL,
  PRIMARY KEY (`LecturerID`));


  CREATE TABLE `unisystem`.`non_academic staff` (
  `staffID` INT NOT NULL,
  `firstname` VARCHAR(45) NOT NULL,
  `lastname` VARCHAR(45) NOT NULL,
  `job title` VARCHAR(45) NOT NULL,
  `departmentID` INT NOT NULL,
  `employment type` VARCHAR(45) NOT NULL,
  `contact details` VARCHAR(45) NOT NULL,
  `salary information` VARCHAR(45) NOT NULL,
  `emergency contact` VARCHAR(245) NOT NULL,
  PRIMARY KEY (`staffID`));

  CREATE TABLE `unisystem`.`course` (
  `Course code` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(245) NOT NULL,
  `department level` INT NOT NULL,
  `credits` INT NOT NULL,
  `schedule` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Course code`));


CREATE TABLE `unisystem`.`departments` (
  `DepartmentName` INT NOT NULL,
  `Faculty` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`DepartmentName`));

--edited departments entity because department name attribute was integer

ALTER TABLE `unisystem`.`departments` 
CHANGE COLUMN `DepartmentName` `DepartmentName` VARCHAR(45) NOT NULL ;



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
  `studentID` INT NOT NULL,
  PRIMARY KEY (`recordID`),
  INDEX `studentID_idx` (`studentID` ASC) VISIBLE,
  CONSTRAINT `idstudents`
    FOREIGN KEY (`studentID`)
    REFERENCES `unisystem`.`students` (`idstudents`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
--added new column to student_disciplinary_records table and renamed "studentID" to "idstudents" to match the primary key in the students table
ALTER TABLE `unisystem`.`student_disciplinary_records` 
DROP FOREIGN KEY `idstudents`;
ALTER TABLE `unisystem`.`student_disciplinary_records` 
ADD COLUMN `incident_description` VARCHAR(245) NOT NULL AFTER `idstudent`,
CHANGE COLUMN `studentID` `idstudent` INT NOT NULL ;
ALTER TABLE `unisystem`.`student_disciplinary_records` 
ADD CONSTRAINT `idstudents`
  FOREIGN KEY (`idstudent`)
  REFERENCES `unisystem`.`students` (`idstudents`);


CREATE TABLE `unisystem`.`lecturer_qualifications` (
  `qualificationID` INT NOT NULL,
  `LecturerID` INT NOT NULL,
  `degree_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`qualificationID`),
  INDEX `LecturerID_idx` (`LecturerID` ASC) VISIBLE,
  CONSTRAINT `LecturerID`
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
    REFERENCES `unisystem`.`course` (`Course code`)
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



