from uuid import UUID

from sqlalchemy.orm import Session

from app.crud.crud_user import get_user


class BaseResourceApiV1:
    def __init__(self, db: Session, user_uuid: UUID):
        self.db = db
        self.user_uuid = user_uuid
        self.user = get_user(self.db, self.user_uuid)
