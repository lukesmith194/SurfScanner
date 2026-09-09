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
    LargeBinary,
    String,
    UniqueConstraint,
    create_engine,
    func,
    text,
)
from sqlalchemy.exc import OperationalError, ProgrammingError
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
    # PNG bytes, resized to a small square thumbnail — stored in the
    # database rather than on disk, since the app's filesystem isn't
    # guaranteed to persist across restarts/redeploys (see the DATABASE_URL
    # note above; same reasoning applies to any uploaded file).
    avatar: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    # One of boards.BOARD_TYPES, or None if never set — used as the default
    # board type on the Trip Planner form once set here.
    board_type: Mapped[str | None] = mapped_column(String(30), nullable=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class RememberToken(Base):
    """A 'remember me' token — a random opaque value handed to the browser
    as a cookie, with only its hash stored here (same reason passwords are
    hashed: a leaked database row shouldn't hand over a usable credential).
    """

    __tablename__ = "remember_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


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
    # Optional snapshot of the Trip Planner recommendation this post was
    # shared from (None for posts created directly on Community, which never
    # had this data) — shown in the feed as extra detail beyond the note.
    board_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    total_cost_eur: Mapped[float | None] = mapped_column(nullable=True)
    distance_km: Mapped[float | None] = mapped_column(nullable=True)
    nights: Mapped[int | None] = mapped_column(nullable=True)

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


class PostReaction(Base):
    """An emoji reaction on a post — separate from PostInterest (the
    "I'm interested in joining this trip" signal), which stays a distinct,
    single-purpose action. A user can react to the same post with several
    different emoji, but not the same emoji twice.
    """

    __tablename__ = "post_reactions"
    __table_args__ = (UniqueConstraint("post_id", "user_id", "emoji"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    emoji: Mapped[str] = mapped_column(String(8))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


def init_db() -> None:
    Base.metadata.create_all(engine)
    _ensure_avatar_column()
    _ensure_board_type_column()
    _ensure_post_snapshot_columns()
    _ensure_rls_enabled()


def _ensure_avatar_column() -> None:
    """create_all() only creates missing tables, not missing columns on a
    table that already exists — and the production database already had a
    users table before `avatar` was added. No Alembic in this project, so:
    a one-off, idempotent ALTER TABLE, ignoring the "already exists" error
    on every run after the first.
    """
    column_type = "BYTEA" if not DATABASE_URL.startswith("sqlite") else "BLOB"
    with engine.connect() as conn:
        try:
            conn.execute(text(f"ALTER TABLE users ADD COLUMN avatar {column_type}"))
            conn.commit()
        except (OperationalError, ProgrammingError):
            conn.rollback()  # column already exists — fine


def _ensure_board_type_column() -> None:
    """Same idempotent-ALTER pattern as _ensure_avatar_column, for the
    board_type column added to an already-existing users table.
    """
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN board_type VARCHAR(30)"))
            conn.commit()
        except (OperationalError, ProgrammingError):
            conn.rollback()  # column already exists — fine


def _ensure_post_snapshot_columns() -> None:
    """Same idempotent-ALTER pattern, for the Trip Planner snapshot columns
    added to an already-existing posts table.
    """
    float_type = "DOUBLE PRECISION" if not DATABASE_URL.startswith("sqlite") else "FLOAT"
    columns = (
        ("board_type", "VARCHAR(30)"),
        ("total_cost_eur", float_type),
        ("distance_km", float_type),
        ("nights", "INTEGER"),
    )
    for column_name, column_type in columns:
        with engine.connect() as conn:
            try:
                conn.execute(text(f"ALTER TABLE posts ADD COLUMN {column_name} {column_type}"))
                conn.commit()
            except (OperationalError, ProgrammingError):
                conn.rollback()  # column already exists — fine


_RLS_TABLES = (
    "users",
    "follows",
    "posts",
    "post_interest",
    "comments",
    "remember_tokens",
    "post_reactions",
)


def _ensure_rls_enabled() -> None:
    """Supabase (and anything else fronted by PostgREST) auto-exposes every
    table in the public schema over a REST API using the project's anon key
    — regardless of whether the connecting app actually uses that API. This
    app never does; it talks to Postgres directly over the wire protocol via
    DATABASE_URL. Left as-is, that REST API sat open with no RLS, meaning
    anyone with the anon key could read users.password_hash and
    remember_tokens.token_hash straight from Supabase's dashboard/API.

    Enabling RLS with zero policies denies PostgREST's anon/authenticated
    roles entirely (default-deny with no policies), while leaving this
    app's own access untouched: Postgres never enforces RLS against a
    table's owner (the role DATABASE_URL connects as, since it's the one
    that created these tables) unless FORCE ROW LEVEL SECURITY is also set,
    which this deliberately does not do. A no-op on SQLite, where RLS/
    PostgREST don't apply.
    """
    if DATABASE_URL.startswith("sqlite"):
        return
    with engine.connect() as conn:
        for table in _RLS_TABLES:
            conn.execute(text(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY"))
        conn.commit()
