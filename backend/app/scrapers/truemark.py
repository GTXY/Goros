from app.scrapers.shopify_base import ShopifyBaseScraper

# TrueMark はオンラインショップを shop.yellow-eagle.net (Shopify) で運営している。
# メインサイト yellow-eagle.net は Wix だが、ショップ自体は別ドメインの Shopify ストア。


class TrueMarkScraper(ShopifyBaseScraper):
    source = "truemark"
    currency = "JPY"
    base_url = "https://shop.yellow-eagle.net"
    # 全商品が goro's なのでフィルタ不要
    title_filter: list[str] = []
