from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

Base = declarative_base()
SessionLocal = None
engine = None


def init_db(app):
    global engine, SessionLocal
    database_url = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(database_url, future=True)
    SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))


def get_session():
    return SessionLocal()
