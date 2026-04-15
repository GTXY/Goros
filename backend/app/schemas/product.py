from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
import json


class ProductOut(BaseModel):
    id: int
    source: str
    source_name: str = ""
    source_id: str
    title: str
    price_raw: Optional[str] = None
    price_jpy: Optional[int] = None
    currency: str = "JPY"
    condition: Optional[str] = None
    category: Optional[str] = None
    images: list[str] = []
    url: Optional[str] = None
    available: bool = True
    tags: list[str] = []
    description: Optional[str] = None
    scraped_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @field_validator("images", "tags", mode="before")
    @classmethod
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: list[ProductOut]
    total: int
    page: int
    limit: int
    pages: int


class SourceStats(BaseModel):
    source: str
    name: str
    count: int
    available_count: int
    last_scraped: Optional[datetime] = None


class CategoryStats(BaseModel):
    name: str
    count: int


class StatsResponse(BaseModel):
    total_products: int
    available_products: int
    sources: list[SourceStats]
    categories: list[CategoryStats]
    last_scrape: Optional[datetime] = None


class ScrapeResult(BaseModel):
    source: str
    name: str
    status: str        # success / failed / skipped
    count: int = 0
    error: Optional[str] = None


class ScrapeStatusResponse(BaseModel):
    running: bool
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    total_sources: int = 7
    completed_sources: int = 0
    results: list[ScrapeResult] = []
