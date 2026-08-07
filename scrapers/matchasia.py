"""
match.asia scraper — Singapore & SE Asia focused business marketplace.

match.asia is the most regionally relevant source. The scraper navigates
their search/listings page and extracts all business-for-sale listings.
If selectors break, run with debug=True to save raw HTML for inspection.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from .base import BaseScraper, BusinessListing

SEARCH_URLS = [
    "https://www.match.asia/businesses-for-sale",
    "https://www.match.asia/buy-a-business",
    "https://www.match.asia/listings",
]

CARD_SEL = (
    ".listing-card, .business-card, .listing-item, article.listing, "
    ".card[class*='listing'], .card[class*='business'], "
    "[class*='listing-card'], [class*='business-card']"
)
TITLE_SELS = ["h2", "h3", "h4", ".title", ".listing-title", ".business-name", "a.title"]
PRICE_SELS = [".price", ".asking-price", "[class*='price']", ".amount"]
REVENUE_SELS = [".revenue", ".turnover", "[class*='revenue']", "[class*='turnover']"]
CASHFLOW_SELS = [".profit", ".cash-flow", "[class*='profit']", "[class*='ebitda']"]
LOCATION_SELS = [".location", ".city", ".country", "[class*='location']", "[class*='city']"]
INDUSTRY_SELS = [".category", ".type", ".sector", "[class*='category']", "[class*='industry']"]
DESC_SELS = [".description", ".summary", ".excerpt", "p"]

FALLBACK_URLS = [
    "https://www.match.asia",
    "https://match.asia/businesses-for-sale",
    "https://match.asia/buy",
]


class MatchAsiaScraper(BaseScraper):
    NAME = "match.asia"
    BASE_URL = "https://www.match.asia"

    def _find_listings_page(self, page) -> bool:
        """Try multiple URL patterns to find the listings page."""
        for url in SEARCH_URLS + FALLBACK_URLS:
            try:
                print(f"[{self.NAME}] Trying {url}")
                resp = page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
                if resp and resp.status < 400:
                    cards = page.query_selector_all(CARD_SEL)
                    if cards:
                        print(f"[{self.NAME}] Found {len(cards)} cards at {url}")
                        return True
                    # Site loaded but no cards with known selectors — log and try next
                    self._save_debug("homepage", page.content())
            except PWTimeout:
                continue
        return False

    def scrape(self, max_pages: int = 5) -> list[BusinessListing]:
        results: list[BusinessListing] = []
        seen_urls: set[str] = set()

        with sync_playwright() as p:
            browser, context = self._make_browser_context(p)
            page = context.new_page()

            found = self._find_listings_page(page)
            if not found:
                print(
                    f"[{self.NAME}] Could not locate listing cards. "
                    "Run with debug=True and check data/debug/ for the raw HTML."
                )
                browser.close()
                return results

            for page_num in range(1, max_pages + 1):
                self._save_debug(f"p{page_num}", page.content())
                cards = page.query_selector_all(CARD_SEL)

                page_new = 0
                for card in cards:
                    link_el = card.query_selector("a[href]")
                    href = (link_el.get_attribute("href") if link_el else None) or ""
                    if not href:
                        href = card.get_attribute("href") or ""
                    if not href:
                        continue

                    full_url = href if href.startswith("http") else self.BASE_URL + href
                    if full_url in seen_urls:
                        continue
                    seen_urls.add(full_url)

                    title = self._first_text(card, *TITLE_SELS)
                    if not title and link_el:
                        title = (link_el.inner_text() or "").strip()
                    if not title:
                        continue

                    listing = BusinessListing(
                        source="matchasia",
                        title=title,
                        url=full_url,
                        asking_price=self._first_text(card, *PRICE_SELS),
                        revenue=self._first_text(card, *REVENUE_SELS),
                        cash_flow=self._first_text(card, *CASHFLOW_SELS),
                        location=self._first_text(card, *LOCATION_SELS) or "Singapore / SE Asia",
                        industry=self._first_text(card, *INDUSTRY_SELS),
                        description=self._first_text(card, *DESC_SELS),
                        image_url=self._attr(card, "img", "src"),
                    )
                    results.append(listing)
                    page_new += 1

                print(f"[{self.NAME}] Page {page_num}: {page_new} listings")
                if page_new == 0:
                    break

                next_btn = page.query_selector(
                    "a[rel='next'], .pagination a.next, a[aria-label='Next page'], "
                    "button[aria-label='Next'], .next-page a"
                )
                if not next_btn:
                    break
                next_btn.click()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2500)
                self._sleep(1.5, 3)

            browser.close()

        print(f"[{self.NAME}] Total: {len(results)} listings")
        return results
