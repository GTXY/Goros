from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import SOURCES
from app.schemas.product import ProductListResponse, ProductOut, StatsResponse
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])

# 汇率缓存（24小时更新一次）
_rates_cache: dict = {"data": None, "expires": datetime.utcnow()}


@router.get("/rates")
async def get_exchange_rates():
    """从 Frankfurter（欧洲央行，免费无 key）获取实时汇率并缓存 24 小时。"""
    global _rates_cache
    now = datetime.utcnow()
    if _rates_cache["data"] and _rates_cache["expires"] > now:
        return _rates_cache["data"]
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                "https://api.frankfurter.app/latest",
                params={"from": "JPY", "to": "CNY,USD,HKD"},
            )
            resp.raise_for_status()
            raw = resp.json()
        data = {
            "JPY_TO_CNY": raw["rates"]["CNY"],
            "JPY_TO_USD": raw["rates"]["USD"],
            "JPY_TO_HKD": raw["rates"]["HKD"],
            "date": raw["date"],
        }
    except Exception:
        # 降级到固定汇率（约 2026 年均值）
        data = {
            "JPY_TO_CNY": 0.0474,
            "JPY_TO_USD": 0.0067,
            "JPY_TO_HKD": 0.054,
            "date": "fallback",
        }
    _rates_cache = {"data": data, "expires": now + timedelta(hours=24)}
    return data


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    source: str | None = Query(None, description="逗号分隔的来源列表"),
    condition: str | None = Query(None, description="逗号分隔的成色列表"),
    category: str | None = Query(None, description="逗号分隔的品类列表"),
    in_stock: bool | None = Query(True),
    sort: str = Query("scraped_at_desc"),
    q: str | None = Query(None),
    db: Session = Depends(get_db),
):
    sources = [s.strip() for s in source.split(",")] if source else None
    conditions = [c.strip() for c in condition.split(",")] if condition else None
    categories = [c.strip() for c in category.split(",")] if category else None

    items, total, pages = product_service.get_products(
        db, page, limit, sources, conditions, categories, in_stock, sort, q
    )

    products = []
    for item in items:
        p = ProductOut.model_validate(item)
        p.source_name = SOURCES.get(item.source, item.source)
        products.append(p)

    return ProductListResponse(products=products, total=total, page=page, limit=limit, pages=pages)


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    return product_service.get_stats(db)


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    cats = product_service.get_all_categories(db)
    return {"categories": cats}


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    p = ProductOut.model_validate(product)
    p.source_name = SOURCES.get(product.source, product.source)
    return p
