from sqlalchemy.orm import Session

from app.models import Feed, User


def subscribe_user_to_feeds(db: Session, user: User, feeds: list[Feed]) -> None:
    for f in feeds:
        user.feeds.append(f)
    db.commit()
    db.refresh(user)
