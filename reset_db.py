
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

SQL_SCRIPT = """
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
    text VARCHAR(255) NOT NULL
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
"""

def reset_database():
    print(f"Connecting to {DB_HOST}:{DB_PORT} as {DB_USER}...")
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Split by ; and execute each statement
            statements = SQL_SCRIPT.split(';')
            for statement in statements:
                if statement.strip():
                    print(f"Executing: {statement.strip()[:50]}...")
                    cursor.execute(statement)
        
        connection.commit()
        connection.close()
        print("Database reset successfully.")
        
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
