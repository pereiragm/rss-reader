from typing import Optional

from pydantic import BaseModel, EmailStr, UUID4

"""
id = Column(Integer, primary_key=True, index=True)
full_name = Column(String, index=True)
email = Column(String, unique=True, index=True, nullable=False)
hashed_password = Column(String, nullable=False)
is_active = Column(Boolean(), default=True)
is_superuser = Column(Boolean(), default=False)
items = relationship("Item", back_populates="owner")
"""


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    uuid: Optional[UUID4] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserInDBBase(UserBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
