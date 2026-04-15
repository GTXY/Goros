from app.scrapers.shopify_base import ShopifyBaseScraper


class DeltaOneJPScraper(ShopifyBaseScraper):
    source = "deltaone_jp"
    base_url = "https://www.deltaone.jp"
    currency = "JPY"
    # DeltaOne JP 专卖 goro's，无需关键词过滤
    title_filter = []
