import threading
import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.scrapers import ALL_SCRAPERS
from app.schemas.product import ScrapeStatusResponse, ScrapeResult

router = APIRouter(prefix="/scrape", tags=["scrape"])
logger = logging.getLogger(__name__)

# 全局抓取状态（进程内共享）
_scrape_state: dict = {
    "running": False,
    "started_at": None,
    "finished_at": None,
    "total_sources": len(ALL_SCRAPERS),
    "completed_sources": 0,
    "results": [],
}
_lock = threading.Lock()


def _run_all_scrapers():
    db: Session = SessionLocal()
    with _lock:
        _scrape_state["running"] = True
        _scrape_state["started_at"] = datetime.utcnow()
        _scrape_state["finished_at"] = None
        _scrape_state["completed_sources"] = 0
        _scrape_state["results"] = []

    try:
        for ScraperClass in ALL_SCRAPERS:
            scraper = ScraperClass()
            result = scraper.run(db)
            with _lock:
                _scrape_state["results"].append(result)
                _scrape_state["completed_sources"] += 1
    except Exception as e:
        logger.error(f"全量抓取异常: {e}")
    finally:
        db.close()
        with _lock:
            _scrape_state["running"] = False
            _scrape_state["finished_at"] = datetime.utcnow()


@router.post("/all")
def trigger_scrape():
    with _lock:
        if _scrape_state["running"]:
            return {"message": "抓取已在进行中", "running": True}

    thread = threading.Thread(target=_run_all_scrapers, daemon=True)
    thread.start()
    return {"message": "抓取已启动", "running": True}


@router.get("/status", response_model=ScrapeStatusResponse)
def get_scrape_status():
    with _lock:
        state = dict(_scrape_state)
    return ScrapeStatusResponse(
        running=state["running"],
        started_at=state.get("started_at"),
        finished_at=state.get("finished_at"),
        total_sources=state["total_sources"],
        completed_sources=state["completed_sources"],
        results=[ScrapeResult(**r) for r in state["results"]],
    )
