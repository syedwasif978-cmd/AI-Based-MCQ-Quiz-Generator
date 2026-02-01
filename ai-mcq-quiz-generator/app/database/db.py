from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import os
import sys

Base = declarative_base()
SessionLocal = None
engine = None


def init_db(app):
    """Initialize DB engine and session. If the configured database cannot be used
    (for example oracledb not installed), fall back to a local SQLite DB so the
    app can run for local development and testing."""
    global engine, SessionLocal
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI')

    if not database_url:
        # default to local sqlite
        database_url = 'sqlite:///./dev.db'

    try:
        engine = create_engine(database_url, future=True)
        # try a quick connection check
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print(f"[db] Connected to database: {database_url}")
    except Exception as e:
        print(f"[db] Failed to connect to configured DB ({database_url}): {e}", file=sys.stderr)
        print("[db] Falling back to local sqlite database at ./dev.db", file=sys.stderr)
        engine = create_engine('sqlite:///./dev.db', future=True)

    SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))


def get_session():
    return SessionLocal()
