"""Follow graph and planned-trip posts — the community feature's logic,
kept separate from the Streamlit rendering in streamlit_pages/community.py
and streamlit_pages/account.py so it can be tested without a running app.
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import delete, func, select

from db import Comment, Follow, Post, PostInterest, PostReaction, SessionLocal, User


def get_user(user_id: int) -> User | None:
    with SessionLocal() as session:
        return session.get(User, user_id)


def update_profile(
    user_id: int,
    display_name: str,
    home_city: str,
    surf_level: str,
    board_type: str | None = None,
) -> None:
    with SessionLocal() as session:
        user = session.get(User, user_id)
        user.display_name = display_name.strip()
        user.home_city = home_city
        user.surf_level = surf_level
        user.board_type = board_type
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
    author_id: int,
    spot_name: str,
    start_date: date,
    end_date: date,
    level: str,
    note: str,
    *,
    board_type: str | None = None,
    total_cost_eur: float | None = None,
    distance_km: float | None = None,
    nights: int | None = None,
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
                board_type=board_type,
                total_cost_eur=total_cost_eur,
                distance_km=distance_km,
                nights=nights,
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
    board_type: str | None = None
    total_cost_eur: float | None = None
    distance_km: float | None = None
    nights: int | None = None


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
                board_type=post.board_type,
                total_cost_eur=post.total_cost_eur,
                distance_km=post.distance_km,
                nights=post.nights,
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


def toggle_reaction(post_id: int, user_id: int, emoji: str) -> None:
    with SessionLocal() as session:
        existing = session.scalar(
            select(PostReaction).where(
                PostReaction.post_id == post_id,
                PostReaction.user_id == user_id,
                PostReaction.emoji == emoji,
            )
        )
        if existing:
            session.delete(existing)
        else:
            session.add(PostReaction(post_id=post_id, user_id=user_id, emoji=emoji))
        session.commit()


def reaction_summary(post_id: int, viewer_id: int) -> dict[str, tuple[int, bool]]:
    """Maps emoji -> (count, viewer_reacted) for all reactions on a post."""
    with SessionLocal() as session:
        rows = session.execute(
            select(PostReaction.emoji, PostReaction.user_id).where(PostReaction.post_id == post_id)
        ).all()
    summary: dict[str, tuple[int, bool]] = {}
    for emoji, user_id in rows:
        count, viewer_reacted = summary.get(emoji, (0, False))
        summary[emoji] = (count + 1, viewer_reacted or user_id == viewer_id)
    return summary


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
