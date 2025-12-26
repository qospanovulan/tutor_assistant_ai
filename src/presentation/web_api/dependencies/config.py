from dataclasses import dataclass


@dataclass
class WebViewConfig:
    login_url: str
    db_uri: str
