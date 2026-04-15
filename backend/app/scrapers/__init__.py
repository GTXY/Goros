from app.scrapers.deltaone_jp import DeltaOneJPScraper
from app.scrapers.deltaone_hk import DeltaOneHKScraper
from app.scrapers.corner import CornerScraper
from app.scrapers.nativefeather import NativeFeatherScraper
from app.scrapers.truemark import TrueMarkScraper
from app.scrapers.fivesix import FiveSixScraper
from app.scrapers.rinkan import RinkanScraper

ALL_SCRAPERS = [
    DeltaOneJPScraper,
    DeltaOneHKScraper,
    CornerScraper,
    NativeFeatherScraper,
    TrueMarkScraper,
    FiveSixScraper,
    RinkanScraper,
]
