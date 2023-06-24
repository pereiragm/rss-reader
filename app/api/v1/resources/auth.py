from typing import Dict

from app.api.v1.resources.base import BaseResourceApiV1
from app.core.security import authenticate_user, create_access_token


class AuthenticationError(Exception):
    pass


class LoginResource(BaseResourceApiV1):
    def __init__(self, username, password, requested_scopes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.password = password
        self.requested_scopes = requested_scopes

    def authenticate(self) -> Dict:
        user = authenticate_user(self.db, self.username, self.password)
        if not user:
            raise AuthenticationError("Incorrect username or password.")
        access_token = create_access_token(
            data={"sub": user.username, "scopes": self.requested_scopes},
        )
        return {"access_token": access_token, "token_type": "Bearer"}
