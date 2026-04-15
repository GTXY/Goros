from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/goros.db"

    RATE_USD_TO_JPY: float = 150.0
    RATE_HKD_TO_JPY: float = 19.5

    SCRAPE_CRON_HOUR: int = 3
    SCRAPE_CRON_MINUTE: int = 0

    REQUEST_DELAY_MIN: float = 3.0
    REQUEST_DELAY_MAX: float = 8.0
    REQUEST_TIMEOUT: int = 30

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


settings = Settings()

SOURCES = {
    "deltaone_jp": "DeltaOne JP",
    "deltaone_hk": "DeltaOne HK",
    "corner": "Corner",
    "nativefeather": "Native Feather",
    "truemark": "TrueMark",
    "fivesix": "FiveSix",
    "rinkan": "RINKAN",
}

CONDITION_ORDER = ["新品", "ほぼ新品", "超美品", "美品", "美中古", "中古", "不明"]

CATEGORIES = ["フェザー", "イーグル", "メタル", "リング", "ブレス", "チェーン/ホイール", "レザー", "その他"]
