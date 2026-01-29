"""SQLAlchemy models for users and roles."""

import os
from datetime import datetime

from passlib.hash import bcrypt
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = os.environ.get("AUTH_DATABASE_URL", "sqlite:///auth.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    scopes = Column(String, default="")  # space-separated scopes
    created_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="joined")

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, default="")

    users = relationship("User", secondary=user_roles, back_populates="roles", lazy="selectin")


def init_db() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        admin_role = session.query(Role).filter_by(name="admin").one_or_none()
        analyst_role = session.query(Role).filter_by(name="analyst").one_or_none()
        if not admin_role:
            admin_role = Role(name="admin", description="Platform administrator")
            session.add(admin_role)
        if not analyst_role:
            analyst_role = Role(name="analyst", description="Security analyst")
            session.add(analyst_role)
        session.flush()

        admin_user = session.query(User).filter_by(email="admin@cybersentry.ai").one_or_none()
        if not admin_user:
            admin_user = User(email="admin@cybersentry.ai", scopes="alerts:read alerts:write")
            admin_user.set_password(os.environ.get("ADMIN_DEFAULT_PASSWORD", "admin123"))
            admin_user.roles = [admin_role]
            session.add(admin_user)

        analyst_user = session.query(User).filter_by(email="analyst@corp.com").one_or_none()
        if not analyst_user:
            analyst_user = User(email="analyst@corp.com", scopes="alerts:read reports:read")
            analyst_user.set_password(os.environ.get("ANALYST_DEFAULT_PASSWORD", "analyst123"))
            analyst_user.roles = [analyst_role]
            session.add(analyst_user)

        session.commit()


__all__ = [
    "Base",
    "User",
    "Role",
    "user_roles",
    "SessionLocal",
    "engine",
    "init_db",
]
