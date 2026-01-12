CREATE DATABASE IF NOT EXISTS syllabus_feedback;
USE syllabus_feedback;


-- Drop tables in correct order to avoid FK errors (optional)
DROP TABLE IF EXISTS feedback_answers;
DROP TABLE IF EXISTS stakeholder_personal_info;
DROP TABLE IF EXISTS syllabus_question;
DROP TABLE IF EXISTS admin_user;
DROP TABLE IF EXISTS feedback_session;
DROP TABLE IF EXISTS stakeholders;

------------------------------------------------------------
-- 1. Table: stakeholders
------------------------------------------------------------
CREATE TABLE stakeholders (
    stakeholder_id INT AUTO_INCREMENT PRIMARY KEY,
    stakeholder_type VARCHAR(50) NOT NULL
);

------------------------------------------------------------
-- 2. Table: feedback_session
------------------------------------------------------------
CREATE TABLE feedback_session (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    session_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

------------------------------------------------------------
-- 3. Table: stakeholder_personal_info
------------------------------------------------------------
CREATE TABLE stakeholder_personal_info (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    stakeholder_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    association_name VARCHAR(100),

    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(stakeholder_id),
    FOREIGN KEY (session_id) REFERENCES feedback_session(session_id)
);

------------------------------------------------------------
-- 4. Table: syllabus_question
------------------------------------------------------------
CREATE TABLE syllabus_question (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL
);

------------------------------------------------------------
-- 5. Table: admin_user
------------------------------------------------------------
CREATE TABLE admin_user (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);

------------------------------------------------------------
-- 6. Table: feedback_answers
------------------------------------------------------------
CREATE TABLE feedback_answers (
    answer_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    question_id INT NOT NULL,
    answer_text VARCHAR(255) NOT NULL,

    FOREIGN KEY (person_id) REFERENCES stakeholder_personal_info(person_id),
    FOREIGN KEY (question_id) REFERENCES syllabus_question(id)
);

INSERT INTO syllabus_question (text) VALUES

-- ================= TEACHER : DEMOGRAPHIC =================
('[TEACHER][DEMOGRAPHIC] Name'),
('[TEACHER][DEMOGRAPHIC] Email ID (Enter SIES edu ID only)'),
('[TEACHER][DEMOGRAPHIC] Course(BCom, B.Com(Accounting and finance), B.Com(Banking and Insurance), B.Com(Financial Market), BSc.IT, BSc.CS, BMS, BAMMC, BSc.PT, BSc.EVS, ENT.M BMAF, MCom ADVANCED ACCOUNTANCY, MCOM BUSINESS MANAGEMENT, MA ECONOMICS, MSc.CS, MSc.IT, MSc.EVS, MAMMC, BSc.DS, OTHER)'),
('[TEACHER][DEMOGRAPHIC] Class (FY, SY, TY, PG-1, PG-2)'),

-- ================= TEACHER : SYLLABUS =================
('[TEACHER][SYLLABUS] Relevance of Syllabus Content – How well does the syllabus align with industry trends, technological advancements, and current academic standards?'),
('[TEACHER][SYLLABUS] Depth and Coverage – Does the syllabus provide a balanced mix of fundamental and advanced topics, ensuring a comprehensive understanding of the subject?'),
('[TEACHER][SYLLABUS] Practical Application – To what extent does the syllabus integrate hands-on learning, industry use cases, and real-world problem-solving?'),
('[TEACHER][SYLLABUS] Assessment Methods – How effectively do the assessments (assignments, exams, projects) align with the syllabus objectives and learning outcomes?'),
('[TEACHER][SYLLABUS] Teaching Pedagogies – How effective are the teaching methodologies (lectures, case studies, flipped classrooms, interactive sessions, industry interactions, etc.) in delivering the syllabus content?'),
('[TEACHER][SYLLABUS] How would you rate the Overall Syllabus?'),
('[TEACHER][SYLLABUS] Suggestions for Improvement-Based on your Teaching Experience,What changes or enhancements would you recommend to improve the syllabus, teaching methods, or overall experience?(Subjectwise Suggestions,If Any)'),

-- ================= ALUMNI : DEMOGRAPHIC =================
('[ALUMNI][DEMOGRAPHIC] Student Name'),
('[ALUMNI][DEMOGRAPHIC] Email ID'),
('[ALUMNI][DEMOGRAPHIC] Course(BCom, B.Com(Accounting and finance), B.Com(Banking and Insurance), B.Com(Financial Market), BSc.IT, BSc.CS, BMS, BAMMC, BSc.PT, BSc.EVS, ENT.M BMAF, MCom ADVANCED ACCOUNTANCY, MCOM BUSINESS MANAGEMENT, MA ECONOMICS, MSc.CS, MSc.IT, MSc.EVS, MAMMC, BSc.DS, OTHER)'),

-- ================= ALUMNI : SYLLABUS =================
('[ALUMNI][SYLLABUS] Relevance of Syllabus Content – How well does the syllabus align with industry trends, technological advancements, and current academic standards?'),
('[ALUMNI][SYLLABUS] Depth and Coverage – Does the syllabus provide a balanced mix of fundamental and advanced topics, ensuring a comprehensive understanding of the subject?'),
('[ALUMNI][SYLLABUS] Practical Application – To what extent does the syllabus integrate hands-on learning, industry use cases, and real-world problem-solving?'),
('[ALUMNI][SYLLABUS] Assessment Methods – How effectively do the assessments (assignments, exams, projects) align with the syllabus objectives and learning outcomes?'),
('[ALUMNI][SYLLABUS]Teaching Pedagogies – How effective are the teaching methodologies (lectures, case studies, flipped classrooms, interactive sessions, industry interactions, etc.) in delivering the syllabus content?'),
('[ALUMNI][SYLLABUS] How satisfied are you with the overall syllabus you have learned?'),
('[ALUMNI][SYLLABUS] Suggestions for Improvement-What changes or enhancements would you recommend to improve the syllabus, teaching methods, or overall learning experience?'),

-- ================= EMPLOYER : DEMOGRAPHIC =================
('[EMPLOYER][DEMOGRAPHIC] Name of Employer'),
('[EMPLOYER][DEMOGRAPHIC] Name of Institution/Organization'),
('[EMPLOYER][DEMOGRAPHIC] Designation'),
('[EMPLOYER][DEMOGRAPHIC] Email Address'),
('[EMPLOYER][DEMOGRAPHIC] Stream from which students employed in your organization(BCom, B.Com(Accounting and finance), B.Com(Banking and Insurance), B.Com(Financial Market), BSc.IT, BSc.CS, BMS, BAMMC, BSc.PT, BSc.EVS, ENT.M BMAF, MCom ADVANCED ACCOUNTANCY, MCOM BUSINESS MANAGEMENT, MA ECONOMICS, MSc.CS, MSc.IT, MSc.EVS, MAMMC, BSc.DS, OTHER)'),

-- ================= EMPLOYER : SYLLABUS =================
('[EMPLOYER][SYLLABUS] The curriculum is relevant for employability'),
('[EMPLOYER][SYLLABUS] The curriculum is effective in developing innovative thinking'),
('[EMPLOYER][SYLLABUS] The syllabus is effective in developing skill-oriented human resources'),
('[EMPLOYER][SYLLABUS] The current syllabus is need-based as per industry requirements'),
('[EMPLOYER][SYLLABUS] The curriculum is effective for development of entrepreneurship skills'),
('[EMPLOYER][SYLLABUS] Student employees from SIES Nerul College are sensitized towards cross-cutting issues like gender equality, environment and sustainability, ethics and values, etc. through relevant courses in the curriculum'),
('[EMPLOYER][SYLLABUS] Students are equipped with the latest developments in their field as the courses taught are up to date'),
('[EMPLOYER][SYLLABUS] Please suggest at least one topic that you think should be included in the curriculum'),
('[EMPLOYER][SYLLABUS] What is your opinion about the implementation of NEP and Autonomy in the college?'),

-- ================= OUTSIDE COLLEGE TEACHER : DEMOGRAPHIC =================
('[OUTSIDE_TEACHER][DEMOGRAPHIC] Name of Respondent'),
('[OUTSIDE_TEACHER][DEMOGRAPHIC] College of Respondent'),
('[OUTSIDE_TEACHER][DEMOGRAPHIC] Subject Name'),
('[OUTSIDE_TEACHER][DEMOGRAPHIC] Email'),
('[OUTSIDE_TEACHER][DEMOGRAPHIC] Program Name(BCom, B.Com(Accounting and finance), B.Com(Banking and Insurance), B.Com(Financial Market), BSc.IT, BSc.CS, BMS, BAMMC, BSc.PT, BSc.EVS, ENT.M BMAF, MCom ADVANCED ACCOUNTANCY, MCOM BUSINESS MANAGEMENT, MA ECONOMICS, MSc.CS, MSc.IT, MSc.EVS, MAMMC, BSc.DS, OTHER)'),
('[OUTSIDE_TEACHER][DEMOGRAPHIC] Years of Semester(FY Sem I, FY Sem II, SY Sem III, SY Sem IV, TY Sem V, TY Sem VI)'),

-- ================= OUTSIDE COLLEGE TEACHER : SYLLABUS =================
('[OUTSIDE_TEACHER][SYLLABUS] Entrepreneurship Skills – How effectively does the course content support the development of entrepreneurial skills among students?'),
('[OUTSIDE_TEACHER][SYLLABUS] Employability Relevance – To what extent does the course content prepare students for employability and professional requirements?'),
('[OUTSIDE_TEACHER][SYLLABUS] Skill Development – How well does the course content contribute to the development of practical, analytical, and technical skills?'),
('[OUTSIDE_TEACHER][SYLLABUS] Alignment with Recent Trends – How adequately does the course content reflect recent developments, emerging trends, and advancements in the subject area?'),


-- ================= PARENT : DEMOGRAPHIC =================
('[PARENT][DEMOGRAPHIC] Name of Parent'),
('[PARENT][DEMOGRAPHIC] Name of Ward'),
('[PARENT][DEMOGRAPHIC] Please select your Child’s Stream'),

-- ================= PARENT : SYLLABUS / NEP =================
('[PARENT][SYLLABUS] Overall Satisfaction with NEP Implementation How satisfied are you with the overall implementation of NEP in the college?'),
('[PARENT][SYLLABUS] Flexibility of the Curriculum How much do you agree with the following statement? "The curriculum allows flexibility to explore diverse subjects." '),
('[PARENT][SYLLABUS] Employability Focus How much do you agree with the following statement? "The curriculum enhances employability opportunities for students."'),
('[PARENT][SYLLABUS] Support for Skill Development How much do you agree with the following statement? "The syllabus supports skill development relevant to industry needs."'),
('[PARENT][SYLLABUS] Inclusion of Practical Learning How much do you agree with the following statement? "The syllabus provides valuable practical learning opportunities."'),
('[PARENT][SYLLABUS] Holistic Development Opportunities How much do you agree with the following statement? "The NEP ensures holistic development through co-curricular activities."'),
('[PARENT][SYLLABUS] Collaboration and Teamwork Opportunities How much do you agree with the following statement? "The syllabus promotes collaboration and teamwork among students."'),
('[PARENT][SYLLABUS] Overall Impact of NEP on Educational Quality How would you rate the overall impact of NEP implementation on the quality of education your child is receiving?'),
('[PARENT][SYLLABUS] Suggestions for New Topics Please suggest any topics you feel should be included in the syllabus:'),
('[PARENT][SYLLABUS] Please share any additional comments or suggestions regarding the NEP implementation:'),

-- ================= STUDENT : DEMOGRAPHIC =================
('[STUDENT][DEMOGRAPHIC] Student Name'),
('[STUDENT][DEMOGRAPHIC] Roll Number / PRN'),
('[STUDENT][DEMOGRAPHIC] Email ID (Enter SIES edu ID only)'),
('[STUDENT][DEMOGRAPHIC] Program / Course
 (BCom, B.Com (Accounting & Finance), B.Com (Banking & Insurance), B.Com (Financial Market), BSc.IT, BSc.CS, BMS, BAMMC, BSc.PT, BSc.EVS, BSc.DS, MSc.IT, MSc.CS, MCom, MA Economics, OTHER)'),
('[STUDENT][DEMOGRAPHIC] Class (FY / SY / TY / PG-1 / PG-2)'),
('[STUDENT][DEMOGRAPHIC] Academic Year'),

-- ================= STUDENT : SYLLABUS =================
('[STUDENT][SYLLABUS] How well does the syllabus align with current industry trends and real-world applications?'),
('[STUDENT][SYLLABUS] Does the syllabus provide a balanced mix of fundamental concepts and advanced topics?'),
('[STUDENT][SYLLABUS] How effective are the teaching methodologies used to deliver the syllabus content?'),
('[STUDENT][SYLLABUS] To what extent does the syllabus include practical learning, projects, internships, or hands-on activities?'),
('[STUDENT][SYLLABUS] How effectively do assignments, internal assessments, and exams reflect the syllabus objectives and learning outcomes?'),
('[STUDENT][SYLLABUS] How well does the syllabus prepare you for employment, higher studies, or entrepreneurship?'),
('[STUDENT][SYLLABUS] How satisfied are you with the flexibility offered by NEP (electives, skill-based courses, multidisciplinary learning)?'),
('[STUDENT][SYLLABUS] Any other feedback or suggestions regarding curriculum, NEP implementation, or overall learning experience.');


