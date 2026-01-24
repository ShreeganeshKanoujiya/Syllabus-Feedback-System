CREATE DATABASE IF NOT EXISTS syllabus_feedback;
USE syllabus_feedback;


DROP TABLE IF EXISTS feedback_answers;
DROP TABLE IF EXISTS stakeholder_personal_info;
DROP TABLE IF EXISTS syllabus_question;
DROP TABLE IF EXISTS admin_user;
DROP TABLE IF EXISTS feedback_session;
DROP TABLE IF EXISTS stakeholders;


CREATE TABLE stakeholders (
    stakeholder_id INT AUTO_INCREMENT PRIMARY KEY,
    stakeholder_type VARCHAR(50) NOT NULL
);


CREATE TABLE feedback_session (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    session_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE stakeholder_personal_info (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    stakeholder_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    association_name VARCHAR(100),

    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(stakeholder_id),
    FOREIGN KEY (session_id) REFERENCES feedback_session(session_id)
);


CREATE TABLE syllabus_question (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    stakeholder_type VARCHAR(50) NOT NULL,
    category ENUM('DEMOGRAPHIC','SYLLABUS','SUGGESTION') NOT NULL
);


CREATE TABLE admin_user (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);


CREATE TABLE feedback_answers (
    answer_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    question_id INT NOT NULL,
    answer_text VARCHAR(255) NOT NULL,

    FOREIGN KEY (person_id) REFERENCES stakeholder_personal_info(person_id),
    FOREIGN KEY (question_id) REFERENCES syllabus_question(id)
);


-- ================= TEACHER =================
INSERT INTO syllabus_question (text, stakeholder_type, category) VALUES
-- DEMOGRAPHIC
('Name', 'TEACHER', 'DEMOGRAPHIC'),
('Email ID (Enter SIES edu ID only)', 'TEACHER', 'DEMOGRAPHIC'),
('Course', 'TEACHER', 'DEMOGRAPHIC'),
('Class', 'TEACHER', 'DEMOGRAPHIC'),

-- SYLLABUS
('Relevance of Syllabus Content : How well does the syllabus align with industry trends, technological advancements, and current academic standards?', 'TEACHER', 'SYLLABUS'),
('Depth and Coverage : Does the syllabus provide a balanced mix of fundamental and advanced topics?', 'TEACHER', 'SYLLABUS'),
('Practical Application : To what extent does the syllabus integrate hands on learning and real-world problem-solving?', 'TEACHER', 'SYLLABUS'),
('Assessment Methods : How effectively do assessments align with learning outcomes?', 'TEACHER', 'SYLLABUS'),
('Teaching Pedagogies : How effective are the teaching methodologies?', 'TEACHER', 'SYLLABUS'),
('How would you rate the Overall Syllabus?', 'TEACHER', 'SYLLABUS'),

-- SUGGESTION
('Suggestions for improvement based on your teaching experience.', 'TEACHER', 'SUGGESTION');

-- ================= STUDENT =================
INSERT INTO syllabus_question (text, stakeholder_type, category) VALUES
-- DEMOGRAPHIC
('Student Name', 'STUDENT', 'DEMOGRAPHIC'),
('Roll Number / PRN', 'STUDENT', 'DEMOGRAPHIC'),
('Email ID (Enter SIES edu ID only)', 'STUDENT', 'DEMOGRAPHIC'),
('Program / Course', 'STUDENT', 'DEMOGRAPHIC'),
('Class', 'STUDENT', 'DEMOGRAPHIC'),
('Academic Year', 'STUDENT', 'DEMOGRAPHIC'),

-- SYLLABUS
('How well does the syllabus align with current industry trends?', 'STUDENT', 'SYLLABUS'),
('Does the syllabus provide a balanced mix of fundamental and advanced topics?', 'STUDENT', 'SYLLABUS'),
('How effective are the teaching methodologies?', 'STUDENT', 'SYLLABUS'),
('How well does the syllabus prepare you for employment or higher studies?', 'STUDENT', 'SYLLABUS'),

-- SUGGESTION
('Any other feedback or suggestions regarding curriculum or NEP implementation?', 'STUDENT', 'SUGGESTION');

-- ================= ALUMNI =================
INSERT INTO syllabus_question (text, stakeholder_type, category) VALUES
-- DEMOGRAPHIC
('Student Name', 'ALUMNI', 'DEMOGRAPHIC'),
('Email ID', 'ALUMNI', 'DEMOGRAPHIC'),
('Course', 'ALUMNI', 'DEMOGRAPHIC'),

-- SYLLABUS
('Relevance of syllabus content with industry trends and academic standards', 'ALUMNI', 'SYLLABUS'),
('Depth and coverage of syllabus topics', 'ALUMNI', 'SYLLABUS'),
('Practical application and real-world problem solving', 'ALUMNI', 'SYLLABUS'),
('Effectiveness of assessment methods', 'ALUMNI', 'SYLLABUS'),
('Effectiveness of teaching pedagogies', 'ALUMNI', 'SYLLABUS'),
('Overall satisfaction with the syllabus learned', 'ALUMNI', 'SYLLABUS'),

-- SUGGESTION
('Suggestions for improving syllabus, teaching methods, or learning experience', 'ALUMNI', 'SUGGESTION');

-- ================= EMPLOYER =================
INSERT INTO syllabus_question (text, stakeholder_type, category) VALUES
-- DEMOGRAPHIC
('Name of Employer', 'EMPLOYER', 'DEMOGRAPHIC'),
('Name of Institution / Organization', 'EMPLOYER', 'DEMOGRAPHIC'),
('Designation', 'EMPLOYER', 'DEMOGRAPHIC'),
('Email Address', 'EMPLOYER', 'DEMOGRAPHIC'),
('Stream from which students are employed', 'EMPLOYER', 'DEMOGRAPHIC'),

-- SYLLABUS
('Curriculum relevance for employability', 'EMPLOYER', 'SYLLABUS'),
('Curriculum effectiveness in developing innovative thinking', 'EMPLOYER', 'SYLLABUS'),
('Effectiveness of syllabus in developing skill-oriented human resources', 'EMPLOYER', 'SYLLABUS'),
('Need-based nature of the current syllabus as per industry requirements', 'EMPLOYER', 'SYLLABUS'),
('Effectiveness of curriculum in developing entrepreneurship skills', 'EMPLOYER', 'SYLLABUS'),
('Student sensitivity towards ethics, values, sustainability, and social issues', 'EMPLOYER', 'SYLLABUS'),
('Students are equipped with latest developments in their field', 'EMPLOYER', 'SYLLABUS'),

-- SUGGESTION
('Topics that should be included in the curriculum', 'EMPLOYER', 'SUGGESTION'),
('Opinion on implementation of NEP and Autonomy in the college', 'EMPLOYER', 'SUGGESTION');

-- ================= OUTSIDE COLLEGE TEACHER =================
INSERT INTO syllabus_question (text, stakeholder_type, category) VALUES
-- DEMOGRAPHIC
('Name of Respondent', 'OUTSIDE_TEACHER', 'DEMOGRAPHIC'),
('College of Respondent', 'OUTSIDE_TEACHER', 'DEMOGRAPHIC'),
('Subject Name', 'OUTSIDE_TEACHER', 'DEMOGRAPHIC'),
('Email', 'OUTSIDE_TEACHER', 'DEMOGRAPHIC'),
('Program Name', 'OUTSIDE_TEACHER', 'DEMOGRAPHIC'),
('Years / Semester taught', 'OUTSIDE_TEACHER', 'DEMOGRAPHIC'),

-- SYLLABUS
('Entrepreneurship skill development through course content', 'OUTSIDE_TEACHER', 'SYLLABUS'),
('Employability relevance of course content', 'OUTSIDE_TEACHER', 'SYLLABUS'),
('Contribution of course content to skill development', 'OUTSIDE_TEACHER', 'SYLLABUS'),
('Alignment of course content with recent trends and advancements', 'OUTSIDE_TEACHER', 'SYLLABUS');

-- ================= PARENTS =================
INSERT INTO syllabus_question (text, stakeholder_type, category) VALUES
-- DEMOGRAPHIC
('Name of Parent', 'PARENT', 'DEMOGRAPHIC'),
('Name of Ward', 'PARENT', 'DEMOGRAPHIC'),
('Wards Stream', 'PARENT', 'DEMOGRAPHIC'),

-- SYLLABUS
('Overall satisfaction with NEP implementation', 'PARENT', 'SYLLABUS'),
('Flexibility of curriculum for diverse subject exploration', 'PARENT', 'SYLLABUS'),
('Employability focus of the curriculum', 'PARENT', 'SYLLABUS'),
('Support for industry-relevant skill development', 'PARENT', 'SYLLABUS'),
('Inclusion of practical learning opportunities', 'PARENT', 'SYLLABUS'),
('Holistic development through co-curricular activities under NEP', 'PARENT', 'SYLLABUS'),
('Collaboration and teamwork opportunities in syllabus', 'PARENT', 'SYLLABUS'),
('Overall impact of NEP on educational quality', 'PARENT', 'SYLLABUS'),

-- SUGGESTION
('Suggestions for new topics to be included in the syllabus', 'PARENT', 'SUGGESTION'),
('Additional comments or suggestions regarding NEP implementation', 'PARENT', 'SUGGESTION');


