from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import os
import sys
import re

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

    # If Oracle is configured, optionally attempt to initialize oracledb in thick mode
    if database_url and 'oracle' in database_url:
        # Check for explicit Instant Client path in env
        instant_client_dir = os.getenv('ORACLE_INSTANT_CLIENT_PATH')
        try:
            import oracledb
            # If user provided a path, try initializing thick mode
            if instant_client_dir:
                try:
                    oracledb.init_oracle_client(lib_dir=instant_client_dir)
                    print(f"[db] Initialized oracledb thick mode with {instant_client_dir}")
                except Exception as ie:
                    print(f"[db] Failed to init oracledb thick mode: {ie}", file=sys.stderr)
            # else leave default driver state (thin by default)
        except ImportError:
            # oracledb not installed; SQLAlchemy will raise on engine creation
            print("[db] python-oracledb not installed; install oracledb or use local sqlite.", file=sys.stderr)
        except Exception as ie:
            print(f"[db] oracledb init check error: {ie}", file=sys.stderr)

    try:
        engine = create_engine(database_url, future=True)
        # try a quick connection check
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print(f"[db] Connected to database: {database_url}")
    except Exception as e:
        # Detect common python-oracledb thin-mode compatibility error (DPY-3010)
        msg = str(e)
        if 'DPY-3010' in msg or 'thin mode' in msg:
            print("[db] Detected python-oracledb thin-mode compatibility issue (DPY-3010).", file=sys.stderr)
            print("[db] Recommended fix: install Oracle Instant Client and set ORACLE_INSTANT_CLIENT_PATH to its directory, then restart the app.", file=sys.stderr)
            print("See: https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html", file=sys.stderr)
        else:
            # Generic connection failure
            print(f"[db] Failed to connect to configured DB ({database_url}): {e}", file=sys.stderr)

        print("[db] Falling back to local sqlite database at ./dev.db", file=sys.stderr)
        engine = create_engine('sqlite:///./dev.db', future=True)

    SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))


def get_session():
    return SessionLocal()
