from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict, field
from typing import Optional
import time
import random
import os
from config import BROWSER_UA, DEBUG_DIR


@dataclass
class BusinessListing:
    source: str
    title: str
    url: str
    listing_id: Optional[str] = None
    asking_price: Optional[str] = None
    revenue: Optional[str] = None
    cash_flow: Optional[str] = None
    ebitda: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    established: Optional[str] = None
    employees: Optional[str] = None
    image_url: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class BaseScraper(ABC):
    NAME = "Base"
    BASE_URL = ""

    def __init__(self, debug: bool = False):
        self.debug = debug

    def _sleep(self, min_s: float = 2.0, max_s: float = 4.5):
        time.sleep(random.uniform(min_s, max_s))

    def _save_debug(self, name: str, content: str):
        if not self.debug:
            return
        os.makedirs(DEBUG_DIR, exist_ok=True)
        path = os.path.join(DEBUG_DIR, f"{self.NAME.lower()}_{name}.html")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[{self.NAME}] Debug HTML saved to {path}")

    def _make_browser_context(self, playwright):
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=BROWSER_UA,
            viewport={"width": 1440, "height": 900},
            locale="en-US",
            timezone_id="Asia/Singapore",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        context.set_default_timeout(30000)
        return browser, context

    def _text(self, page_or_elem, selector: str, default: str = "") -> str:
        try:
            el = page_or_elem.query_selector(selector)
            return el.inner_text().strip() if el else default
        except Exception:
            return default

    def _attr(self, page_or_elem, selector: str, attr: str, default: str = "") -> str:
        try:
            el = page_or_elem.query_selector(selector)
            val = el.get_attribute(attr) if el else None
            return (val or default).strip()
        except Exception:
            return default

    def _first_text(self, elem, *selectors: str) -> str:
        for sel in selectors:
            val = self._text(elem, sel)
            if val:
                return val
        return ""

    @abstractmethod
    def scrape(self, max_pages: int = 5) -> list[BusinessListing]:
        pass
