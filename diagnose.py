"""
Run this to diagnose why scrapers return 0 results.
It visits each site, saves HTML + a screenshot, and prints candidate selectors.

Usage:  python3 diagnose.py
Output: data/debug/<source>_page.html  and  data/debug/<source>_screenshot.png
"""
import os, sys
from playwright.sync_api import sync_playwright

DEBUG_DIR = os.path.join(os.path.dirname(__file__), "data", "debug")
os.makedirs(DEBUG_DIR, exist_ok=True)

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

SITES = [
    ("bizbuysell",        "https://www.bizbuysell.com/businesses-for-sale/?q=Singapore"),
    ("businessesforsale", "https://www.businessesforsale.com/singapore/businesses-for-sale"),
    ("matchasia",         "https://www.match.asia"),
    ("acquire",           "https://acquire.com/marketplace"),
]

def diagnose_site(page, name, url):
    print(f"\n{'='*60}")
    print(f"  {name.upper()}  →  {url}")
    print(f"{'='*60}")

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)
    except Exception as e:
        print(f"  ERROR loading page: {e}")
        return

    # Save HTML and screenshot
    html_path = os.path.join(DEBUG_DIR, f"{name}_page.html")
    png_path  = os.path.join(DEBUG_DIR, f"{name}_screenshot.png")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(page.content())
    page.screenshot(path=png_path, full_page=False)
    print(f"  HTML saved:       {html_path}")
    print(f"  Screenshot saved: {png_path}")

    # Count headings and links — gives a sense of page structure
    h_counts = {
        tag: len(page.query_selector_all(tag))
        for tag in ["h1", "h2", "h3", "h4", "article", "section", "li", "a"]
    }
    print(f"\n  Element counts: {h_counts}")

    # Print first 8 h2/h3 texts — usually listing titles
    for tag in ["h2", "h3"]:
        els = page.query_selector_all(tag)[:8]
        if els:
            texts = [e.inner_text().strip()[:80] for e in els if e.inner_text().strip()]
            if texts:
                print(f"\n  First <{tag}> texts:")
                for t in texts:
                    print(f"    • {t}")

    # Find repeated block elements — likely listing cards
    # Look for elements with class names containing common keywords
    keywords = ["listing", "card", "business", "result", "item", "classified", "startup"]
    found_classes = set()
    for kw in keywords:
        els = page.query_selector_all(f"[class*='{kw}']")
        for el in els[:3]:
            cls = el.get_attribute("class") or ""
            first_cls = cls.split()[0] if cls.split() else ""
            if first_cls:
                found_classes.add(f".{first_cls}")

    if found_classes:
        print(f"\n  Candidate card classes: {sorted(found_classes)}")
    else:
        print("\n  No card classes found with keywords: listing/card/business/result/item")

    # Check for price-like text
    price_patterns = ["$", "SGD", "USD", "MYR", "asking", "price"]
    for pat in price_patterns:
        try:
            el = page.get_by_text(pat, exact=False).first
            if el:
                parent_cls = ""
                try:
                    parent = el.evaluate("el => el.parentElement?.className || ''")
                    parent_cls = f"(parent class: {parent[:60]})"
                except Exception:
                    pass
                print(f"  Found '{pat}' text {parent_cls}")
                break
        except Exception:
            pass

    # Print page title so we know what loaded
    print(f"\n  Page title: {page.title()[:100]}")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=UA,
            viewport={"width": 1440, "height": 900},
            locale="en-US",
        )
        page = context.new_page()

        for name, url in SITES:
            if target != "all" and target != name:
                continue
            diagnose_site(page, name, url)

        browser.close()

    print(f"\n\nDone. Check data/debug/ for screenshots and raw HTML.")
    print("Share this output + screenshots to get the selectors fixed.\n")


if __name__ == "__main__":
    main()
