import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "makers")
MYSQL_USER = os.environ.get("MYSQL_USER", "makers")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "makers")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
SQLALCHEMY_DATABASE_URL = os.environ.get("MYSQL_URL",
                                         f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()