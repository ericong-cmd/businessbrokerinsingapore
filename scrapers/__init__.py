from .bizbuysell import BizBuySellScraper
from .businessesforsale import BusinessesForSaleScraper
from .matchasia import MatchAsiaScraper
from .acquire import AcquireScraper

SCRAPER_MAP = {
    'bizbuysell': BizBuySellScraper,
    'businessesforsale': BusinessesForSaleScraper,
    'matchasia': MatchAsiaScraper,
    'acquire': AcquireScraper,
}

__all__ = [
    'BizBuySellScraper',
    'BusinessesForSaleScraper',
    'MatchAsiaScraper',
    'AcquireScraper',
    'SCRAPER_MAP',
]
