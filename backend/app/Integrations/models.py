from sqlalchemy import create_engine, Table, Column, Integer, String, ForeignKey, JSON, MetaData, UniqueConstraint
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

metadata = MetaData()

students = Table(
    "students", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(255)),
    Column("surname", String(255)),
    Column("university", String(255)),
    Column("email", String(255), unique=True),
)

platform_accounts = Table(
    "platform_accounts", metadata,
    Column("id", Integer, primary_key=True),
    Column("student_id", Integer, ForeignKey("students.id")),
    Column("platform_name", String(255)),
    Column("access_token", String(500)),
    Column("refresh_token", String(500), nullable=True),
    Column("platform_user_id", String(255)), 
    UniqueConstraint("platform_user_id", name="uq_platform_user_id"),
)

projects = Table(
    "projects", metadata,
    Column("id", Integer, primary_key=True),
    Column("student_id", Integer, ForeignKey("students.id")),
    Column("title", String(255)),
    Column("content", String(2000)),
    Column("skills", JSON),
    Column("context", String(255)),
    Column("type", String(255)),
    Column("source_platform", String(255)),
)

metadata.create_all(engine)