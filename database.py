import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

raw_db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if raw_db_url.startswith('postgres://'):
    raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)

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
    Base.metadata.create_all(bind=engine)
