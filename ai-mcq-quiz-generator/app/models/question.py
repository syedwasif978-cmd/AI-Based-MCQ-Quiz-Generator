from sqlalchemy import Column, Integer, String
from ..database.db import Base

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, nullable=False)
    q_text = Column(String(2000))
    opt_a = Column(String(1000))
    opt_b = Column(String(1000))
    opt_c = Column(String(1000))
    opt_d = Column(String(1000))
    order_index = Column(Integer)
