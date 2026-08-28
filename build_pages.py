#!/usr/bin/env python3
"""Generate interior pages for businessbrokerinsingapore.com with a shared shell."""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.businessbrokerinsingapore.com"
WA = "6589518821"

WA_PATH = "M17.5 14.4c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.68-1.62-.93-2.22-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.5 0 1.47 1.07 2.9 1.22 3.1.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.42.25-.7.25-1.3.18-1.42-.08-.13-.28-.2-.58-.35zM12.05 21.8h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.82 9.82 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.9-9.88a9.82 9.82 0 0 1 7 2.9 9.82 9.82 0 0 1 2.9 7c0 5.44-4.45 9.87-9.9 9.87zm8.42-18.3A11.8 11.8 0 0 0 12.04 0C5.46 0 .1 5.35.1 11.92c0 2.1.55 4.15 1.6 5.96L0 24l6.27-1.64a11.94 11.94 0 0 0 5.77 1.47c6.58 0 11.94-5.35 11.94-11.92 0-3.18-1.24-6.18-3.5-8.42z"

def wa_icon(size=18):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="{WA_PATH}"/></svg>'

def wa_link(text):
    from urllib.parse import quote
    return f"https://wa.me/{WA}?text={quote(text)}"

CHEV = '<svg class="chev" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'

def faq_html(faqs):
    out = []
    for q, a in faqs:
        out.append(f'''<div class="faq-item">
          <button class="faq-q" aria-expanded="false">{q}{CHEV}</button>
          <div class="faq-a-wrap"><div class="faq-a"><p>{a}</p></div></div>
        </div>''')
    return "\n".join(out)

def faq_schema(faqs):
    import re
    strip = lambda s: re.sub(r"<[^>]+>", "", s)
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": strip(q),
             "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
            for q, a in faqs
        ],
    }

def breadcrumb_schema(title, path):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": title, "item": f"{BASE}/{path}/"},
        ],
    }

ORG_ID = BASE + "/#organization"

def org_schema():
    return {
        "@type": "ProfessionalService",
        "@id": ORG_ID,
        "name": "Business Broker In Singapore",
        "url": BASE + "/",
        "description": "Confidential sell-side M&A advisory and business brokerage for Singapore SMEs with S$2M–S$20M revenue. Zero upfront fees, success-only commission.",
        "areaServed": {"@type": "Country", "name": "Singapore"},
        "knowsAbout": ["Business sales", "SME M&A", "Business valuation", "Succession planning"],
        "priceRange": "Success fee 1%–5% of sale price, no upfront fees",
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "sales",
            "telephone": "+65 8951 8821",
            "availableLanguage": ["en"],
        },
        "sameAs": ["https://thefundingassembly.com"],
        "parentOrganization": {
            "@type": "Organization",
            "name": "The Funding Assembly",
            "legalName": "THE FUNDING ASSEMBLY PTE. LTD.",
            "url": "https://thefundingassembly.com",
            "identifier": {"@type": "PropertyValue", "propertyID": "UEN", "value": "202443830Z"},
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "2 Leng Kee Road, #02-06 Thye Hong Centre",
                "postalCode": "159086",
                "addressCountry": "SG",
            },
        },
    }

def website_schema():
    return {
        "@type": "WebSite",
        "@id": BASE + "/#website",
        "url": BASE + "/",
        "name": "Business Broker In Singapore",
        "publisher": {"@id": ORG_ID},
        "inLanguage": "en-SG",
    }

def service_schema(name, stype):
    return {
        "@type": "Service",
        "name": name,
        "serviceType": stype,
        "areaServed": {"@type": "Country", "name": "Singapore"},
        "provider": {"@id": ORG_ID},
    }

def nav(active):
    items = [
        ("sell-your-business-singapore", "Sell Your Business"),
        ("business-valuation-singapore", "Valuation"),
        ("how-it-works", "How It Works"),
        ("fees", "Fees"),
        ("buy-a-business-singapore", "Buy a Business"),
    ]
    cur = ' aria-current="page"'
    links = "\n".join(
        f'<li><a href="/{slug}/"{cur if slug == active else ""}>{label}</a></li>'
        for slug, label in items
    )
    mlinks = "\n".join(
        f'<a href="/{slug}/"{cur if slug == active else ""}>{label}</a>'
        for slug, label in items + [("faq", "FAQ"), ("contact", "Contact")]
    )
    return links, mlinks

def shell(page):
    links, mlinks = nav(page["slug"])
    schema = {"@context": "https://schema.org",
              "@graph": [org_schema(), website_schema()] + page["schema"]}
    hero_ctas = page.get("hero_ctas", f'''<div class="hero-ctas" style="margin-top:1.8rem">
        <a class="btn btn-wa" href="{wa_link("Hi, I'd like a confidential chat about selling my business.")}">{wa_icon()} WhatsApp — Confidential</a>
        <a class="btn btn-outline" href="/#valuation">Free Valuation Estimate</a>
      </div>''')
    return f'''<!DOCTYPE html>
<html lang="en-SG">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page["title"]}</title>
<meta name="description" content="{page["description"]}">
<link rel="canonical" href="{BASE}/{page["slug"]}/">
<meta property="og:type" content="website">
<meta property="og:title" content="{page["title"]}">
<meta property="og:description" content="{page["description"]}">
<meta property="og:url" content="{BASE}/{page["slug"]}/">
<meta property="og:locale" content="en_SG">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/poppins-600-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/opensans-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/style.css">
<noscript><style>.reveal,.hero .fx{{opacity:1!important;transform:none!important}}.timeline .t-line{{transform:none!important}}</style></noscript>
<script type="application/ld+json">
{json.dumps(schema, indent=1, ensure_ascii=False)}
</script>
<script defer src="/_vercel/insights/script.js"></script>
<script defer src="/_vercel/speed-insights/script.js"></script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<div id="top-sentinel"></div>

<header class="site-header">
  <div class="nav-wrap">
    <a class="brand" href="/">Business Broker <em style="font-style:normal;color:var(--gold-soft)">In Singapore</em>
      <span class="brand-sub">Confidential SME Sales</span>
    </a>
    <nav aria-label="Main">
      <ul class="nav-links">
        {links}
      </ul>
    </nav>
    <a class="btn btn-wa nav-cta" href="{wa_link("Hi, I own a business in Singapore and I'm exploring a confidential sale. Can we talk?")}">{wa_icon()} WhatsApp Us</a>
    <button class="menu-btn" aria-label="Open menu" aria-expanded="false">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
    </button>
  </div>
  <nav class="mobile-nav" aria-label="Mobile">
    {mlinks}
  </nav>
</header>

<main id="main">
  <div class="page-hero">
    <div class="container">
      <p class="breadcrumbs"><a href="/">Home</a> / {page["crumb"]}</p>
      <h1>{page["h1"]}</h1>
      <p class="lead">{page["lead"]}</p>
      {hero_ctas}
    </div>
  </div>

{page["main"]}

  <section class="cta-band" aria-label="Get in touch">
    <div class="container">
      <h2>{page.get("cta_h", "Start with one confidential conversation.")}</h2>
      <p>{page.get("cta_p", "Thirty minutes on WhatsApp or a call. No fee, no obligation — and your name stays private until you decide otherwise.")}</p>
      <div class="hero-ctas">
        <a class="btn btn-wa" href="{wa_link(page.get("cta_wa", "Hi, I'd like a confidential 30-minute conversation about selling my business."))}">{wa_icon()} WhatsApp +65 8951 8821</a>
      </div>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <h3>Business Broker In Singapore</h3>
        <p style="max-width:40ch">Confidential sell-side brokerage for Singapore SME owners. Success-only fees, NDA-protected process, buyers vetted before disclosure.</p>
      </div>
      <div>
        <h3>Sellers</h3>
        <ul>
          <li><a href="/sell-your-business-singapore/">Sell your business</a></li>
          <li><a href="/business-valuation-singapore/">Business valuation</a></li>
          <li><a href="/how-it-works/">How it works</a></li>
          <li><a href="/fees/">Fees</a></li>
          <li><a href="/sell-your-fnb-business-singapore/">Sell an F&amp;B business</a></li>
          <li><a href="/faq/">Seller FAQ</a></li>
        </ul>
      </div>
      <div>
        <h3>Contact</h3>
        <ul>
          <li><a href="https://wa.me/{WA}">WhatsApp +65 8951 8821</a></li>
          <li><a href="/buy-a-business-singapore/">Buy a business</a></li>
          <li><a href="/contact/">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>© 2026 Business Broker In Singapore. All discussions are confidential; nothing on this site is an offer of securities or investment advice.</p>
    </div>
  </div>
</footer>

<a class="wa-float" href="{wa_link("Hi, I'd like a confidential chat about selling my business.")}" aria-label="Chat on WhatsApp">{wa_icon(30)}</a>

<nav class="mobile-bar" aria-label="Quick actions">
  <a class="m-wa" href="{wa_link("Hi, I'd like a confidential chat about selling my business.")}">{wa_icon(20)} WhatsApp</a>
  <a class="m-val" href="/#valuation">Free Valuation</a>
</nav>

<script src="/assets/js/main.js" defer></script>
</body>
</html>
'''

# ============================== PAGES ==============================
PAGES = []

# ---- Sell Your Business ----
faqs_sell = [
    ("Do I need a business broker to sell my company?",
     "No — but sales without an advisor are significantly less likely to complete, and represented sellers typically achieve higher prices through competitive tension, buyer screening and negotiation support. Just as importantly, a broker runs the six-to-twelve-month process while you keep running the business, so performance doesn't dip mid-sale."),
    ("Should I sell shares or assets?",
     "Most Singapore SME sales are share sales: the buyer acquires the entire Pte Ltd, contracts and licences transfer automatically, and individuals pay no capital gains tax in Singapore. Asset sales suit buyers who want to avoid inherited liabilities, but can trigger GST and require re-signing contracts and leases. The right structure is a negotiation point — often worth more than a few points of headline price."),
    ("What documents do I need to prepare?",
     "Buyers expect at least three years of financial statements, up-to-date ACRA records, management accounts, GST and tax filings, CPF records, key contracts and leases, licence documentation, and an organisation chart. Clean, consistent records directly increase both valuation and the odds the deal completes."),
    ("What if my business depends heavily on me?",
     "It's the most common situation we see, and it's fixable. Documented processes, a second-tier manager, and transferable customer relationships — built up over 6–18 months — materially raise both saleability and price. A transition period after completion, where you stay on for a agreed handover, bridges the rest."),
    ("When should I start planning the sale?",
     "Ideally one to three years before you want to exit. That's enough time to normalise the accounts, reduce owner-dependence and time the market. But if you need to sell sooner, a structured process still beats an unprepared one — start with a confidential conversation either way."),
    ("What is an earn-out, and should I accept one?",
     "An earn-out pays part of the price later, conditional on the business hitting agreed targets after completion. Buyers propose it when part of the value depends on you — key customer relationships, a pending contract, your continued involvement. Accept one only when the targets are measurable, largely within your control, capped in time (typically 12–24 months), and the guaranteed portion alone is a price you can live with. A well-run competitive process reduces how much earn-out you're forced to accept."),
    ("What happens to my employees when I sell?",
     "In a share sale — the structure of most Singapore SME deals — employment contracts continue automatically because the employer, the Pte Ltd, hasn't changed. CPF, leave accruals and length of service are all preserved. Buyers of profitable SMEs are almost always acquiring the team, not dismantling it; key-staff retention is usually a condition of the deal, not a casualty of it. Where you want specific protections for long-serving staff, we negotiate them into the sale and purchase agreement."),
]
PAGES.append({
    "slug": "sell-your-business-singapore",
    "crumb": "Sell Your Business",
    "title": "Sell My Business in Singapore — Confidential, Success-Fee Only",
    "description": "How to sell your business in Singapore confidentially: valuation, vetted buyers under NDA, negotiation and completion — zero upfront fees.",
    "h1": "Sell your business in Singapore — without anyone knowing it's for sale.",
    "lead": "You've spent decades building it. Selling it well is a six-to-eight-month structured process — not a listing on a marketplace. Here's how it works, and how your staff, customers and competitors stay unaware until the day you choose to tell them.",
    "schema": [],
    "main": f'''
  <section>
    <div class="container prose">
      <div class="answer-first reveal">
        <p><strong>To sell a business in Singapore</strong>, you establish a defensible valuation (usually a multiple of adjusted EBITDA), prepare no-name marketing materials, approach screened buyers under NDA, negotiate offers to a term sheet, then complete due diligence and the sale and purchase agreement. With an advisor running the process, it typically takes 6–8 months and costs nothing unless the business sells.</p>
      </div>

      <h2 class="reveal">Selling well is a process problem, not a luck problem</h2>
      <p class="reveal">Most owners sell a business once in their life. The buyer across the table has often bought several. That gap — in experience, in information, in patience — is exactly what a structured sell-side process closes:</p>
      <div class="grid-2 mt-2">
        <div class="card reveal" style="--i:0"><h3>Competitive tension</h3><p>One interested buyer sets the price. Several, arriving through a managed process, compete for it. This is the single biggest driver of final value.</p></div>
        <div class="card reveal" style="--i:1"><h3>Qualified buyers only</h3><p>Every enquiry is scored on intent, fit and financial capability before you hear about it. You meet three serious buyers, not thirty curious ones.</p></div>
        <div class="card reveal" style="--i:2"><h3>The business keeps performing</h3><p>Deals die when owners get distracted and revenue dips mid-process. You run the company; the process runs in the background.</p></div>
        <div class="card reveal" style="--i:3"><h3>Someone on your side</h3><p>From valuation to term sheet to due diligence, every negotiation point — price, structure, transition, warranties — is argued for you, not against you.</p></div>
      </div>

      <h2 class="reveal">What your business sale looks like, step by step</h2>
      <p class="reveal">The full seven-stage process is on <a href="/how-it-works/">How It Works</a>. In short: a confidential conversation, then valuation and preparation (weeks 2–6), blind marketing (month 2), buyer screening and meetings (months 2–4), offers and negotiation (months 4–5), due diligence (months 5–7), and completion (months 7–8).</p>

      <h2 class="reveal">Legacy matters as much as price</h2>
      <p class="reveal">For most founders, the number is only half the decision. What happens to long-serving staff, whether the brand continues, how customers are handed over — these are negotiated deal terms, not afterthoughts. Buyer selection weighs them from the first screen: a buyer who plans to keep your team and grow the business is often the right buyer even when a purely financial bidder offers slightly more.</p>

      <h2 class="reveal">Who this is for</h2>
      <p class="reveal">Owners of profitable Singapore businesses with roughly <strong>S$2M–S$20M annual revenue</strong> — retiring founders, family businesses without a successor, partners going separate ways, or owners ready for the next chapter. If your business is smaller, message us anyway; we'll point you to the right resources honestly rather than waste your time.</p>
    </div>
  </section>

  <section class="on-light" style="padding-top:0">
    <div class="container">
      <div class="section-head reveal"><h2>Common questions from sellers</h2></div>
      <div class="reveal" style="max-width:820px">
        {faq_html(faqs_sell)}
      </div>
    </div>
  </section>
''',
    "cta_wa": "Hi, I'm thinking about selling my business and would like a confidential conversation.",
})
PAGES[-1]["schema"] = [faq_schema(faqs_sell), breadcrumb_schema("Sell Your Business", "sell-your-business-singapore"),
                       service_schema("Sell your business in Singapore", "Sell-side business brokerage")]

# ---- Business Valuation ----
faqs_val = [
    ("How much is my business worth?",
     "Most profitable Singapore SMEs sell for a multiple of adjusted EBITDA — typically 2× to 9× depending on industry, size, growth and owner-dependence. A business earning S$500,000 adjusted EBITDA in a 3–4× sector would be worth roughly S$1.5M–S$2M. Use the estimator on this page for an indicative range."),
    ("What is adjusted EBITDA?",
     "EBITDA is earnings before interest, tax, depreciation and amortisation — a proxy for the cash profit a buyer acquires. 'Adjusted' means normalising it: adding back the excess of the owner's salary over a market-rate replacement, one-off or non-recurring expenses, and personal expenses run through the company; and deducting any market-rate costs the business currently avoids, such as rent on premises the owner owns personally."),
    ("Why do multiples differ so much between industries?",
     "Multiples price risk and growth. Recurring-revenue businesses (software, healthcare, education) command 4–9× because earnings are predictable. Project-based sectors (construction, retail) sit at 2–4× because each year starts from zero. Contracts, customer diversification and margin stability move a business up within its sector's range."),
    ("Does revenue matter, or only profit?",
     "Both. Profit (adjusted EBITDA) sets the valuation base, but revenue scale affects the multiple itself — larger businesses trade at higher multiples because they're less fragile and attract institutional buyers. That's one reason a S$10M-revenue business is usually worth more than twice a S$5M one with the same margin."),
    ("Is a professional valuation different from this estimate?",
     "Yes. An estimate applies a sector multiple to your stated EBITDA. A real assessment verifies the EBITDA adjustments line by line, weighs customer concentration, contract quality, growth and transferability, and positions the business against actual recent transactions — producing a range you can defend across the table from a buyer's accountant."),
    ("A buyer has already approached me. How do I know their offer is fair?",
     "You can't — not from one offer. An unsolicited buyer is pricing against your ignorance of the market, not against other bidders, and unsolicited first offers on Singapore SMEs routinely come in 20–40% below what a competitive process achieves. The answer isn't to reject the buyer; it's to establish an independent valuation, then either negotiate from evidence or quietly test the market alongside them. We regularly run exactly this play — the original buyer often still wins, but at a market price."),
    ("Can I sell a business that isn't profitable?",
     "Often, yes — but on a different basis. Loss-making or break-even businesses sell on asset value (equipment, fitted premises, stock), on licences and approvals that are slow to obtain from scratch, on contracts and customer relationships, or to a strategic buyer who can strip out duplicate costs. The price reflects that basis rather than an earnings multiple. What matters is being honest about which basis applies before going to market."),
]
PAGES.append({
    "slug": "business-valuation-singapore",
    "crumb": "Business Valuation",
    "title": "Business Valuation Singapore — What's My Business Worth?",
    "description": "How Singapore SMEs are valued: adjusted EBITDA × sector multiple (2–9×), with a worked example, multiples table by industry, and a free instant estimator.",
    "h1": "How much is your business worth?",
    "lead": "Most profitable Singapore SMEs sell for 2–9× adjusted EBITDA, depending on the sector. Here's exactly how the arithmetic works — with real multiples by industry and a worked example a buyer's accountant would accept.",
    "schema": [],
    "hero_ctas": '''<div class="hero-ctas" style="margin-top:1.8rem">
        <a class="btn btn-gold" href="/#valuation">Use the Free Estimator</a>
      </div>''',
    "main": f'''
  <section>
    <div class="container prose">
      <div class="answer-first reveal">
        <p><strong>To value a business in Singapore</strong>, take adjusted EBITDA — profit before interest, tax, depreciation and amortisation, normalised for owner's excess salary and one-off costs — and multiply it by a sector multiple, typically 2× to 9×. Asset-heavy or loss-making businesses are valued on assets, licences or strategic worth instead.</p>
      </div>

      <h2 class="reveal">Step 1 — Normalise the profit (adjusted EBITDA)</h2>
      <p class="reveal">Buyers don't buy your accounting profit; they buy the cash the business would generate under their ownership. A worked example:</p>
      <div class="table-wrap reveal">
        <table>
          <thead><tr><th scope="col">Line item</th><th scope="col">Amount</th></tr></thead>
          <tbody>
            <tr><td>Profit before tax (per accounts)</td><td>S$450,000</td></tr>
            <tr><td>+ Interest expense</td><td>S$20,000</td></tr>
            <tr><td>+ Depreciation &amp; amortisation</td><td>S$80,000</td></tr>
            <tr><td><strong>EBITDA</strong></td><td><strong>S$550,000</strong></td></tr>
            <tr><td>+ Owner's salary of S$300,000, less S$150,000 market rate for a replacement GM (add back the excess)</td><td>S$150,000</td></tr>
            <tr><td>+ One-off renovation expensed this year</td><td>S$50,000</td></tr>
            <tr><td><strong>Adjusted EBITDA</strong></td><td><strong>S$750,000</strong></td></tr>
          </tbody>
        </table>
      </div>
      <p class="reveal mt-1">At a 3–4× sector multiple, this business is indicatively worth <strong>S$2.25M–S$3.0M</strong>. Note the direction of each adjustment matters: if the owner underpays themselves, the adjustment goes the other way — a deduction, not an add-back.</p>

      <h2 class="reveal">Step 2 — Apply the sector multiple</h2>
      <div class="table-wrap reveal">
        <table>
          <thead><tr><th scope="col">Industry (Singapore SME)</th><th scope="col">Typical adjusted EBITDA multiple</th></tr></thead>
          <tbody>
            <tr><td>Software / technology</td><td><strong>4× – 9×</strong></td></tr>
            <tr><td>Healthcare / education</td><td><strong>4× – 7×</strong></td></tr>
            <tr><td>Manufacturing / engineering</td><td><strong>3× – 6×</strong></td></tr>
            <tr><td>Professional / B2B services</td><td><strong>3× – 6×</strong></td></tr>
            <tr><td>Logistics / transport</td><td><strong>3× – 5.5×</strong></td></tr>
            <tr><td>E-commerce / online</td><td><strong>2.5× – 5.5×</strong></td></tr>
            <tr><td>F&amp;B / food manufacturing</td><td><strong>2.5× – 5×</strong></td></tr>
            <tr><td>Distribution / wholesale</td><td><strong>2.5× – 5×</strong></td></tr>
            <tr><td>Construction / M&amp;E</td><td><strong>2× – 4×</strong></td></tr>
            <tr><td>Retail / consumer</td><td><strong>2× – 4×</strong></td></tr>
          </tbody>
        </table>
      </div>
      <p class="reveal mt-1">Where you land within the range depends on: growth trend, customer concentration (one customer above 30% of revenue is a red flag), recurring vs project revenue, margin stability, contract quality, and how dependent the business is on you personally.</p>

      <h2 class="reveal">Step 3 — Reality-check against the market</h2>
      <p class="reveal">A valuation is a hypothesis; the market is the test. Serious buyers benchmark against comparable transactions, and the final number also reflects deal structure — an all-cash completion prices differently from an earn-out. This is why a defensible range beats a single precise-sounding number.</p>

      <p class="reveal mt-2"><a class="btn btn-gold" href="/#valuation">Get your instant estimate</a></p>
    </div>
  </section>

  <section class="on-light" style="padding-top:0">
    <div class="container">
      <div class="section-head reveal"><h2>Valuation questions, answered</h2></div>
      <div class="reveal" style="max-width:820px">
        {faq_html(faqs_val)}
      </div>
    </div>
  </section>
''',
    "cta_h": "Want a number you can actually defend?",
    "cta_p": "Send us your rough figures on WhatsApp and get a considered view — what the range is, what's driving it, and what would raise it. Confidential, no fee, no obligation.",
    "cta_wa": "Hi, I'd like a confidential view on what my business might be worth.",
})
PAGES[-1]["schema"] = [faq_schema(faqs_val), breadcrumb_schema("Business Valuation", "business-valuation-singapore"),
                       service_schema("Business valuation in Singapore", "Business valuation")]

# ---- Fees ----
faqs_fees = [
    ("How much do business brokers charge in Singapore?",
     "Most Singapore business brokers charge a success fee of 5–10% of the sale price, and some M&A firms add monthly retainers of S$5,000–S$25,000. Our schedule is success-only and tiered: 5% up to S$5M, stepping down to 1% above S$50M, minimum fee S$100,000, zero upfront."),
    ("What does the success fee actually cover?",
     "Everything from valuation to completion: preparing the information memorandum, confidential buyer marketing, screening and scoring buyers, running meetings and negotiations, managing the data room and due diligence, and coordinating lawyers through to the sale and purchase agreement. There are no add-on charges along the way."),
    ("Why is there a minimum fee?",
     "A properly run sale takes the same six to eight months of senior work whether the business sells for S$1M or S$10M. The S$100,000 minimum reflects that — and it means our process realistically suits transactions of about S$1.5M and above. Below that, marketplace platforms are often the more economical route, and we'll say so."),
    ("Do I pay anything if the business doesn't sell?",
     "No. No retainer, no monthly fee, no marketing charges, no exit penalty. The entire fee is contingent on completion — we are paid out of the sale proceeds when you are paid."),
    ("Is the fee negotiable or locked in a long contract?",
     "The fee schedule is standard so every seller is treated the same. The engagement includes an agreed exclusivity period — necessary for running a credible process with buyers — but you are not locked in indefinitely, and the terms are in plain English in the appointment agreement you sign."),
    ("I've already found a buyer myself. Is the fee lower?",
     "Having a buyer at the table changes the work, not the stakes — valuation evidence, negotiation, deal structure, due diligence management and completion still decide whether you get a fair price or leave hundreds of thousands behind. We offer a reduced single-buyer engagement for exactly this situation: you keep your buyer, we run the deal, and if we think competitive tension would materially beat their number, we'll show you the arithmetic and let you decide."),
]
PAGES.append({
    "slug": "fees",
    "crumb": "Fees",
    "title": "Business Broker Fees Singapore — Published Fee Schedule",
    "description": "Business broker fees in Singapore: market rates run 5–10%. Our success-only schedule: 5% up to S$5M down to 1% above S$50M, S$100k minimum, zero upfront.",
    "h1": "Business broker fees in Singapore — published, not whispered.",
    "lead": "Most brokers say “no upfront fees” and stop there. Here is the entire fee schedule, what the market typically charges, and an honest note on when our minimum fee makes us the wrong choice.",
    "schema": [],
    "main": f'''
  <section>
    <div class="container prose">
      <div class="answer-first reveal">
        <p><strong>Business brokers in Singapore typically charge 5–10% of the sale price</strong> as a success fee, with some M&amp;A advisory firms adding monthly retainers of S$5,000–S$25,000. Our fees are success-only and tiered by transaction size: 5% up to S$5M, down to 1% above S$50M, with a S$100,000 minimum and nothing payable upfront.</p>
      </div>

      <h2 class="reveal">Our fee schedule</h2>
      <div class="table-wrap reveal">
        <table>
          <thead><tr><th scope="col">Transaction value</th><th scope="col">Success fee</th><th scope="col">Fee on a sale at the top of the band</th></tr></thead>
          <tbody>
            <tr><td>Up to S$5M</td><td><strong>5%</strong></td><td>S$250,000 on a S$5M sale</td></tr>
            <tr><td>S$5M – S$10M</td><td><strong>4%</strong></td><td>S$400,000 on a S$10M sale</td></tr>
            <tr><td>S$10M – S$20M</td><td><strong>3%</strong></td><td>S$600,000 on a S$20M sale</td></tr>
            <tr><td>S$20M – S$50M</td><td><strong>2%</strong></td><td>S$1,000,000 on a S$50M sale</td></tr>
            <tr><td>Above S$50M</td><td><strong>1%</strong></td><td>—</td></tr>
          </tbody>
        </table>
      </div>
      <p class="reveal mt-1">Minimum fee: <strong>S$100,000</strong>. Payable only on completion, out of sale proceeds. No retainers, no marketing charges, no monthly fees, no charge if the business doesn't sell.</p>

      <h2 class="reveal">The honest fine print, above the fold</h2>
      <ul class="reveal">
        <li><strong>The minimum fee has a floor effect.</strong> On a S$1M sale, S$100,000 is effectively 10% — so our process realistically suits transactions of about <strong>S$1.5M and above</strong>. Smaller than that, a marketplace listing is usually the better economic choice, and we'll tell you so on the first call.</li>
        <li><strong>Exclusivity is part of the deal.</strong> Running a credible process — approaching buyers, opening a data room, managing offers — requires an exclusive mandate for an agreed period. That's standard across serious advisors; walk away from anyone who demands it <em>and</em> a retainer <em>and</em> won't publish their fees.</li>
        <li><strong>Buy-side is separate and disclosed.</strong> Buyers we introduce pay a 1% success-only finder's fee for process services on their side. Both fees are disclosed to both parties — no hidden double-dipping.</li>
      </ul>

      <h2 class="reveal">How this compares with the market</h2>
      <div class="table-wrap reveal">
        <table>
          <thead><tr><th scope="col">Model</th><th scope="col">Typical cost</th><th scope="col">Watch for</th></tr></thead>
          <tbody>
            <tr><td>Traditional broker</td><td>5–10% success fee</td><td>Rates often unpublished; quoted after they've sized you up</td></tr>
            <tr><td>M&amp;A advisory firm</td><td>Retainer S$5k–S$25k/month + success fee</td><td>You pay whether or not it sells</td></tr>
            <tr><td>Marketplace listing</td><td>Listing fee or small commission</td><td>You run the sale yourself — screening, NDAs, negotiation, DD</td></tr>
            <tr><td><strong>This firm</strong></td><td><strong>1–5% success-only, published above</strong></td><td>S$100k minimum — unsuitable below ~S$1.5M</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <section class="on-light" style="padding-top:0">
    <div class="container">
      <div class="section-head reveal"><h2>Fee questions, answered</h2></div>
      <div class="reveal" style="max-width:820px">
        {faq_html(faqs_fees)}
      </div>
    </div>
  </section>
''',
    "cta_h": "Zero fees until the day you're paid.",
    "cta_p": "Ask us anything about the fee schedule on WhatsApp — including whether your business is the right size for it.",
    "cta_wa": "Hi, I have a question about your fees for selling a business.",
})
PAGES[-1]["schema"] = [faq_schema(faqs_fees), breadcrumb_schema("Fees", "fees")]

# ---- How It Works ----
faqs_how = [
    ("Can I stop the process at any point?",
     "Yes. Until you sign a term sheet with a buyer, you can pause or withdraw — owners sometimes do when circumstances change. Because fees are success-only, stopping costs you nothing beyond the time invested."),
    ("Who actually meets the buyers?",
     "Early conversations happen without you — buyers are screened and scored first. You meet only shortlisted, NDA-signed, financially capable buyers, usually two to four of them, with the meetings prepared and accompanied."),
    ("What is a term sheet?",
     "A short document — usually two to five pages — recording the agreed price, deal structure, transition period and key conditions before lawyers draft the full sale and purchase agreement. It's mostly non-binding, but it sets the anchor for everything that follows, which is why negotiating it well matters."),
    ("What does due diligence actually check?",
     "The buyer's accountants and lawyers verify what they're buying: financial statements against bank records, tax and CPF compliance, contracts and licences, employment records, and any litigation. Prepared sellers sail through it; unprepared ones lose deals or get re-traded on price. Preparation starts in stage two precisely for this reason."),
    ("Do I have to stay on after the sale?",
     "Usually for a agreed transition period — commonly three to twelve months, sometimes shorter for management-run businesses. It's a negotiated term, not an obligation, and it's often what gets a nervous buyer to full price."),
    ("What are the most common reasons deals fall through?",
     "Four causes account for most failed sales: financial records that don't survive due diligence, revenue dipping mid-process because the owner got distracted, price expectations set above what any evidence supports, and slow responses that let momentum die. Every one of them is preventable — which is why preparation, a maintained business and a managed timetable are stages of the process, not suggestions."),
    ("Can I run the sale while living overseas?",
     "Yes. The process is built to run remotely: conversations over WhatsApp and video calls, documents through a controlled data room, and signings that can be done electronically or through your Singapore corporate secretary. Owners who have relocated — or are mid-relocation — sell Singapore businesses this way routinely. Buyer meetings are scheduled around your time zone, and a local advisor being physically present for viewings and negotiations is precisely what you're engaging us for."),
]
PAGES.append({
    "slug": "how-it-works",
    "crumb": "How It Works",
    "title": "How to Sell a Business in Singapore — The 7-Stage Process",
    "description": "The seven stages of selling a business in Singapore — from confidential valuation to completion, with timelines for each stage.",
    "h1": "The seven stages of a well-run business sale.",
    "lead": "Six to eight months, seven stages, one rule throughout: nothing about your identity moves without your approval. Here's what actually happens, stage by stage.",
    "schema": [],
    "main": f'''
  <section>
    <div class="container">
      <div class="timeline" style="max-width:820px">
        <div class="t-line"></div>
        <div class="t-step reveal" style="--i:0"><span class="dot">1</span><span class="t-meta">Weeks 1–2 · Confidential discussion</span><h3>Fit and goals</h3><p>A 30-minute conversation — WhatsApp, call, or coffee. Your goals, your timeline, a first sense of value. No documents required, no fee, no obligation. If selling now isn't right, we'll say so; some of the best outcomes start with “wait 18 months and fix these two things.”</p></div>
        <div class="t-step reveal" style="--i:1"><span class="dot">2</span><span class="t-meta">Weeks 2–6 · Valuation &amp; preparation</span><h3>Know what it's worth — and make it worth more</h3><p>Three years of financials analysed, EBITDA adjustments identified line by line, a defensible valuation range built against sector multiples. At the same time: quick wins that raise value — cleaning up related-party items, documenting processes, tidying contracts.</p></div>
        <div class="t-step reveal" style="--i:2"><span class="dot">3</span><span class="t-meta">Month 2 · Marketing materials</span><h3>The blind teaser and the IM</h3><p>Two documents: a no-name teaser (sector, revenue band, strengths — nothing identifying) shown to prospective buyers, and a full information memorandum released only after an NDA is signed. You approve both before anything moves.</p></div>
        <div class="t-step reveal" style="--i:3"><span class="dot">4</span><span class="t-meta">Months 2–4 · Buyer search &amp; screening</span><h3>Finding the right buyers, quietly</h3><p>Targeted outreach to strategic acquirers, investors and qualified operators. Every respondent is scored on intent, fit and financial capability. Only NDA-signed, capable, shortlisted buyers are introduced — and you approve each introduction personally.</p></div>
        <div class="t-step reveal" style="--i:4"><span class="dot">5</span><span class="t-meta">Months 4–5 · Offers &amp; negotiation</span><h3>Competing offers to a signed term sheet</h3><p>Offers are brought to the table together, compared on price <em>and</em> structure, transition terms and certainty of completion. Negotiation runs until one buyer signs a term sheet on terms you're happy with.</p></div>
        <div class="t-step reveal" style="--i:5"><span class="dot">6</span><span class="t-meta">Months 5–7 · Due diligence</span><h3>Verification, managed</h3><p>The buyer's accountants and lawyers verify the business through a controlled data room — access granted per buyer, per document, fully logged. Questions are coordinated so the process stays on schedule and your team stays unaware.</p></div>
        <div class="t-step reveal" style="--i:6"><span class="dot">7</span><span class="t-meta">Months 7–8 · Completion &amp; handover</span><h3>Signed, paid, handed over well</h3><p>Lawyers finalise the sale and purchase agreement; completion mechanics move the money and the shares. Then the part that protects your legacy: a planned handover to staff and customers, on the timing and terms negotiated in stage five.</p></div>
      </div>
    </div>
  </section>

  <section class="on-light" style="padding-top:0">
    <div class="container">
      <div class="section-head reveal"><h2>Process questions, answered</h2></div>
      <div class="reveal" style="max-width:820px">
        {faq_html(faqs_how)}
      </div>
    </div>
  </section>
''',
    "cta_wa": "Hi, I'd like to understand the process of selling my business. Can we have a confidential chat?",
})
PAGES[-1]["schema"] = [faq_schema(faqs_how), breadcrumb_schema("How It Works", "how-it-works")]

# ---- F&B ----
faqs_fnb = [
    ("How much can I sell my F&B business for in Singapore?",
     "Profitable F&B businesses in Singapore typically sell for 2.5–5× adjusted EBITDA. A restaurant group or food manufacturer earning S$600,000 adjusted EBITDA would indicatively fetch S$1.5M–S$3M, with central kitchens, food manufacturing licences and strong brands commanding the upper end."),
    ("Do SFA licences transfer to the buyer?",
     "In a share sale, licences held by the company — SFA food shop or food processing licences, liquor licences, halal certification — generally remain with the company and continue uninterrupted, though some require notification of the change in shareholding. In an asset sale, the buyer must apply afresh. This is one of the main reasons F&B deals are usually structured as share sales."),
    ("What about my shop lease?",
     "The lease often matters as much as the P&L. Landlord consent is typically required for a change of control, and remaining tenure affects value — a prime location with six years remaining is an asset; eight months remaining is a discount. We review lease terms in stage two, before buyers ever see the business."),
    ("Will my head chef and managers find out?",
     "Not through the sale process. Marketing is no-name, buyers sign NDAs before learning the identity, and site visits are arranged discreetly — typically as ordinary customer visits. Staff learn of the transition when you decide, usually at completion with the handover plan agreed."),
    ("Is a loss-making F&B outlet sellable?",
     "Sometimes — on the value of the location, the fitted premises, licences, or the brand rather than earnings. The price reflects that basis instead of an EBITDA multiple. Message us with the situation; the honest answer might be a trade sale, an asset sale, or closing well — we'll tell you which."),
]
PAGES.append({
    "slug": "sell-your-fnb-business-singapore",
    "crumb": "Sell Your F&B Business",
    "title": "Sell an F&B Business in Singapore — Broker for Restaurants",
    "description": "How to sell an F&B business in Singapore: 2.5–5× EBITDA multiples, SFA licences, lease transfer and a confidential sale process.",
    "h1": "Selling an F&B business in Singapore, done properly.",
    "lead": "Restaurants, central kitchens, catering, food brands and food manufacturers — F&B is Singapore's most active SME deal sector, and the one where confidentiality and licensing details decide whether a deal completes.",
    "schema": [],
    "main": f'''
  <section>
    <div class="container prose">
      <div class="answer-first reveal">
        <p><strong>To sell an F&amp;B business in Singapore</strong>, expect 2.5–5× adjusted EBITDA for profitable operations, structured as a share sale so SFA licences, halal certification and the lease stay with the company. The process runs no-name until buyers sign NDAs — critical in a sector where staff and landlord rumours can damage the business overnight.</p>
      </div>

      <h2 class="reveal">Why F&amp;B deals are different</h2>
      <div class="grid-2 mt-2">
        <div class="card reveal" style="--i:0"><h3>Licences are the moat</h3><p>SFA food processing licences, liquor licences, halal certification — hard to obtain, valuable to transfer. A share sale keeps them with the company; buyers pay for that continuity.</p></div>
        <div class="card reveal" style="--i:1"><h3>The lease is half the deal</h3><p>Location tenure, rent trajectory and landlord consent for change of control get reviewed before marketing — not discovered in due diligence.</p></div>
        <div class="card reveal" style="--i:2"><h3>Rumours are expensive</h3><p>If staff or suppliers hear “the boss is selling,” the damage is immediate. F&amp;B demands the strictest no-name process — even site visits are staged as customer visits.</p></div>
        <div class="card reveal" style="--i:3"><h3>Buyers are plentiful</h3><p>Regional F&amp;B groups, consolidators, central-kitchen operators and first-time acquirers are all active in Singapore. Competition among them is what moves the multiple.</p></div>
      </div>

      <h2 class="reveal">What F&amp;B buyers pay for</h2>
      <ul class="reveal">
        <li><strong>Earnings quality</strong> — consistent adjusted EBITDA across outlets, not one good year.</li>
        <li><strong>Systems over personalities</strong> — recipes documented, kitchen ops running without the founder, a manager layer in place.</li>
        <li><strong>Brand and repeat custom</strong> — delivery-platform ratings, corporate accounts, catering contracts.</li>
        <li><strong>Capacity</strong> — a central kitchen or SFA-licensed production facility with headroom is a growth story buyers will pay up for.</li>
      </ul>
      <p class="reveal">Multi-outlet groups and food manufacturers with S$2M–S$20M revenue attract the strongest buyer competition. See <a href="/business-valuation-singapore/">how valuation works</a> or get an instant range from the <a href="/#valuation">free estimator</a>.</p>
    </div>
  </section>

  <section class="on-light" style="padding-top:0">
    <div class="container">
      <div class="section-head reveal"><h2>F&amp;B seller questions, answered</h2></div>
      <div class="reveal" style="max-width:820px">
        {faq_html(faqs_fnb)}
      </div>
    </div>
  </section>
''',
    "cta_h": "Own an F&B business? Start the quiet conversation.",
    "cta_p": "Tell us the shape of the business on WhatsApp — sector, outlets, rough revenue. You'll get a straight view on value and buyer appetite. Nobody else hears about it.",
    "cta_wa": "Hi, I own an F&B business in Singapore and I'm exploring a confidential sale.",
})
PAGES[-1]["schema"] = [faq_schema(faqs_fnb), breadcrumb_schema("Sell Your F&B Business", "sell-your-fnb-business-singapore"),
                       service_schema("Sell an F&B business in Singapore", "Sell-side business brokerage for F&B businesses")]

# ---- Buy a Business ----
faqs_buy = [
    ("How do I buy a business in Singapore?",
     "Define your acquisition criteria (sector, size, price range), get access to deal flow, sign NDAs to review information memoranda, submit offers, then complete due diligence and the sale and purchase agreement. Working with a broker who holds sell-side mandates gives you access to businesses that never appear on public marketplaces."),
    ("What does the 1% buy-side fee cover?",
     "Screened deal flow matched to your criteria, process management from first review to completion, coordination of the data room and due diligence, and negotiation logistics. It's success-only — 1% of transaction value, payable only if you complete an acquisition we introduced. Our sell-side fee is disclosed to you, and this fee is disclosed to the seller; both sides see the full picture."),
    ("Aren't you acting for the seller?",
     "On mandated deals, yes — the seller is our client, and buyers should know that plainly. The 1% buy-side fee pays for buyer process services, not divided loyalty: you get vetted deal flow, organised information and a professionally run process. Serious buyers prefer a well-run sell-side process over a chaotic one."),
    ("What information do I get before signing an NDA?",
     "A no-name teaser: sub-sector, revenue and EBITDA bands, key strengths, reason for sale, and deal-readiness signals. Enough for you to decide whether to proceed. Identity, financial statements and the full information memorandum come after the NDA — that staging is what lets serious sellers come to market at all."),
]
PAGES.append({
    "slug": "buy-a-business-singapore",
    "crumb": "Buy a Business",
    "title": "Buy a Business in Singapore — Off-Market SME Deal Flow",
    "description": "Buy an established Singapore SME: off-market deal flow from mandated sellers, S$2M–S$20M revenue, 1% success-only buyer fee.",
    "h1": "Buy an established Singapore business — before it hits the market.",
    "lead": "Our mandates are sell-side: committed sellers, prepared financials, and a structured process. Registered buyers see opportunities that never reach public marketplaces.",
    "schema": [],
    "hero_ctas": f'''<div class="hero-ctas" style="margin-top:1.8rem">
        <a class="btn btn-wa" href="{wa_link("Hi, I'm interested in acquiring a business in Singapore. My criteria: [sector / size / budget]")}">{wa_icon()} Register Acquisition Criteria</a>
      </div>''',
    "main": f'''
  <section>
    <div class="container prose">
      <h2 class="reveal">What registered buyers receive</h2>
      <div class="grid-2 mt-2">
        <div class="card reveal" style="--i:0"><h3>Off-market deal flow</h3><p>No-name teasers matched to your criteria — sub-sector, revenue and EBITDA bands, deal-readiness — from owners who would never list publicly.</p></div>
        <div class="card reveal" style="--i:1"><h3>Committed sellers</h3><p>Every mandate is exclusive and prepared: valuation done, information memorandum ready, financials organised. No tyre-kicking sellers wasting your diligence budget.</p></div>
        <div class="card reveal" style="--i:2"><h3>A process that moves</h3><p>Staged disclosure under NDA, a managed data room, coordinated Q&amp;A, and momentum through to completion — typically 6–8 months end to end.</p></div>
        <div class="card reveal" style="--i:3"><h3>Success-only 1% fee</h3><p>1% of transaction value, payable only on completion of a deal we introduced. Disclosed to both sides, alongside the seller's fee. No retainers, no subscription.</p></div>
      </div>

      <h2 class="reveal">Who buys through us</h2>
      <p class="reveal">Strategic and trade buyers consolidating their sector, regional companies entering Singapore, family offices and search funds, and experienced owner-operators. Typical targets: profitable Singapore SMEs with S$2M–S$20M revenue in F&amp;B, manufacturing, distribution, services and logistics.</p>

      <h2 class="reveal">How to register</h2>
      <p class="reveal">Send your acquisition criteria on WhatsApp — sector, size range, budget, and whether you've acquired before. You'll be notified when a mandate matches. Criteria are held confidentially and never shared with sellers without your consent.</p>
    </div>
  </section>

  <section class="on-light" style="padding-top:0">
    <div class="container">
      <div class="section-head reveal"><h2>Buyer questions, answered</h2></div>
      <div class="reveal" style="max-width:820px">
        {faq_html(faqs_buy)}
      </div>
    </div>
  </section>
''',
    "cta_h": "Tell us what you're looking to acquire.",
    "cta_p": "Sector, size, budget — one WhatsApp message registers your criteria for matching against current and future mandates.",
    "cta_wa": "Hi, I'm interested in acquiring a business in Singapore. My criteria: [sector / size / budget]",
})
PAGES[-1]["schema"] = [faq_schema(faqs_buy), breadcrumb_schema("Buy a Business", "buy-a-business-singapore"),
                       service_schema("Buy a business in Singapore", "Business acquisition deal flow for registered buyers")]

# ---- Contact ----
PAGES.append({
    "slug": "contact",
    "crumb": "Contact",
    "title": "Contact a Business Broker in Singapore — Confidential",
    "description": "Start a confidential conversation about selling or buying a Singapore business. WhatsApp us — no fee, no obligation, your name stays private.",
    "h1": "One message starts the conversation.",
    "lead": "WhatsApp is fastest — you'll reach a person, not a call centre. Every conversation is confidential from the first word, whether you're a year from selling or ready now.",
    "schema": [breadcrumb_schema("Contact", "contact")],
    "hero_ctas": f'''<div class="hero-ctas" style="margin-top:1.8rem">
        <a class="btn btn-wa" href="{wa_link("Hi, I'd like a confidential conversation.")}">{wa_icon()} WhatsApp +65 8951 8821</a>
      </div>''',
    "main": f'''
  <section>
    <div class="container">
      <div class="grid-3">
        <div class="card reveal" style="--i:0">
          <h3>Selling a business</h3>
          <p>A confidential 30-minute conversation about value, timing and fit. No documents needed. Bringing your spouse or an adult son or daughter to the call is welcome.</p>
          <a class="btn btn-wa mt-1" href="{wa_link("Hi, I'm thinking about selling my business and would like a confidential conversation.")}">{wa_icon()} Start seller chat</a>
        </div>
        <div class="card reveal" style="--i:1">
          <h3>Buying a business</h3>
          <p>Send your acquisition criteria — sector, size, budget — and get matched against current and future off-market mandates.</p>
          <a class="btn btn-wa mt-1" href="{wa_link("Hi, I'm interested in acquiring a business in Singapore. My criteria: [sector / size / budget]")}">{wa_icon()} Register as buyer</a>
        </div>
        <div class="card reveal" style="--i:2">
          <h3>Professional referrals</h3>
          <p>Lawyers, accountants, corporate secretaries and bankers with a client considering a transition — your client gets senior, same-day, white-glove handling.</p>
          <a class="btn btn-wa mt-1" href="{wa_link("Hi, I'm a professional advisor with a client who may be considering a business sale.")}">{wa_icon()} Refer a client</a>
        </div>
      </div>
      <p class="reveal mt-3" style="max-width:680px;color:var(--slate);font-size:0.95rem">Prefer not to message first? Use the <a href="/#valuation">free valuation estimator</a> — it runs entirely in your browser and sends nothing until you choose to.</p>
    </div>
  </section>
''',
    "cta_h": "Confidential, from the first word.",
    "cta_p": "No fee, no obligation, no name disclosed until you decide. That's the standing arrangement — not a promotion.",
    "cta_wa": "Hi, I'd like a confidential conversation.",
})

# ---- FAQ hub ----
faqs_hub_timing = [
    ("How long does it take to sell a business in Singapore?",
     "Six to eight months from first conversation to money in the bank is typical for a prepared, realistically priced Singapore SME. Well-prepared businesses in active sectors can complete in four to five; licence-heavy or complex deals can run nine to twelve. The biggest variable isn't the market — it's how clean the financial records are and how quickly each side responds once offers are on the table."),
    ("When is the best time to sell my business?",
     "When it's performing — not when you're exhausted or the numbers have turned. Buyers pay for trajectory, so the best exits are planned 12–24 months ahead: enough time to normalise the accounts, reduce owner-dependence and go to market on strength. Market cycles matter far less than your business's own curve. If circumstances force a faster sale, a structured process still beats a distressed one."),
    ("Is my business big enough to sell?",
     "Our process suits profitable businesses with roughly S$2M–S$20M annual revenue or adjusted EBITDA above about S$300,000 — the range where serious trade buyers, family offices and search funds actively acquire in Singapore. Below that, the economics of a full sell-side process stop making sense for you, and a marketplace listing is often the better route. Message us either way — we'll tell you honestly which side of the line you're on."),
    ("What should I prepare before speaking to a broker?",
     "Nothing, for the first conversation — it's thirty minutes on WhatsApp or a call about your goals, timeline and whether a sale makes sense at all. If you engage, the working documents come later: three years of financial statements, management accounts, ACRA records, key contracts and leases. Don't reorganise or 'tidy' anything first; advisors would rather see the real picture early than discover surprises in due diligence."),
]
faqs_hub_money = [
    ("Do I pay tax when I sell my business in Singapore?",
     "Singapore has no capital gains tax, so for most owners selling shares in their Pte Ltd, the sale proceeds are not taxed. The main caveats: IRAS can treat gains as taxable income if buying and selling companies is effectively your trade; buyers pay stamp duty of 0.2% on share transfers; and asset sales are different — the company may be taxed on gains over book value and GST can apply. Structure decides the outcome, which is why it's negotiated early. We coordinate with your tax advisor before terms are locked."),
    ("Do I keep the cash in the company's bank account when I sell?",
     "Effectively, yes. Singapore SME deals are typically priced 'cash-free, debt-free': the headline price assumes you extract excess cash (usually as a tax-free dividend before completion) and settle borrowings, leaving an agreed normal level of working capital in the business. That working-capital level is a negotiated number — one of those quiet terms that can move the real proceeds by six figures."),
    ("How much does it cost to sell a business in Singapore?",
     "Brokers in Singapore typically charge 5–10% of the sale price, some with upfront or monthly retainers. Our schedule is published and success-only: 5% up to S$5M, stepping down to 1% above S$50M, minimum S$100,000, zero upfront — we're paid from the proceeds when you are. Your other costs are your own lawyer for the sale agreement and, in some deals, a tax opinion. See the full breakdown on the <a href='/fees/'>fees page</a>."),
]
faqs_hub_conf = [
    ("Can I sell my business without staff, customers or competitors finding out?",
     "Yes — this is standard practice, not a special request. The business is marketed under a no-name 'blind profile'; buyers are screened and financially qualified first, sign an NDA before your identity is revealed, and receive sensitive information in stages inside a controlled data room. Your staff typically learn of the sale when you announce it — after completion, with the future secured. The full mechanism is explained on the <a href='/'>home page</a>."),
    ("What if an interested buyer is really a competitor fishing for information?",
     "It happens, and the process is built for it. Every buyer is scored on intent and capability before any disclosure; NDAs carry non-solicitation clauses covering your staff and customers; and the data room releases information in stages — customer names, pricing and supplier terms come last, after price and structure are already agreed. A competitor who is genuinely the best buyer can stay in the process; one who's fishing never gets past the shallow end."),
]
faqs_hub_special = [
    ("What if my business partner doesn't want to sell?",
     "You generally can't force a co-shareholder to sell, and most SME constitutions give them pre-emption rights over your stake — but deadlock is more solvable than it feels. A market-tested valuation turns an emotional stand-off into an arithmetic conversation: the reluctant partner can buy you out at the evidenced price, join the sale, or accept terms that protect their position under the new owner. We've run each of these plays; the first step is a valuation neither side can argue with."),
    ("My children don't want to take over the business. What are my options?",
     "You're in the majority — most Singapore SME successions now end in a sale, not a handover. The good news: a sale done while the business is performing converts your life's work into retirement capital, and the things succession was meant to protect — staff, brand, customers — become negotiated terms of the deal. Many of our sellers are exactly here: sixties, profitable business, no successor. The earlier the conversation starts, the more options stay open."),
    ("Can a foreign buyer acquire my Singapore company?",
     "Yes. Singapore places no general restriction on foreign ownership of private companies — regional trade buyers, Southeast Asian consolidators and international investors are among the most active acquirers of Singapore SMEs, and often the best payers. A few licensed sectors require regulatory notification or approval on change of control, which is checked in preparation, not discovered in due diligence. Completion mechanics are the same; funds flow through the same escrow protections."),
]
faqs_hub_broker = [
    ("Do I need a broker, or can I sell the business myself?",
     "You can sell yourself — owners do. But one buyer negotiating against an inexperienced seller sets their own price, and running a six-to-eight-month process while managing the company is where self-run sales most often die. A broker's case rests on three things: competitive tension between several vetted buyers, a shield that keeps the sale confidential and you out of the firing line, and the business staying on-curve because you never stopped running it. The <a href='/sell-your-business-singapore/'>sell your business page</a> covers what that looks like in practice."),
    ("How is a business broker different from an M&A advisor?",
     "Mostly scale and depth of process. 'Business broker' usually means marketplace listings and smaller transactions; 'M&A advisory' means a managed sell-side process — valuation evidence, targeted buyer outreach, structured negotiation, due diligence management — for larger deals. For Singapore SMEs in the S$2M–S$20M revenue range, what matters isn't the label but whether your advisor runs a real process. Ours is sell-side M&A methodology applied at SME scale, on success-only broker economics."),
]
_hub_all = faqs_hub_timing + faqs_hub_money + faqs_hub_conf + faqs_hub_special + faqs_hub_broker

def _hub_section(title, faqs, i):
    return f'''<h2 class="reveal" style="margin-top:{'0' if i == 0 else '3rem'}">{title}</h2>
      <div class="reveal">
        {faq_html(faqs)}
      </div>'''

PAGES.append({
    "slug": "faq",
    "crumb": "FAQ",
    "title": "Selling a Business in Singapore — FAQ",
    "description": "Straight answers for Singapore business owners: tax on sale proceeds, timelines, confidentiality, foreign buyers and broker fees.",
    "h1": "Questions owners ask before selling — answered straight.",
    "lead": "Everything sellers ask us before the first call: what a sale costs, what gets taxed, how long it takes, who finds out, and what happens in the hard cases. Short answers here; deeper pages linked throughout.",
    "schema": [],
    "main": f'''
  <section>
    <div class="container" style="max-width:820px">
      <div class="answer-first reveal">
        <p><strong>Selling a business in Singapore</strong> typically takes 6–8 months, costs a success-only fee of 1–5% of the sale price, and — because Singapore has no capital gains tax — usually leaves the share-sale proceeds untaxed in your hands. It can be done without staff, customers or competitors knowing until you choose to tell them. The details, case by case, are below.</p>
      </div>

      {_hub_section("Timing and size", faqs_hub_timing, 0)}
      {_hub_section("Money and tax", faqs_hub_money, 1)}
      {_hub_section("Confidentiality", faqs_hub_conf, 2)}
      {_hub_section("Partners, family and special situations", faqs_hub_special, 3)}
      {_hub_section("Working with a broker", faqs_hub_broker, 4)}

      <p class="reveal mt-3" style="color:var(--slate)">Looking for numbers instead? See <a href="/business-valuation-singapore/">how valuation works</a>, the <a href="/fees/">published fee schedule</a>, or the <a href="/how-it-works/">seven-stage process</a>. Question not here? Ask it directly — that's what the WhatsApp line is for.</p>
    </div>
  </section>
''',
    "cta_h": "Your question, answered by a person.",
    "cta_p": "Thirty minutes, confidential, no obligation. Ask the question you didn't find above — you'll get a straight answer either way.",
    "cta_wa": "Hi, I have a question about selling my business in Singapore.",
})
PAGES[-1]["schema"] = [faq_schema(_hub_all), breadcrumb_schema("FAQ", "faq")]

# ============================== WRITE ==============================
for page in PAGES:
    path = os.path.join(ROOT, page["slug"], "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(shell(page))
    print("wrote", path)
