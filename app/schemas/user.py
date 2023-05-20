from typing import Optional

from pydantic import BaseModel, EmailStr, UUID4


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    uuid: Optional[UUID4] = None
    name: Optional[str] = None


class UserCreate(BaseModel):
    uuid: Optional[UUID4]
    name: Optional[str] = None
    email: EmailStr
