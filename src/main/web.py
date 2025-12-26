import sys
import logging
from datetime import timedelta
from pathlib import Path
from typing import TypeVar, Callable

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# from adapters.auth.token import JwtTokenProcessor
from main.config import load_web_config
from main.ioc import IoC
from presentation.interactor_factory import InteractorFactory
from presentation.web_api.dependencies.config import WebViewConfig
from presentation.web_api.ui import router as ui_router

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,  # <-- this is key: overrides uvicorn’s defaults
)

class WebViewConfigProvider:
    def __init__(
            self,
            login_url: str,
            db_uri: str,
    ):
        self.login_url=login_url
        self.db_uri=db_uri

    async def __call__(self) -> WebViewConfig:
        return WebViewConfig(
            login_url=self.login_url,
            db_uri=self.db_uri,
        )


DependencyT = TypeVar("DependencyT")

def singleton(value: DependencyT) -> Callable[[], DependencyT]:
    """Produce save value as a fastapi dependency."""

    def singleton_factory() -> DependencyT:
        return value

    return singleton_factory


def create_app():
    app = FastAPI()

    web_config = load_web_config()

    ioc = IoC(
        db_uri=web_config.db_uri,
    )

    web_view_config_provider = WebViewConfigProvider(
        login_url=web_config.login_url,
        db_uri=web_config.db_uri,
    )

    # token_processor = JwtTokenProcessor(
    #     secret=web_config.secret_key,
    #     expires=timedelta(
    #         minutes=web_config.access_token_expire_minutes
    #     ),
    #     algorithm="HS256",
    # )


    app.dependency_overrides.update({
        InteractorFactory: singleton(ioc),
        WebViewConfig: web_view_config_provider,
        # JwtTokenProcessor: singleton(token_processor),
    })

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # static
    static_dir = Path(__file__).resolve().parents[1] / "presentation" / "web_api" / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # ui router
    app.include_router(ui_router)

    @app.get("/")
    @app.get("/health")
    async def health():
        return {"status": "UP"}

    return app

logger = logging.getLogger(__name__)
app = create_app()
logger.info("Started ehooo")
