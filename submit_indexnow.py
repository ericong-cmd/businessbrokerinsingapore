#!/usr/bin/env python3
"""Ping IndexNow with every URL in sitemap.xml.

IndexNow notifies Bing (and Yandex, Seznam, Naver) immediately instead of waiting
to be crawled. Bing's index is what ChatGPT search reads, so this is an AEO
channel as much as an SEO one. Google does not participate.

The key file must be reachable at https://www.businessbrokerinsingapore.com/<key>.txt
and contain exactly the key — it is committed at the repo root.

Usage: python3 submit_indexnow.py
"""
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
HOST = "www.businessbrokerinsingapore.com"
ENDPOINT = "https://api.indexnow.org/IndexNow"

keys = [f for f in glob.glob(os.path.join(ROOT, "*.txt"))
        if re.fullmatch(r"[0-9a-f]{32}", os.path.basename(f)[:-4] or "")]
if not keys:
    sys.exit("No IndexNow key file (<32-hex>.txt) found at the repo root.")
key = os.path.basename(keys[0])[:-4]

sitemap = open(os.path.join(ROOT, "sitemap.xml")).read()
urls = re.findall(r"<loc>(.*?)</loc>", sitemap)
if not urls:
    sys.exit("No URLs found in sitemap.xml")

payload = {
    "host": HOST,
    "key": key,
    "keyLocation": f"https://{HOST}/{key}.txt",
    "urlList": urls,
}
req = urllib.request.Request(ENDPOINT, method="POST",
                             data=json.dumps(payload).encode())
req.add_header("Content-Type", "application/json; charset=utf-8")
try:
    with urllib.request.urlopen(req) as r:
        # 200 = accepted, 202 = accepted but key still being validated
        print(f"IndexNow HTTP {r.status} — submitted {len(urls)} URLs")
except urllib.error.HTTPError as e:
    sys.exit(f"IndexNow HTTP {e.code}: {e.read().decode()[:300]}")
