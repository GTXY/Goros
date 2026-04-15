import json
import logging
from datetime import datetime

from app.scrapers.base import BaseScraper, random_delay, normalize_price_jpy, extract_category, extract_condition
from app.core.config import settings

logger = logging.getLogger(__name__)


class ShopifyBaseScraper(BaseScraper):
    """
    Shopify JSON API 通用爬虫基类。
    子类只需设置 base_url、currency、source，
    以及可选的 title_filter 关键词列表用于过滤非目标商品。
    """
    base_url: str = ""
    title_filter: list[str] = []   # 为空表示接收全部商品

    def _is_target(self, title: str, tags: list[str]) -> bool:
        if not self.title_filter:
            return True
        combined = (title + " " + " ".join(tags)).lower()
        return any(kw.lower() in combined for kw in self.title_filter)

    def _normalize(self, item: dict) -> dict | None:
        title = item.get("title", "")
        tags = [t.strip() for t in item.get("tags", [])]

        if not self._is_target(title, tags):
            return None

        variants = item.get("variants", [{}])
        variant = variants[0] if variants else {}
        price_raw = variant.get("price", "")
        available = any(v.get("available", False) for v in variants)

        images = [img["src"] for img in item.get("images", []) if img.get("src")]

        body_html = item.get("body_html") or ""
        description = body_html.replace("<br>", "\n").replace("<br/>", "\n")
        import re
        description = re.sub(r"<[^>]+>", "", description).strip()

        price_jpy = normalize_price_jpy(
            price_raw, self.currency,
            settings.RATE_USD_TO_JPY, settings.RATE_HKD_TO_JPY
        )

        # 货币符号拼接；价格为 0 时标注为 ASK（店家仅接受询价）
        currency_symbols = {"JPY": "¥", "USD": "$", "HKD": "HK$"}
        sym = currency_symbols.get(self.currency, "")
        try:
            price_val = float(price_raw) if price_raw else 0
        except (ValueError, TypeError):
            price_val = -1

        # 0、888888888（港台电商吉祥数占位符）、换算后超过 5 亿日元（明显虚假价格）
        is_ask = (
            price_val == 0
            or price_val == 888_888_888
            or (price_jpy is not None and price_jpy >= 500_000_000)
        )
        if is_ask:
            formatted = "ASK"
            price_jpy = None
        elif price_raw:
            try:
                formatted = f"{sym}{price_val:,.0f}"
            except Exception:
                formatted = f"{sym}{price_raw}"
        else:
            formatted = ""

        return {
            "source": self.source,
            "source_id": str(item.get("id", "")),
            "title": title,
            "price_raw": formatted,
            "price_jpy": price_jpy,
            "currency": self.currency,
            "condition": extract_condition(tags),
            "category": extract_category(tags, title),
            "images": json.dumps(images),
            "url": f"https://{self.base_url.rstrip('/').split('://')[-1].split('/')[0]}/products/{item.get('handle', '')}",
            "available": available,
            "tags": json.dumps(tags),
            "description": description,
            "scraped_at": datetime.utcnow(),
        }

    def fetch_products(self) -> list[dict]:
        results = []
        page = 1
        while True:
            url = f"{self.base_url}/products.json?limit=250&page={page}"
            logger.info(f"[{self.source_name}] 抓取第 {page} 页: {url}")
            resp = self.get(url)
            data = resp.json()
            products = data.get("products", [])
            if not products:
                break
            for item in products:
                normalized = self._normalize(item)
                if normalized:
                    results.append(normalized)
            if len(products) < 250:
                break
            page += 1
            random_delay()
        return results
