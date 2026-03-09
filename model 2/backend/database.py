from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite URL for local execution or persistent disk on Render
import os
sqlite_path = os.getenv("SQLITE_PATH", "./pscrm.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{sqlite_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
