"""Password hashing and account creation/login — stdlib only, no auth
service dependency, matching this MVP's self-contained approach elsewhere.

PBKDF2-HMAC-SHA256 with a random salt and 260,000 iterations (Django's
current default) is a reasonable, well-understood choice without pulling in
bcrypt/argon2 as an extra dependency for what's still a local MVP.
"""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import delete, select

from db import RememberToken, SessionLocal, User

PBKDF2_ITERATIONS = 260_000
REMEMBER_TOKEN_DAYS = 30


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS
    ).hex()


def make_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    return f"{salt}${_hash_password(password, salt)}"


def verify_password(password: str, stored_hash: str) -> bool:
    salt, _, expected = stored_hash.partition("$")
    if not salt or not expected:
        return False
    return secrets.compare_digest(_hash_password(password, salt), expected)


@dataclass
class AuthResult:
    ok: bool
    error: str | None = None
    user_id: int | None = None


def sign_up(email: str, password: str, display_name: str, home_city: str, surf_level: str) -> AuthResult:
    email = email.strip().lower()
    if not email or "@" not in email:
        return AuthResult(ok=False, error="Enter a valid email address.")
    if len(password) < 8:
        return AuthResult(ok=False, error="Password must be at least 8 characters.")
    if not display_name.strip():
        return AuthResult(ok=False, error="Enter a display name.")

    with SessionLocal() as session:
        existing = session.scalar(select(User).where(User.email == email))
        if existing:
            return AuthResult(ok=False, error="An account with that email already exists.")

        user = User(
            email=email,
            password_hash=make_password_hash(password),
            display_name=display_name.strip(),
            home_city=home_city,
            surf_level=surf_level,
        )
        session.add(user)
        session.commit()
        return AuthResult(ok=True, user_id=user.id)


def log_in(email: str, password: str) -> AuthResult:
    email = email.strip().lower()
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        if not user or not verify_password(password, user.password_hash):
            return AuthResult(ok=False, error="Incorrect email or password.")
        return AuthResult(ok=True, user_id=user.id)


def get_user_id_by_email(email: str) -> int | None:
    """No password check — dev-only lookup for auto-logging in the seeded
    test account when running the app locally. See main.py.
    """
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email.strip().lower()))
        return user.id if user else None


def change_password(user_id: int, current_password: str, new_password: str) -> AuthResult:
    if len(new_password) < 8:
        return AuthResult(ok=False, error="New password must be at least 8 characters.")
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if not verify_password(current_password, user.password_hash):
            return AuthResult(ok=False, error="Current password is incorrect.")
        user.password_hash = make_password_hash(new_password)
        session.commit()
        return AuthResult(ok=True, user_id=user_id)


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def create_remember_token(user_id: int) -> str:
    """A high-entropy random token for a 'remember me' cookie. Only its hash
    is stored — same rationale as password hashing, so a leaked database
    can't be replayed as a working login cookie.
    """
    raw_token = secrets.token_urlsafe(32)
    with SessionLocal() as session:
        session.add(
            RememberToken(
                user_id=user_id,
                token_hash=_hash_token(raw_token),
                expires_at=datetime.utcnow() + timedelta(days=REMEMBER_TOKEN_DAYS),
            )
        )
        session.commit()
    return raw_token


def verify_remember_token(raw_token: str) -> int | None:
    if not raw_token:
        return None
    with SessionLocal() as session:
        token = session.scalar(
            select(RememberToken).where(RememberToken.token_hash == _hash_token(raw_token))
        )
        if not token or token.expires_at < datetime.utcnow():
            return None
        return token.user_id


def revoke_remember_token(raw_token: str) -> None:
    if not raw_token:
        return
    with SessionLocal() as session:
        session.execute(delete(RememberToken).where(RememberToken.token_hash == _hash_token(raw_token)))
        session.commit()
