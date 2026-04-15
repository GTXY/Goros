from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, Integer, cast
from app.models.product import Product, ScrapeLog
from app.core.config import SOURCES
import json


def get_products(
    db: Session,
    page: int = 1,
    limit: int = 24,
    sources: list[str] | None = None,
    conditions: list[str] | None = None,
    categories: list[str] | None = None,
    in_stock: bool | None = True,
    sort: str = "scraped_at_desc",
    q: str | None = None,
):
    query = db.query(Product)

    if sources:
        query = query.filter(Product.source.in_(sources))
    if conditions:
        query = query.filter(Product.condition.in_(conditions))
    if categories:
        query = query.filter(Product.category.in_(categories))
    if in_stock is not None:
        query = query.filter(Product.available == in_stock)
    if q:
        query = query.filter(Product.title.ilike(f"%{q}%"))

    sort_map = {
        "price_asc": Product.price_jpy.asc().nullslast(),
        "price_desc": Product.price_jpy.desc().nullslast(),
        "scraped_at_desc": Product.scraped_at.desc().nullslast(),
        "created_at_desc": Product.created_at.desc().nullslast(),
    }
    order = sort_map.get(sort, Product.scraped_at.desc().nullslast())
    query = query.order_by(order)

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    pages = max(1, (total + limit - 1) // limit)

    return items, total, pages


def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def upsert_product(db: Session, data: dict) -> Product:
    existing = (
        db.query(Product)
        .filter(
            Product.source == data["source"],
            Product.source_id == data["source_id"],
        )
        .first()
    )
    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        db.flush()
        return existing
    else:
        product = Product(**data)
        db.add(product)
        db.flush()
        return product


def get_stats(db: Session) -> dict:
    total = db.query(func.count(Product.id)).scalar()
    available = db.query(func.count(Product.id)).filter(Product.available == True).scalar()

    source_rows = (
        db.query(
            Product.source,
            func.count(Product.id).label("count"),
            func.sum(cast(Product.available, Integer)).label("available_count"),
            func.max(Product.scraped_at).label("last_scraped"),
        )
        .group_by(Product.source)
        .all()
    )

    sources = [
        {
            "source": row.source,
            "name": SOURCES.get(row.source, row.source),
            "count": row.count,
            "available_count": int(row.available_count or 0),
            "last_scraped": row.last_scraped,
        }
        for row in source_rows
    ]

    cat_rows = (
        db.query(Product.category, func.count(Product.id).label("count"))
        .filter(Product.category.isnot(None))
        .group_by(Product.category)
        .order_by(func.count(Product.id).desc())
        .all()
    )
    categories = [{"name": r.category, "count": r.count} for r in cat_rows]

    last_log = (
        db.query(ScrapeLog.finished_at)
        .order_by(ScrapeLog.finished_at.desc())
        .first()
    )

    return {
        "total_products": total or 0,
        "available_products": available or 0,
        "sources": sources,
        "categories": categories,
        "last_scrape": last_log.finished_at if last_log else None,
    }


def get_all_categories(db: Session) -> list[str]:
    rows = (
        db.query(Product.category)
        .filter(Product.category.isnot(None))
        .distinct()
        .all()
    )
    return [r.category for r in rows if r.category]


def save_scrape_log(db: Session, log_data: dict):
    log = ScrapeLog(**log_data)
    db.add(log)
    db.commit()
