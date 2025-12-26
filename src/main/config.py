import os
from dataclasses import dataclass
from logging import getLogger

logger = getLogger(__name__)


class ConfigParseError(ValueError):
    pass


@dataclass
class WebConfig:
    login_url: str

    db_uri: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    # rabbitmq_host: str
    # rabbitmq_user: str
    # rabbitmq_password: str
    # rabbitmq_url: str
    #
    # redis_host: str
    # redis_url: str


def get_str_env(key) -> str:
    val = os.getenv(key)
    if not val:
        logger.error("%s is not set", key)
        raise ConfigParseError(f"{key} is not set")
    return val


def load_web_config():
    login_url = get_str_env('WEB_LOGIN_URL')

    # rabbitmq_host = get_str_env('RABBITMQ_HOST')
    # rabbitmq_user = get_str_env('RABBITMQ_USER')
    # rabbitmq_password = get_str_env('RABBITMQ_PASSWORD')
    # rabbitmq_url = f'amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}:5672//'
    #
    # redis_host = get_str_env("REDIS_HOST")
    # redis_url = f'redis://{redis_host}:6379/0'

    return WebConfig(
        login_url=login_url,
        db_uri=get_str_env('DB_URI'),
        secret_key=get_str_env('SECRET_KEY'),
        algorithm=get_str_env('ALGORITHM'),
        access_token_expire_minutes=int(get_str_env('ACCESS_TOKEN_EXPIRE_MINUTES')),
        refresh_token_expire_days=int(get_str_env('REFRESH_TOKEN_EXPIRE_DAYS')),
    )
