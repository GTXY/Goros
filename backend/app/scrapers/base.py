import json
import logging
import time
import random
from datetime import datetime
from abc import ABC, abstractmethod

import requests
from sqlalchemy.orm import Session

from app.core.config import settings, SOURCES
from app.services.product_service import upsert_product, save_scrape_log

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def random_delay():
    time.sleep(random.uniform(settings.REQUEST_DELAY_MIN, settings.REQUEST_DELAY_MAX))


def normalize_price_jpy(price_raw: str | None, currency: str, rate_usd: float, rate_hkd: float) -> int | None:
    if not price_raw:
        return None
    cleaned = price_raw.replace(",", "").replace("¥", "").replace("$", "").replace("HK", "").strip()
    try:
        amount = float(cleaned)
    except ValueError:
        return None
    if currency == "JPY":
        return int(amount)
    elif currency == "USD":
        return int(amount * rate_usd)
    elif currency == "HKD":
        return int(amount * rate_hkd)
    return int(amount)


def extract_category(tags: list[str], title: str) -> str:
    combined = " ".join(tags) + " " + title
    if "フェザー" in combined or "feather" in combined.lower():
        return "フェザー"
    if "イーグル" in combined or "eagle" in combined.lower():
        return "イーグル"
    if "リング" in combined or "ring" in combined.lower():
        return "リング"
    if "ブレス" in combined or "bracelet" in combined.lower():
        return "ブレス"
    if "チェーン" in combined or "ホイール" in combined or "chain" in combined.lower() or "wheel" in combined.lower():
        return "チェーン/ホイール"
    if "メタル" in combined or "metal" in combined.lower():
        return "メタル"
    if "レザー" in combined or "財布" in combined or "leather" in combined.lower() or "wallet" in combined.lower():
        return "レザー"
    return "その他"


def extract_condition(tags: list[str]) -> str:
    priority = ["新品", "ほぼ新品", "超美品", "美品", "美中古", "中古"]
    tag_set = set(tags)
    for c in priority:
        if c in tag_set:
            return c
    for tag in tags:
        tl = tag.lower()
        if "新品" in tag:
            return "新品"
        if "美中古" in tag:
            return "美中古"
        if "中古" in tag or "used" in tl:
            return "中古"
    return "不明"


class BaseScraper(ABC):
    source: str = ""
    currency: str = "JPY"

    @property
    def source_name(self) -> str:
        return SOURCES.get(self.source, self.source)

    def get(self, url: str, **kwargs) -> requests.Response:
        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=settings.REQUEST_TIMEOUT,
            **kwargs,
        )
        resp.raise_for_status()
        return resp

    @abstractmethod
    def fetch_products(self) -> list[dict]:
        """各站点抓取逻辑，返回标准化后的 product dict 列表"""
        ...

    def run(self, db: Session) -> dict:
        started_at = datetime.utcnow()
        result = {
            "source": self.source,
            "name": self.source_name,
            "status": "failed",
            "count": 0,
            "error": None,
        }
        try:
            logger.info(f"[{self.source_name}] 开始抓取...")
            products = self.fetch_products()
            count = 0
            for p in products:
                try:
                    upsert_product(db, p)
                    count += 1
                except Exception as e:
                    logger.warning(f"[{self.source_name}] upsert 失败: {e}")
            db.commit()
            result["status"] = "success"
            result["count"] = count
            logger.info(f"[{self.source_name}] 抓取完成，共 {count} 件")
        except Exception as e:
            db.rollback()
            result["error"] = str(e)
            logger.error(f"[{self.source_name}] 抓取失败: {e}")
        finally:
            finished_at = datetime.utcnow()
            save_scrape_log(db, {
                "source": self.source,
                "status": result["status"],
                "count": result["count"],
                "error": result["error"],
                "started_at": started_at,
                "finished_at": finished_at,
            })
        return result
