"""
Acquire.com scraper — online / SaaS businesses globally.

Acquire.com is a React SPA. The scraper waits for the listings to hydrate,
then parses the rendered DOM. The site may require scrolling to load all cards.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from .base import BaseScraper, BusinessListing

BASE_URL = "https://acquire.com"

CARD_SEL = (
    "[data-testid='listing-card'], .listing-card, .startup-card, "
    "[class*='ListingCard'], [class*='listing-card'], "
    "[class*='StartupCard'], article"
)
TITLE_SELS = [
    "[data-testid='listing-title']", "h2", "h3",
    "[class*='title']", "[class*='name']"
]
PRICE_SELS = [
    "[data-testid='asking-price']", "[class*='price']",
    "[class*='asking']", "[class*='Price']"
]
REVENUE_SELS = [
    "[data-testid='revenue']", "[class*='revenue']", "[class*='Revenue']",
    "[class*='arr']", "[class*='mrr']"
]
PROFIT_SELS = [
    "[data-testid='profit']", "[class*='profit']", "[class*='ebitda']",
    "[class*='Profit']"
]
LOCATION_SELS = [
    "[data-testid='location']", "[class*='location']",
    "[class*='Location']", "[class*='country']"
]
INDUSTRY_SELS = [
    "[data-testid='category']", "[class*='category']",
    "[class*='Category']", "[class*='type']", "[class*='tag']"
]


class AcquireScraper(BaseScraper):
    NAME = "Acquire.com"
    BASE_URL = BASE_URL

    def scrape(self, max_pages: int = 5) -> list[BusinessListing]:
        results: list[BusinessListing] = []
        seen_urls: set[str] = set()

        with sync_playwright() as p:
            browser, context = self._make_browser_context(p)
            page = context.new_page()

            url = "https://acquire.com/marketplace"
            print(f"[{self.NAME}] Navigating to {url}")
            try:
                page.goto(url, wait_until="networkidle", timeout=45000)
            except PWTimeout:
                try:
                    page.goto(url, wait_until="domcontentloaded")
                    page.wait_for_timeout(5000)
                except PWTimeout:
                    print(f"[{self.NAME}] Could not load {url}")
                    browser.close()
                    return results

            self._save_debug("marketplace", page.content())

            for page_num in range(1, max_pages + 1):
                # Scroll to load all cards (lazy loading)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)

                self._save_debug(f"p{page_num}", page.content())
                cards = page.query_selector_all(CARD_SEL)
                if not cards:
                    print(f"[{self.NAME}] No cards found. HTML saved for debugging.")
                    break

                page_new = 0
                for card in cards:
                    link_el = card.query_selector("a[href]")
                    href = (link_el.get_attribute("href") if link_el else None) or ""
                    if not href:
                        href = card.get_attribute("href") or ""
                    if not href:
                        continue

                    full_url = href if href.startswith("http") else BASE_URL + href
                    if full_url in seen_urls:
                        continue
                    seen_urls.add(full_url)

                    title = self._first_text(card, *TITLE_SELS)
                    if not title:
                        continue

                    listing = BusinessListing(
                        source="acquire",
                        title=title,
                        url=full_url,
                        asking_price=self._first_text(card, *PRICE_SELS),
                        revenue=self._first_text(card, *REVENUE_SELS),
                        cash_flow=self._first_text(card, *PROFIT_SELS),
                        location=self._first_text(card, *LOCATION_SELS),
                        industry=self._first_text(card, *INDUSTRY_SELS),
                        image_url=self._attr(card, "img", "src"),
                    )
                    results.append(listing)
                    page_new += 1

                print(f"[{self.NAME}] Page {page_num}: {page_new} listings")

                # Acquire uses infinite scroll or pagination buttons
                next_btn = page.query_selector(
                    "button[aria-label='Next page'], a[aria-label='Next'], "
                    "[data-testid='next-page'], button.next, .pagination-next"
                )
                if not next_btn or page_num >= max_pages:
                    break
                next_btn.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)
                self._sleep(2, 4)

            browser.close()

        print(f"[{self.NAME}] Total: {len(results)} listings")
        return results
