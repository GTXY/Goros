from app.scrapers.shopify_base import ShopifyBaseScraper


class NativeFeatherScraper(ShopifyBaseScraper):
    source = "nativefeather"
    base_url = "https://nativefeather.jp"
    currency = "USD"
    # Native Feather 同时卖其他品牌，过滤只保留 goro's
    title_filter = ["Goros", "goro's", "Goro's"]
