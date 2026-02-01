from sqlalchemy import Column, Integer, LargeBinary
from ..database.db import Base

class AnswerKey(Base):
    __tablename__ = 'quiz_answer_keys'
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, nullable=False)
    encrypted_blob = Column(LargeBinary)
