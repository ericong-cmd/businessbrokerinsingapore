"""
BusinessesForSale.com scraper — targets the Singapore and SE Asia sections.

The site has dedicated country sub-directories. Add more country URLs to
SEARCH_URLS to expand geographic coverage.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from .base import BaseScraper, BusinessListing

SEARCH_URLS = [
    "https://www.businessesforsale.com/singapore/businesses-for-sale",
    "https://www.businessesforsale.com/malaysia/businesses-for-sale",
    "https://www.businessesforsale.com/thailand/businesses-for-sale",
    "https://www.businessesforsale.com/indonesia/businesses-for-sale",
    "https://www.businessesforsale.com/philippines/businesses-for-sale",
    "https://www.businessesforsale.com/hong-kong/businesses-for-sale",
]

CARD_SEL = (
    ".listing-item, article.listing, .classified-listing, "
    ".search-result-item, .business-listing-item"
)
TITLE_SELS = ["h2 a", "h3 a", ".listing-title a", ".title a", "h2", "h3"]
PRICE_SELS = [".asking-price", ".price", ".listing-price", "[class*='price']"]
REVENUE_SELS = [".revenue", ".annual-revenue", "[class*='revenue']", "[class*='turnover']"]
CASHFLOW_SELS = [".cash-flow", ".profit", ".net-profit", "[class*='cash']"]
LOCATION_SELS = [".location", ".address", ".city", "[class*='location']"]
INDUSTRY_SELS = [".category", ".industry", ".sector", "[class*='category']", "[class*='type']"]
DESC_SELS = [".description", ".listing-description", ".summary", "p.excerpt"]


class BusinessesForSaleScraper(BaseScraper):
    NAME = "BusinessesForSale"
    BASE_URL = "https://www.businessesforsale.com"

    def scrape(self, max_pages: int = 5) -> list[BusinessListing]:
        results: list[BusinessListing] = []
        seen_urls: set[str] = set()

        with sync_playwright() as p:
            browser, context = self._make_browser_context(p)
            page = context.new_page()

            for base_url in SEARCH_URLS:
                country = base_url.split("/")[3].replace("-", " ").title()
                for page_num in range(1, max_pages + 1):
                    url = base_url if page_num == 1 else f"{base_url}?page={page_num}"
                    print(f"[{self.NAME}] [{country}] Fetching page {page_num}: {url}")
                    try:
                        page.goto(url, wait_until="domcontentloaded")
                        page.wait_for_timeout(2500)
                    except PWTimeout:
                        print(f"[{self.NAME}] Timeout on {url}, skipping")
                        break

                    self._save_debug(f"{country.lower()}_p{page_num}", page.content())

                    cards = page.query_selector_all(CARD_SEL)
                    if not cards:
                        print(f"[{self.NAME}] No listing cards found on page {page_num}")
                        break

                    page_new = 0
                    for card in cards:
                        link_el = card.query_selector("a[href]")
                        if not link_el:
                            continue
                        href = link_el.get_attribute("href") or ""
                        if not href:
                            continue
                        full_url = href if href.startswith("http") else self.BASE_URL + href
                        if full_url in seen_urls:
                            continue
                        seen_urls.add(full_url)

                        title = self._first_text(card, *TITLE_SELS)
                        if not title:
                            title = (link_el.inner_text() or "").strip()
                        if not title:
                            continue

                        listing = BusinessListing(
                            source="businessesforsale",
                            title=title,
                            url=full_url,
                            asking_price=self._first_text(card, *PRICE_SELS),
                            revenue=self._first_text(card, *REVENUE_SELS),
                            cash_flow=self._first_text(card, *CASHFLOW_SELS),
                            location=self._first_text(card, *LOCATION_SELS) or country,
                            industry=self._first_text(card, *INDUSTRY_SELS),
                            description=self._first_text(card, *DESC_SELS),
                            image_url=self._attr(card, "img", "src"),
                        )
                        results.append(listing)
                        page_new += 1

                    print(f"[{self.NAME}] [{country}] Page {page_num}: {page_new} listings")
                    if page_new == 0:
                        break

                    next_btn = page.query_selector(
                        "a[rel='next'], .pagination a.next, a[aria-label='Next']"
                    )
                    if not next_btn:
                        break
                    self._sleep(2, 4)

            browser.close()

        print(f"[{self.NAME}] Total: {len(results)} listings")
        return results
