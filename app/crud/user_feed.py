from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Feed


def subscribe_user_to_feeds(db: Session, user: User, uuids: set(UUID)) -> list[Feed]:
    pass