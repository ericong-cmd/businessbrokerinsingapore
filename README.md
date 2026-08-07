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
| `/contact/` | — |

Every page carries JSON-LD (`ProfessionalService`, `FAQPage`,
`BreadcrumbList`) and an AEO-style direct-answer first paragraph.

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
