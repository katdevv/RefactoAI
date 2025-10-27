# server/database/db_models.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

# 1) Prefer absolute DATABASE_PATH if available; fallback to DATABASE_URL.
db_path = os.getenv("DATABASE_PATH")
db_url = os.getenv("DATABASE_URL")

if db_path:
    # Build a proper sqlite URL from the absolute path
    DATABASE_URL = f"sqlite:///{db_path}"
elif db_url:
    DATABASE_URL = db_url
else:
    raise RuntimeError("Neither DATABASE_PATH nor DATABASE_URL is set in .env")

# 2) SQLite specific connect arg (safe for others to leave empty)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# 3) Create engine (THIS was missing in your snippet)
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args=connect_args,
)

class Base(DeclarativeBase):
    pass

# 4) Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 5) FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional: quick sanity print on startup to confirm path
print("▶ Using DB URL:", DATABASE_URL)
