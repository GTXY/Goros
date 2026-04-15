import json
import logging
import re
import time
from datetime import datetime

from app.scrapers.base import BaseScraper, extract_category, extract_condition, normalize_price_jpy
from app.core.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://56s.jp"
# goro's カテゴリページ (category_id=38)
GOROS_LIST_URL = f"{BASE_URL}/products/list/38"

# goro's 商品を示すキーワード（TADY&KING 等を除外）
GOROS_KEYWORDS = ["goro", "ゴローズ", "goro's"]
EXCLUDE_BRANDS = ["TADY&KING", "タディアンドキング", "Chrome Hearts", "クロムハーツ",
                  "Supreme", "FIRST ARROW", "TENDERLOIN"]


class FiveSixScraper(BaseScraper):
    """
    66666 FiveSix (56s.jp) スクレーパー。
    EC-CUBE ベースのサイトで JS レンダリングが必要なため Playwright を使用。
    goro's カテゴリ (category_id=38) から商品を取得する。
    """
    source = "fivesix"
    currency = "JPY"

    def fetch_products(self) -> list[dict]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("[FiveSix] playwright がインストールされていません")
            return []

        results = []
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            try:
                product_urls = self._collect_product_urls(browser)
                logger.info(f"[FiveSix] 取得した商品URL数: {len(product_urls)}")
                for url in product_urls:
                    try:
                        product = self._fetch_detail(browser, url)
                        if product:
                            results.append(product)
                    except Exception as e:
                        logger.warning(f"[FiveSix] 商品 {url} 取得失敗: {e}")
                    time.sleep(1.0)
            finally:
                browser.close()
        return results

    def _collect_product_urls(self, browser) -> list[str]:
        """goro's カテゴリの全商品 URL を収集する。"""
        urls: list[str] = []
        seen: set[str] = set()
        page = browser.new_page()
        try:
            for page_num in range(1, 50):
                url = f"{GOROS_LIST_URL}?pageno={page_num}" if page_num > 1 else GOROS_LIST_URL
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(2)

                links: list[str] = page.eval_on_selector_all(
                    "a[href*='/products/detail']",
                    "els => [...new Set(els.map(e => e.href))]"
                )
                if not links:
                    break

                new_found = False
                for link in links:
                    if link not in seen:
                        seen.add(link)
                        urls.append(link)
                        new_found = True

                if not new_found:
                    break

                # ページネーション確認
                next_link = page.query_selector(f"a[href*='pageno={page_num + 1}']")
                if not next_link:
                    break
                time.sleep(1)
        finally:
            page.close()
        return urls

    def _fetch_detail(self, browser, detail_url: str) -> dict | None:
        """商品詳細ページから情報を取得する。"""
        image_urls: list[str] = []

        def _capture_image(response):
            url = response.url
            if "/html/upload/save_image/" in url:
                if url not in image_urls:
                    image_urls.append(url)

        page = browser.new_page()
        page.on("response", _capture_image)
        try:
            page.goto(detail_url, wait_until="domcontentloaded", timeout=20000)
            time.sleep(2)

            body = page.inner_text("body")
            lines = [l.strip() for l in body.split("\n") if l.strip()]

            # 価格行のインデックスを探す
            price_idx = -1
            price_jpy = None
            price_raw = ""
            for i, line in enumerate(lines):
                m = re.search(r'¥\s*([\d,]+)\s*税込', line)
                if m:
                    price_idx = i
                    price_jpy = int(m.group(1).replace(",", ""))
                    price_raw = f"¥{m.group(1)}"
                    break

            if price_idx < 0 or price_jpy is None:
                return None

            # タイトル: 価格行の1行前
            title = lines[price_idx - 1] if price_idx > 0 else ""

            # goro's 商品のみ対象
            combined = title + " " + " ".join(lines[max(0, price_idx - 5):price_idx + 5])
            if not any(kw.lower() in combined.lower() for kw in GOROS_KEYWORDS):
                return None
            if any(brand.lower() in combined.lower() for brand in EXCLUDE_BRANDS):
                return None

            # コンディション
            condition = "不明"
            for line in lines[price_idx:price_idx + 10]:
                if "状態" in line:
                    m_cond = re.search(r'状態\s*[:：]\s*(.+)', line)
                    if m_cond:
                        raw_cond = m_cond.group(1).strip()
                        if "新品" in raw_cond:
                            condition = "新品"
                        elif "美品" in raw_cond:
                            condition = "ほぼ新品"
                        elif "中古" in raw_cond:
                            condition = "中古"
                        break

            # 説明文
            desc_lines = []
            for line in lines[price_idx + 3:price_idx + 20]:
                if line and not re.search(r'カート|ウィッシュ|送料|返品|注文', line):
                    desc_lines.append(line)
            description = "\n".join(desc_lines[:10])

            # 在庫確認
            available = not any("売り切れ" in l or "SOLD OUT" in l.upper() for l in lines)

            # source_id: URL末尾の数字
            source_id = detail_url.rstrip("/").split("/")[-1]

            tags = [condition] if condition != "不明" else []
            return {
                "source": self.source,
                "source_id": source_id,
                "title": title,
                "price_raw": price_raw,
                "price_jpy": price_jpy,
                "currency": "JPY",
                "condition": condition,
                "category": extract_category(tags, title),
                "images": json.dumps(image_urls[:8]),
                "url": detail_url,
                "available": available,
                "tags": json.dumps(tags),
                "description": description,
                "scraped_at": datetime.utcnow(),
            }
        finally:
            page.close()
