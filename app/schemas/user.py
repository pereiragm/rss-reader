from typing import Optional

from pydantic import BaseModel, EmailStr, UUID4


"""
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    feeds = relationship("Feed", secondary=user_feed, backref="followers")
"""
# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    uuid: Optional[UUID4] = None
    # is_active: Optional[bool] = True
    # is_superuser: bool = False
    name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    # password: str


class UserInDBBase(UserBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
