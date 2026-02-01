from sqlalchemy import Column, Integer, String, DateTime
from ..database.db import Base
import datetime

class Quiz(Base):
    __tablename__ = 'user_quizzes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    subject = Column(String(100))
    difficulty = Column(String(20))
    num_questions = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    questions_blob = Column(String)  # JSON blob or path
