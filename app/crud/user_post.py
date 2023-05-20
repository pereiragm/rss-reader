from sqlalchemy.orm import Session

from app.models import Post, User


def mark_posts_as_read(db: Session, user: User, posts: list[Post]) -> None:
    for p in posts:
        user.read_posts.append(p)
    db.commit()
    db.refresh(user)


def mark_posts_as_unread(db: Session, user: User, posts: list[Post]) -> None:
    for p in posts:
        p.readers.remove(user)
    db.commit()
    db.refresh(user)
