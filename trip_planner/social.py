"""Follow graph and planned-trip posts — the community feature's logic,
kept separate from the Streamlit rendering in streamlit_pages/community.py
and streamlit_pages/account.py so it can be tested without a running app.
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import delete, func, select

from db import Comment, Follow, Post, PostInterest, SessionLocal, User


def get_user(user_id: int) -> User | None:
    with SessionLocal() as session:
        return session.get(User, user_id)


def update_profile(user_id: int, display_name: str, home_city: str, surf_level: str) -> None:
    with SessionLocal() as session:
        user = session.get(User, user_id)
        user.display_name = display_name.strip()
        user.home_city = home_city
        user.surf_level = surf_level
        session.commit()


def update_avatar(user_id: int, avatar_png: bytes | None) -> None:
    """avatar_png should already be a resized PNG (see account.py) — this
    just stores whatever bytes it's given.
    """
    with SessionLocal() as session:
        user = session.get(User, user_id)
        user.avatar = avatar_png
        session.commit()


def list_other_users(exclude_user_id: int) -> list[User]:
    with SessionLocal() as session:
        return list(
            session.scalars(
                select(User).where(User.id != exclude_user_id).order_by(User.display_name)
            )
        )


def following_ids(user_id: int) -> set[int]:
    with SessionLocal() as session:
        rows = session.scalars(select(Follow.followed_id).where(Follow.follower_id == user_id))
        return set(rows)


def follow(follower_id: int, followed_id: int) -> None:
    if follower_id == followed_id:
        return
    with SessionLocal() as session:
        exists = session.scalar(
            select(Follow).where(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
        )
        if not exists:
            session.add(Follow(follower_id=follower_id, followed_id=followed_id))
            session.commit()


def unfollow(follower_id: int, followed_id: int) -> None:
    with SessionLocal() as session:
        session.execute(
            delete(Follow).where(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
        )
        session.commit()


def create_post(
    author_id: int, spot_name: str, start_date: date, end_date: date, level: str, note: str
) -> None:
    with SessionLocal() as session:
        session.add(
            Post(
                author_id=author_id,
                spot_name=spot_name,
                start_date=start_date,
                end_date=end_date,
                level=level,
                note=note.strip()[:280],
            )
        )
        session.commit()


@dataclass
class FeedPost:
    post_id: int
    author_id: int
    author_name: str
    author_home_city: str
    spot_name: str
    start_date: date
    end_date: date
    level: str
    note: str
    interest_count: int
    viewer_is_interested: bool
    is_own_post: bool
    comment_count: int


def _enrich_posts(session, posts, viewer_id: int) -> list[FeedPost]:
    result = []
    for post in posts:
        interested_user_ids = set(
            session.scalars(select(PostInterest.user_id).where(PostInterest.post_id == post.id))
        )
        comment_count = session.scalar(
            select(func.count()).select_from(Comment).where(Comment.post_id == post.id)
        )
        result.append(
            FeedPost(
                post_id=post.id,
                author_id=post.author_id,
                author_name=post.author.display_name,
                author_home_city=post.author.home_city,
                spot_name=post.spot_name,
                start_date=post.start_date,
                end_date=post.end_date,
                level=post.level,
                note=post.note,
                interest_count=len(interested_user_ids),
                viewer_is_interested=viewer_id in interested_user_ids,
                is_own_post=post.author_id == viewer_id,
                comment_count=comment_count,
            )
        )
    return result


def feed_for(viewer_id: int) -> list[FeedPost]:
    """Posts by the viewer and everyone they follow, newest first."""
    with SessionLocal() as session:
        followed = set(session.scalars(select(Follow.followed_id).where(Follow.follower_id == viewer_id)))
        author_ids = followed | {viewer_id}
        posts = session.scalars(
            select(Post).where(Post.author_id.in_(author_ids)).order_by(Post.created_at.desc())
        ).all()
        return _enrich_posts(session, posts, viewer_id)


def posts_by_user(user_id: int) -> list[FeedPost]:
    """Just this user's own posts, newest first — for the Account 'My Trips' tab."""
    with SessionLocal() as session:
        posts = session.scalars(
            select(Post).where(Post.author_id == user_id).order_by(Post.created_at.desc())
        ).all()
        return _enrich_posts(session, posts, user_id)


def toggle_interest(post_id: int, user_id: int) -> None:
    with SessionLocal() as session:
        existing = session.scalar(
            select(PostInterest).where(PostInterest.post_id == post_id, PostInterest.user_id == user_id)
        )
        if existing:
            session.delete(existing)
        else:
            session.add(PostInterest(post_id=post_id, user_id=user_id))
        session.commit()


@dataclass
class CommentView:
    author_name: str
    body: str
    created_at: object


def comments_for(post_id: int) -> list[CommentView]:
    with SessionLocal() as session:
        comments = session.scalars(
            select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at)
        ).all()
        return [CommentView(c.author.display_name, c.body, c.created_at) for c in comments]


def add_comment(post_id: int, author_id: int, body: str) -> None:
    body = body.strip()[:280]
    if not body:
        return
    with SessionLocal() as session:
        session.add(Comment(post_id=post_id, author_id=author_id, body=body))
        session.commit()
