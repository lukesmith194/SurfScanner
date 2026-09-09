"""Persistence for accounts, follows and community posts.

Uses a hosted Postgres database when a DATABASE_URL is configured (required
for a real deployment — most hosts, including Streamlit Community Cloud,
don't guarantee a local file survives a restart or redeploy, so a SQLite
file would silently lose all accounts/posts). Falls back to a local SQLite
file for zero-setup local development. The original repo's config.py already
had (unused) SQLAlchemy wiring for a MySQL connection; this follows the same
ORM, just pointed at whichever database is configured.

DATABASE_URL is read from, in order: the DATABASE_URL environment variable
(works on Render/Railway/Fly/etc.), then Streamlit's secrets (for Streamlit
Community Cloud specifically — set it in the app's Settings > Secrets as
DATABASE_URL = "postgresql://..."). Never commit real credentials — secrets
live in .streamlit/secrets.toml locally, which is gitignored.
"""

import os
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    create_engine,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        try:
            import streamlit as st

            url = st.secrets["DATABASE_URL"]
        except Exception:
            url = None
    if not url:
        local_path = Path(__file__).resolve().parent / "surfscanner.db"
        return f"sqlite:///{local_path}"
    # Some hosted Postgres providers (Heroku-style) hand out "postgres://",
    # but SQLAlchemy's psycopg driver requires "postgresql://".
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


DATABASE_URL = _database_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(80))
    # Home departure city — one of spots.DEPARTURE_CITIES' keys, kept as
    # plain text rather than a foreign key since that list is static config,
    # not a database table.
    home_city: Mapped[str] = mapped_column(String(80))
    surf_level: Mapped[str] = mapped_column(String(20))  # Beginner/Intermediate/Advanced
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Follow(Base):
    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint("follower_id", "followed_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Post(Base):
    """A planned-trip post: 'I'm planning {spot_name} on {dates}'."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    spot_name: Mapped[str] = mapped_column(String(80))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    # Snapshot of the author's level at post time, so editing your profile
    # later doesn't rewrite the story of an old post.
    level: Mapped[str] = mapped_column(String(20))
    note: Mapped[str] = mapped_column(String(280), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    author: Mapped["User"] = relationship(back_populates="posts")


class PostInterest(Base):
    """A 'Join'/thumbs-up — someone signalling interest in another user's
    planned trip. Doubles as this app's version of a "like": there's no
    separate generic like button, since in a trip-planning feed "interested"
    already means the same thing a heart/thumbs-up would.
    """

    __tablename__ = "post_interest"
    __table_args__ = (UniqueConstraint("post_id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(String(280))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    author: Mapped["User"] = relationship()


def init_db() -> None:
    Base.metadata.create_all(engine)
