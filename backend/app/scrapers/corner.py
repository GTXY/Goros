from app.scrapers.shopify_base import ShopifyBaseScraper


class CornerScraper(ShopifyBaseScraper):
    source = "corner"
    base_url = "https://corneronline.store"
    currency = "JPY"
    # Corner 同时卖 Chrome Hearts，过滤只保留 goro's 商品
    title_filter = ["ゴローズ", "goro's", "goros", "goroz"]
