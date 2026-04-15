"""
独立定时任务进程。
与 uvicorn 分开运行：python scheduler.py
"""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.scrapers import ALL_SCRAPERS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_all():
    logger.info("定时抓取任务开始...")
    init_db()
    db = SessionLocal()
    try:
        for ScraperClass in ALL_SCRAPERS:
            scraper = ScraperClass()
            result = scraper.run(db)
            logger.info(f"[{result['name']}] {result['status']} — {result['count']} 件")
    finally:
        db.close()
    logger.info("定时抓取任务完成")


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Asia/Tokyo")
    scheduler.add_job(
        run_all,
        CronTrigger(
            hour=settings.SCRAPE_CRON_HOUR,
            minute=settings.SCRAPE_CRON_MINUTE,
        ),
        id="daily_scrape",
        name="每日 goro's 全站抓取",
    )
    logger.info(
        f"调度器已启动，每天 {settings.SCRAPE_CRON_HOUR:02d}:{settings.SCRAPE_CRON_MINUTE:02d} (JST) 执行抓取"
    )
    scheduler.start()
