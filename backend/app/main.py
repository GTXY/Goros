import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import init_db
from app.api.routes import products, scrape

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


def _scheduled_scrape():
    """定时抓取入口（在独立线程中运行，与手动触发共用同一个 _scrape_state 锁）。"""
    from app.api.routes.scrape import _run_all_scrapers, _scrape_state, _lock
    with _lock:
        if _scrape_state["running"]:
            logger.info("[调度器] 上次抓取仍在进行中，跳过本次定时任务")
            return
    logger.info("[调度器] 凌晨定时抓取启动")
    thread = threading.Thread(target=_run_all_scrapers, daemon=True)
    thread.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("数据库初始化完成")

    # 每天凌晨 3:00（本机时区）自动全量同步
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        _scheduled_scrape,
        CronTrigger(hour=3, minute=0),
        id="daily_scrape",
        replace_existing=True,
        misfire_grace_time=300,   # 最多允许延迟 5 分钟触发
    )
    scheduler.start()
    logger.info("定时任务已启动（每天 03:00 自动同步）")

    yield

    scheduler.shutdown(wait=False)
    logger.info("定时任务已停止")


app = FastAPI(
    title="Goros API",
    description="goro's 全渠道商品聚合 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api")
app.include_router(scrape.router, prefix="/api")

# 前端打包后静态托管（生产环境）
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
