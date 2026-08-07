import threading
import traceback
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response

import database as db
from config import SOURCES, SOURCE_MAP
from scrapers import SCRAPER_MAP

app = Flask(__name__)
app.secret_key = "tfa-scraper-secret-2024"

db.init_db()

# ── Template context ────────────────────────────────────────────────────────

@app.context_processor
def inject_sources():
    return {"sources": SOURCES}


# ── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    listings = db.get_listings(
        source=request.args.get("source") or None,
        search=request.args.get("q") or None,
        location=request.args.get("location") or None,
        industry=request.args.get("industry") or None,
    )
    stats = db.get_stats()
    return render_template("index.html", listings=listings, stats=stats)


@app.route("/listing/<int:listing_id>")
def listing_detail(listing_id):
    listing = db.get_listing_by_id(listing_id)
    if not listing:
        flash("Listing not found.", "warning")
        return redirect(url_for("index"))
    return render_template("listing.html", listing=listing)


@app.route("/export.csv")
def export_csv():
    csv_data = db.export_csv(
        source=request.args.get("source") or None,
        search=request.args.get("q") or None,
    )
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=business_listings.csv"},
    )


# ── API ───────────────────────────────────────────────────────────────────────

@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    body = request.get_json(silent=True) or {}
    source = body.get("source", "all")
    debug = body.get("debug", False)

    if source == "all":
        sources_to_run = list(SCRAPER_MAP.keys())
    elif source in SCRAPER_MAP:
        sources_to_run = [source]
    else:
        return jsonify({"error": f"Unknown source: {source}"}), 400

    run_ids = []
    for src_id in sources_to_run:
        run_id = db.start_scrape_run(src_id)
        run_ids.append(run_id)
        t = threading.Thread(
            target=_run_scraper,
            args=(src_id, run_id, debug),
            daemon=True,
        )
        t.start()

    return jsonify({"run_ids": run_ids, "sources": sources_to_run})


@app.route("/api/scrape-status/<int:run_id>")
def api_scrape_status(run_id):
    run = db.get_scrape_run(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404

    src_name = SOURCE_MAP.get(run["source"], {}).get("name", run["source"])
    if run["status"] == "running":
        message = f"Scraping {src_name}…"
    elif run["status"] == "done":
        message = f"{src_name}: {run['listings_found']} found, {run['listings_new']} new"
    else:
        message = f"{src_name}: error"

    return jsonify({
        "status": run["status"],
        "source": run["source"],
        "listings_found": run["listings_found"],
        "listings_new": run["listings_new"],
        "error": run["error"],
        "message": message,
    })


@app.route("/api/listings")
def api_listings():
    listings = db.get_listings(
        source=request.args.get("source") or None,
        search=request.args.get("q") or None,
        location=request.args.get("location") or None,
        industry=request.args.get("industry") or None,
        limit=int(request.args.get("limit", 200)),
        offset=int(request.args.get("offset", 0)),
    )
    return jsonify(listings)


# ── Scraper runner (background thread) ───────────────────────────────────────

def _run_scraper(source_id: str, run_id: int, debug: bool = False):
    scraper_cls = SCRAPER_MAP[source_id]
    scraper = scraper_cls(debug=debug)
    found = 0
    new = 0
    try:
        listings = scraper.scrape(max_pages=10)
        found = len(listings)
        for listing in listings:
            is_new = db.upsert_listing(listing.to_dict())
            if is_new:
                new += 1
        db.finish_scrape_run(run_id, found=found, new=new)
        print(f"[Runner] {source_id} done — {found} found, {new} new")
    except Exception as e:
        err = traceback.format_exc()
        print(f"[Runner] {source_id} ERROR:\n{err}")
        db.finish_scrape_run(run_id, found=found, new=new, error=str(e))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Business Listings Finder — The Funding Assembly")
    print("Dashboard: http://localhost:5000")
    print()
    app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
