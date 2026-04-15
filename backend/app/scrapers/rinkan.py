import json
import logging
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.scrapers.base import BaseScraper, extract_category
from app.models.product import Product
from app.services.product_service import upsert_product, save_scrape_log

logger = logging.getLogger(__name__)

BASE_URL = "https://www.rinkan-goros.com"
LIST_URL = f"{BASE_URL}/shop/shopbrand.html"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

_COND_MAP = {
    "新品": "新品",
    "ほぼ新品": "ほぼ新品",
    "美品": "美品",
    "中古品": "中古",
    "中古": "中古",
    "アウトレット": "中古",
}


class RinkanScraper(BaseScraper):
    """
    RINKAN HARAJUKU SILVER ONLINE (rinkan-goros.com) スクレーパー。

    増分同期ロジック（run() をオーバーライド）:
      1. 全リストページからブランドコードを収集（= 現在在庫あり）
      2. DB の既存 source_id と差分を計算
      3. 差分（sold）→ available=False に更新（HTTP リクエスト不要）
      4. 新規ブランドコード → 詳細ページ取得・INSERT（リクエストは新品分のみ）
    """
    source = "rinkan"
    currency = "JPY"

    # fetch_products は run() のフォールバック用（単体テスト向け）
    def fetch_products(self) -> list[dict]:
        session = requests.Session()
        session.headers.update(HEADERS)
        brandcodes = self._collect_brandcodes(session)
        results = []
        for bc in brandcodes:
            try:
                p = self._fetch_detail(session, bc)
                if p:
                    results.append(p)
            except Exception as e:
                logger.warning(f"[RINKAN] 商品 {bc} 取得失敗: {e}")
            time.sleep(1.5)
        return results

    def run(self, db: Session) -> dict:
        """増分同期（在庫状態も同期）。base.run() をオーバーライド。"""
        started_at = datetime.utcnow()
        result = {
            "source": self.source,
            "name": self.source_name,
            "status": "failed",
            "count": 0,
            "error": None,
        }
        try:
            session = requests.Session()
            session.headers.update(HEADERS)

            # ---- Phase 1: 全リストページからブランドコード収集 ----
            live_ids = set(self._collect_brandcodes(session))
            logger.info(f"[RINKAN] 在庫ブランドコード数: {len(live_ids)}")

            # ---- Phase 2: DB の既存 source_id を取得 ----
            db_ids: set[str] = {
                row.source_id
                for row in db.query(Product.source_id)
                              .filter(Product.source == self.source)
                              .all()
            }

            # ---- Phase 3a: 消えたブランドコード → 売り切れに更新 ----
            sold_ids = db_ids - live_ids
            if sold_ids:
                db.query(Product).filter(
                    Product.source == self.source,
                    Product.source_id.in_(sold_ids),
                ).update(
                    {"available": False, "scraped_at": datetime.utcnow()},
                    synchronize_session=False,
                )
                logger.info(f"[RINKAN] 売り切れ更新: {len(sold_ids)} 件")

            # ---- Phase 3b: 新規ブランドコード → 詳細取得・INSERT ----
            new_ids = live_ids - db_ids
            logger.info(f"[RINKAN] 新規商品: {len(new_ids)} 件")

            new_count = 0
            for bc in new_ids:
                try:
                    product = self._fetch_detail(session, bc)
                    if product:
                        upsert_product(db, product)
                        new_count += 1
                except Exception as e:
                    logger.warning(f"[RINKAN] 商品 {bc} 取得失敗: {e}")
                time.sleep(1.5)

            db.commit()
            result["status"] = "success"
            result["count"] = new_count + len(sold_ids)
            logger.info(
                f"[RINKAN] 完了 — 新規: {new_count} 件, 売り切れ更新: {len(sold_ids)} 件"
            )

        except Exception as e:
            db.rollback()
            result["error"] = str(e)
            logger.error(f"[RINKAN] 取得エラー: {e}")
        finally:
            finished_at = datetime.utcnow()
            save_scrape_log(
                db,
                {
                    "source": self.source,
                    "status": result["status"],
                    "count": result["count"],
                    "error": result["error"],
                    "started_at": started_at,
                    "finished_at": finished_at,
                },
            )
        return result

    # ------------------------------------------------------------------ #
    #  内部ヘルパー                                                        #
    # ------------------------------------------------------------------ #

    def _collect_brandcodes(self, session: requests.Session) -> list[str]:
        """全リストページを巡回してブランドコードを収集する。"""
        brandcodes: list[str] = []
        seen: set[str] = set()

        for page_num in range(1, 50):
            url = f"{LIST_URL}?search=&page={page_num}"
            try:
                resp = session.get(url, timeout=15)
                resp.raise_for_status()
            except Exception as e:
                logger.warning(f"[RINKAN] リスト p{page_num} 取得失敗: {e}")
                break

            codes = re.findall(r"brandcode=(\d+)", resp.text)
            new_found = False
            for bc in codes:
                if bc not in seen:
                    seen.add(bc)
                    brandcodes.append(bc)
                    new_found = True

            if not new_found:
                break
            time.sleep(0.6)

        return brandcodes

    def _fetch_detail(self, session: requests.Session, brandcode: str) -> dict | None:
        """詳細ページから商品情報を取得する。"""
        url = f"{BASE_URL}/shop/shopdetail.html?brandcode={brandcode}&search=&sort="
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # タイトル
        h2 = soup.find("h2")
        title = h2.get_text(strip=True) if h2 else ""
        if not title:
            og = soup.find("meta", property="og:title")
            if og:
                title = re.sub(
                    r"\s*[-–]\s*(ゴローズ|RINKAN|goro).+$", "", og["content"], flags=re.I
                ).strip()
        if not title:
            return None

        # 価格
        price_jpy: int | None = None
        price_raw = ""
        for row in soup.find_all("tr"):
            text = row.get_text()
            m = re.search(r"価格\s*[:：]\s*([\d,]+)円", text)
            if m:
                price_jpy = int(m.group(1).replace(",", ""))
                price_raw = f"¥{m.group(1)}"
                break

        if price_jpy is None:
            return None

        # 画像（ロゴ・サムネ除外）
        images: list[str] = []
        for img in soup.find_all("img", src=re.compile(r"makeshop-multi-images.*shopimages")):
            src = img.get("src", "").split("?")[0]
            fname = src.rsplit("/", 1)[-1]
            if not re.match(r"^(logo|s\d+_)", fname, re.I) and src not in images:
                images.append(src)

        # 状態ランク（パンくずリストのリンクテキストから）
        cond_raw = ""
        for a in soup.find_all("a", href=True):
            txt = a.get_text(strip=True)
            if txt in _COND_MAP:
                cond_raw = _COND_MAP[txt]
                break
        condition = cond_raw or "中古"

        # 在庫状態
        sold_btn = soup.find("input", {"type": "submit", "value": re.compile(r"売り切れ|SOLD", re.I)})
        sold_text = soup.find(string=re.compile(r"^(売り切れ|SOLD\s*OUT)$", re.I))
        available = not bool(sold_btn or sold_text)

        # 商品説明
        description = self._extract_description(soup, title)

        tags = [condition] if condition != "不明" else []
        return {
            "source": self.source,
            "source_id": brandcode,
            "title": title,
            "price_raw": price_raw,
            "price_jpy": price_jpy,
            "currency": "JPY",
            "condition": condition,
            "category": extract_category(tags, title),
            "images": json.dumps(images[:8]),
            "url": url,
            "available": available,
            "tags": json.dumps(tags),
            "description": description,
            "scraped_at": datetime.utcnow(),
        }

    @staticmethod
    def _extract_description(soup: BeautifulSoup, title: str) -> str:
        body_text = soup.get_text("\n")
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]
        desc_lines: list[str] = []
        capturing = False
        for line in lines:
            if title in line and not capturing:
                capturing = True
                continue
            if capturing:
                if re.search(r"^(商品コード|価格|ポイント|数量|シェア)", line):
                    break
                if len(line) > 3:
                    desc_lines.append(line)
        return "\n".join(desc_lines[:12])
