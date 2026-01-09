from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal

from jose import JWTError, jwt

from application.common.id_provider import IdProvider
from domain.exceptions.auth import AuthenticationError
from domain.models.user_id import UserId

Algorithm = Literal[
    "HS256", "HS384", "HS512",
    "RS256", "RS384", "RS512",
]


class JwtTokenProcessor:
    def __init__(
        self,
        secret: str,
        expires: timedelta,
        algorithm: Algorithm,
    ):
        self.secret = secret
        self.expires = expires
        self.algorithm = algorithm

    def create_access_token(
        self,
        user_id: UserId,
    ) -> str:
        to_encode = {"sub": str(int(user_id))}
        expire = datetime.utcnow() + self.expires
        to_encode["exp"] = expire
        return jwt.encode(
            to_encode, self.secret, algorithm=self.algorithm,
        )

    def validate_token(self, token: str) -> UserId:
        try:
            payload = jwt.decode(
                token, self.secret, algorithms=[self.algorithm],
            )
        except JWTError as exc:
            raise AuthenticationError("Invalid token.") from exc

        try:
            return UserId(int(payload["sub"]))
        except (KeyError, ValueError) as exc:
            raise AuthenticationError("Invalid token payload.") from exc


class TokenIdProvider(IdProvider):
    def __init__(
        self,
        token_processor: JwtTokenProcessor,
        token: str | None,
    ):
        self.token_processor = token_processor
        self.token = token

    def get_current_user_id(self) -> UserId:
        if not self.token:
            raise AuthenticationError("Missing token.")
        return self.token_processor.validate_token(self.token)
