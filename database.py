import os
import socket
import logging
from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("ai_fitness")

raw_db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if raw_db_url.startswith('postgres://'):
    raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)

# Render Cross-Region / External URL Auto-Resolver:
# If Render Postgres internal hostname (e.g. dpg-xxxx-a) cannot be resolved (due to cross-region deployment),
# auto-detect and append the correct Render region domain (e.g. .oregon-postgres.render.com).
try:
    parsed = urlparse(raw_db_url)
    if parsed.hostname and parsed.hostname.startswith('dpg-') and '.' not in parsed.hostname:
        try:
            socket.gethostbyname(parsed.hostname)
        except socket.gaierror:
            logger.info("Internal host '%s' not resolvable. Attempting to auto-resolve Render region...", parsed.hostname)
            for region in ['oregon', 'frankfurt', 'ohio', 'singapore', 'virginia']:
                candidate = f"{parsed.hostname}.{region}-postgres.render.com"
                try:
                    socket.gethostbyname(candidate)
                    logger.info("Successfully resolved Render Postgres host to: %s", candidate)
                    netloc = candidate
                    if parsed.port:
                        netloc = f"{candidate}:{parsed.port}"
                    if parsed.username or parsed.password:
                        auth = parsed.username or ""
                        if parsed.password:
                            auth = f"{auth}:{parsed.password}"
                        netloc = f"{auth}@{netloc}"
                    raw_db_url = urlunparse(parsed._replace(netloc=netloc))
                    break
                except socket.gaierror:
                    continue
except Exception as e:
    logger.warning("Error inspecting database URL: %s", e)

# Render PostgreSQL requires SSL mode
if raw_db_url.startswith('postgresql') and 'sslmode' not in raw_db_url:
    separator = '&' if '?' in raw_db_url else '?'
    raw_db_url = f"{raw_db_url}{separator}sslmode=require"

connect_args = {}
if raw_db_url.startswith('sqlite'):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    raw_db_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300 if not raw_db_url.startswith('sqlite') else -1,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    global engine, SessionLocal
    try:
        with engine.connect() as conn:
            pass
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully with primary engine (%s).", engine.url.drivername)
    except Exception as e:
        logger.error(
            "Primary database connection failed for '%s': %s. "
            "Falling back to local SQLite database so the application stays fully online and healthy.",
            engine.url.render_as_string(hide_password=True),
            e,
        )
        fallback_url = "sqlite:///database.db"
        engine = create_engine(fallback_url, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.info("Fallback SQLite database initialized successfully.")
