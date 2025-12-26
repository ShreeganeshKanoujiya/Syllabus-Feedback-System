from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, func, Text, ForeignKey
from database import Base

# 1. Table: stakeholders 
class Stakeholder(Base):
    __tablename__ = "stakeholders"
    stakeholder_id = Column(Integer, primary_key=True, autoincrement=True)
    stakeholder_type = Column(String(50), nullable=False)

# 2. Table: feedback_session
class FeedbackSession(Base):
    __tablename__ = "feedback_session"
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    session_name = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

# 3. Table: stakeholder_personal_info
class StakeholderPersonalInfo(Base):
    __tablename__ = "stakeholder_personal_info"
    person_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("feedback_session.session_id"), nullable=False)
    stakeholder_id = Column(Integer, ForeignKey("stakeholders.stakeholder_id"), nullable=False)
    name = Column(String(100), nullable=False)
    association_name = Column(String(100))

# 4. Table: syllabus_question
class SyllabusQuestion(Base):
    __tablename__ = "syllabus_question"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)

# 5. Table: admin_user 
class AdminUser(Base):
    __tablename__ = "admin_user"
    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)

# 6. Table: feedback_answers
class FeedbackAnswer(Base):
    __tablename__ = "feedback_answers"
    answer_id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey("stakeholder_personal_info.person_id"), nullable=False)
    question_id = Column(Integer, ForeignKey("syllabus_question.id"), nullable=False)
    answer_text = Column(String(255), nullable=False)