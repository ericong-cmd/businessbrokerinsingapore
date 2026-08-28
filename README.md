# businessbrokerinsingapore.com

Lead-generation website for **Business Broker In Singapore** — a confidential
sell-side business brokerage for Singapore SME owners.

Static site: no build step, no framework, no dependencies. Semantic HTML,
one CSS file, one vanilla JS file (~8KB) driving scroll reveals, animated
counters, the FAQ accordions and the valuation estimator. All lead capture
routes to WhatsApp (`wa.me` links) — there is no form backend.

## Structure

| Path | Target query |
|---|---|
| `/` | business broker Singapore |
| `/sell-your-business-singapore/` | sell my business Singapore |
| `/business-valuation-singapore/` | business valuation Singapore |
| `/fees/` | business broker fees Singapore |
| `/how-it-works/` | how to sell a business in Singapore |
| `/sell-your-fnb-business-singapore/` | sell F&B business Singapore |
| `/buy-a-business-singapore/` | buy a business Singapore |
| `/faq/` | selling a business Singapore FAQ |
| `/about/` | entity / E-E-A-T page |
| `/contact/` | — |

Every page carries a JSON-LD `@graph` — `ProfessionalService` (with the
operating entity, UEN and registered address) and `WebSite` sitewide, plus
`FAQPage`, `BreadcrumbList`, `Service`, `AboutPage` or `ContactPage` as
applicable — an og:image and Twitter card, the footer entity line, and an
AEO-style direct-answer first paragraph.

## Build

`python3 build_pages.py` regenerates every interior page from the shared
shell, plus `llms.txt` and `sitemap.xml` (whose `lastmod` values come from
each page's real git commit date). The homepage `index.html` and `404.html`
are hand-maintained — mirror shell changes into them by hand.

Answer engines: `robots.txt` explicitly allows GPTBot, OAI-SearchBot,
ClaudeBot, PerplexityBot, Google-Extended, CCBot and Bytespider; `llms.txt`
maps the site for them; every FAQ question has a stable `id` anchor so
individual answers are directly citable.

After deploying a content change, run `python3 submit_indexnow.py` to push
the sitemap URLs to IndexNow (Bing, and therefore ChatGPT search). The
`<32-hex>.txt` key file at the repo root must stay published.

## Deployment

Pushes to `main` deploy to Vercel production via GitHub Actions
(`.github/workflows/deploy.yml`), which also attaches the custom domain.
Requires the `VERCEL_TOKEN` repository secret.

DNS at the registrar:

| Type | Name | Value |
|---|---|---|
| A | @ | 76.76.21.21 |
| CNAME | www | cname.vercel-dns.com |

## Editing

- Interior pages share a common shell; edit them directly, or regenerate
  consistently if making structural changes across all pages.
- The valuation estimator's sector multiples live in
  `assets/js/main.js` (`MULTIPLES`) and mirror the table on
  `/business-valuation-singapore/` — keep the two in sync.
- WhatsApp number is `+65 8951 8821`, appearing in `wa.me` links across
  all pages and in `assets/js/main.js` (`WA_NUMBER`).
