from datetime import timedelta
from typing import Annotated

from fastapi.security import SecurityScopes
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.crud_user import get_user_by_email
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SCOPES = {
    "admin:all": "Do all available operations",
    "user:read": "Read information from a resource",
    "user:write": "Create a resource",
}


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_email(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expiration: int | None = None) -> str:
    to_encode = data.copy()
    exp = expiration or timedelta(minutes=settings.JWT_EXPIRATION)
    to_encode.update({"exp": exp})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY,
                             algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
        security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user
