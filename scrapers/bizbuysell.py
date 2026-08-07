"""
BizBuySell scraper — searches for Singapore / Asia-Pacific listings.

Selectors target the listing cards rendered at /businesses-for-sale/.
If the site updates its markup, adjust CARD_SEL and the field selectors below.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from .base import BaseScraper, BusinessListing

SEARCH_URLS = [
    "https://www.bizbuysell.com/businesses-for-sale/?q=Singapore",
    "https://www.bizbuysell.com/businesses-for-sale/?q=Malaysia",
    "https://www.bizbuysell.com/businesses-for-sale/?q=Asia+Pacific",
]

CARD_SEL = "a.listing-card, div.listing-card, li.listing-card, .bfsListingCard"
TITLE_SELS = [".listing-card__title", "h3", "h2", ".title"]
PRICE_SELS = [".listing-card__asking-price", ".asking-price", "[data-asking-price]", ".price"]
REVENUE_SELS = [".listing-card__revenue", ".revenue", "[data-revenue]"]
CASHFLOW_SELS = [".listing-card__cash-flow", ".cash-flow", "[data-cashflow]"]
LOCATION_SELS = [".listing-card__location", ".location", ".city-state", ".geo"]
INDUSTRY_SELS = [".listing-card__category", ".category", ".industry", ".type"]


class BizBuySellScraper(BaseScraper):
    NAME = "BizBuySell"
    BASE_URL = "https://www.bizbuysell.com"

    def scrape(self, max_pages: int = 5) -> list[BusinessListing]:
        results: list[BusinessListing] = []
        seen_urls: set[str] = set()

        with sync_playwright() as p:
            browser, context = self._make_browser_context(p)
            page = context.new_page()

            for base_url in SEARCH_URLS:
                for page_num in range(1, max_pages + 1):
                    url = base_url if page_num == 1 else f"{base_url}&page={page_num}"
                    print(f"[{self.NAME}] Fetching: {url}")
                    try:
                        page.goto(url, wait_until="domcontentloaded")
                        page.wait_for_timeout(2500)
                    except PWTimeout:
                        print(f"[{self.NAME}] Timeout on {url}, skipping")
                        break

                    self._save_debug(f"p{page_num}", page.content())

                    cards = page.query_selector_all(CARD_SEL)
                    if not cards:
                        print(f"[{self.NAME}] No cards found on page {page_num}, stopping")
                        break

                    page_new = 0
                    for card in cards:
                        href = card.get_attribute("href") or self._attr(card, "a", "href")
                        if not href:
                            continue
                        full_url = href if href.startswith("http") else self.BASE_URL + href
                        if full_url in seen_urls:
                            continue
                        seen_urls.add(full_url)

                        title = self._first_text(card, *TITLE_SELS)
                        if not title:
                            continue

                        listing = BusinessListing(
                            source="bizbuysell",
                            title=title,
                            url=full_url,
                            asking_price=self._first_text(card, *PRICE_SELS),
                            revenue=self._first_text(card, *REVENUE_SELS),
                            cash_flow=self._first_text(card, *CASHFLOW_SELS),
                            location=self._first_text(card, *LOCATION_SELS),
                            industry=self._first_text(card, *INDUSTRY_SELS),
                            image_url=self._attr(card, "img", "src"),
                        )
                        results.append(listing)
                        page_new += 1

                    print(f"[{self.NAME}] Page {page_num}: {page_new} listings")
                    if page_new == 0:
                        break

                    next_btn = page.query_selector("a[rel='next'], .pagination .next a, a.next-page")
                    if not next_btn:
                        break
                    self._sleep(2, 4)

            browser.close()

        print(f"[{self.NAME}] Total: {len(results)} listings")
        return results
