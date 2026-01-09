from fastapi import Depends, Request
from typing_extensions import Annotated

from adapters.auth.session import SessionIdProvider
from adapters.auth.token import JwtTokenProcessor, TokenIdProvider
from adapters.database.session_db import SessionGateway
from application.common.id_provider import IdProvider
from presentation.web_api.dependencies.depends_stub import Stub


async def token_from_cookie(request: Request) -> str | None:
    return request.cookies.get("token")


async def session_key_from_cookie(request: Request) -> str | None:
    return request.cookies.get("session_key")


def token_id_provider(
    token_processor: Annotated[JwtTokenProcessor, Depends(Stub(JwtTokenProcessor))],
    token: Annotated[str | None, Depends(token_from_cookie)],
) -> IdProvider:
    return TokenIdProvider(
        token_processor=token_processor,
        token=token,
    )


def session_id_provider(
    session_gateway: Annotated[SessionGateway, Depends(Stub(SessionGateway))],
    session_key: Annotated[str | None, Depends(session_key_from_cookie)],
) -> IdProvider:
    return SessionIdProvider(
        session_gateway=session_gateway,
        session_key=session_key,
    )
