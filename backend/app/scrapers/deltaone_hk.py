from app.scrapers.shopify_base import ShopifyBaseScraper


class DeltaOneHKScraper(ShopifyBaseScraper):
    source = "deltaone_hk"
    base_url = "https://deltaone.com.hk"
    currency = "HKD"
    # DeltaOne HK 专卖 goro's，无需关键词过滤
    title_filter = []
