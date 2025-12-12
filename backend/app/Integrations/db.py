import os
from sqlalchemy import create_engine

# Use environment variable if set, otherwise fallback to a local SQLite database for testing
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")

# For SQLite, add connect_args
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
