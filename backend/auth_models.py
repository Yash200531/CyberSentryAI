"""User and role models for auth service.

Uses SQLite by default; configure AUTH_DATABASE_URL env var for other backends.
"""

import os
from datetime import datetime

import bcrypt as _bcrypt

# passlib expects bcrypt.__about__.__version__; newer bcrypt drops it, so patch it
if not hasattr(_bcrypt, "__about__"):
    class _About:
        __version__ = getattr(_bcrypt, "__version__", "0")

    _bcrypt.__about__ = _About()

from passlib.hash import bcrypt as passlib_bcrypt
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, create_engine, func
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
        self.password_hash = passlib_bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        return passlib_bcrypt.verify(password, self.password_hash)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, default="")

    users = relationship("User", secondary=user_roles, back_populates="roles", lazy="selectin")


def init_db() -> None:
    """Create tables and seed default users/roles if empty."""
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        admin_email = (os.environ.get("ADMIN_EMAIL") or "admin@cyber.in").strip().lower()
        admin_password = os.environ.get("ADMIN_PASSWORD") or "Admintest123"
        analyst_email = (os.environ.get("ANALYST_EMAIL") or "analyst@co.in").strip().lower()
        analyst_password = os.environ.get("ANALYST_PASSWORD") or "Sw@gtm!1"

        # Seed roles
        admin_role = session.query(Role).filter_by(name="admin").one_or_none()
        analyst_role = session.query(Role).filter_by(name="analyst").one_or_none()
        if not admin_role:
            admin_role = Role(name="admin", description="Platform administrator")
            session.add(admin_role)
        if not analyst_role:
            analyst_role = Role(name="analyst", description="Security analyst")
            session.add(analyst_role)
        session.flush()

        # Remove any legacy/demo users
        allowed_emails = {admin_email, analyst_email}
        for user in session.query(User).all():
            if user.email.lower() not in allowed_emails:
                session.delete(user)

        # Seed users
        admin_user = session.query(User).filter(func.lower(User.email) == admin_email).one_or_none()
        if not admin_user:
            admin_user = User(email=admin_email, scopes="alerts:read alerts:write", is_active=True)
            admin_user.set_password(admin_password)
            admin_user.roles = [admin_role]
            session.add(admin_user)
        else:
            if not admin_user.verify_password(admin_password):
                admin_user.set_password(admin_password)
            admin_user.roles = [admin_role]
            admin_user.is_active = True

        analyst_user = session.query(User).filter(func.lower(User.email) == analyst_email).one_or_none()
        if not analyst_user:
            analyst_user = User(email=analyst_email, scopes="alerts:read reports:read", is_active=True)
            analyst_user.set_password(analyst_password)
            analyst_user.roles = [analyst_role]
            session.add(analyst_user)
        else:
            if not analyst_user.verify_password(analyst_password):
                analyst_user.set_password(analyst_password)
            analyst_user.roles = [analyst_role]
            analyst_user.is_active = True

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
