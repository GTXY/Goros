from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)
    source_id = Column(String(200), nullable=False)
    title = Column(Text, nullable=False)
    price_raw = Column(String(100))
    price_jpy = Column(Integer, index=True)
    currency = Column(String(10), default="JPY")
    condition = Column(String(50), index=True)
    category = Column(String(50), index=True)
    images = Column(Text, default="[]")       # JSON array
    url = Column(Text)
    available = Column(Boolean, default=True, index=True)
    tags = Column(Text, default="[]")          # JSON array
    description = Column(Text)
    scraped_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_source_product"),
    )


class ScrapeLog(Base):
    __tablename__ = "scrape_logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50))
    status = Column(String(20))       # success / failed / skipped
    count = Column(Integer, default=0)
    error = Column(Text)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
