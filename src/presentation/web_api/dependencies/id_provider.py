from fastapi import Request, Depends
from typing_extensions import Annotated

from adapters.auth.telegram_auth import TelegramAuthenticator, TelegramAuthIdProvider
from adapters.auth.token import JwtTokenProcessor, TokenIdProvider
from application.common.id_provider import IdProvider
from presentation.web_api.dependencies.depends_stub import Stub

async def token_from_cookie(request: Request) -> str | None:
    return request.cookies.get("token")

def token_id_provider(
        token_processor: Annotated[JwtTokenProcessor, Depends(Stub(JwtTokenProcessor))],
        token: Annotated[str | None, Depends(token_from_cookie)],
) -> IdProvider:
    return TokenIdProvider(
        token_processor=token_processor,
        token=token,
    )
