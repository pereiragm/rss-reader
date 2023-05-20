from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Feed, User
from app.schemas.user import UserCreate


def get_user(db: Session, uuid: UUID) -> User | None:
    return db.query(User).filter_by(uuid=uuid).one_or_none()


def create_user(db: Session, obj_in: UserCreate) -> User:
    db_obj = User(**obj_in.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
