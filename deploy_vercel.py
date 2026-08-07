#!/usr/bin/env python3
"""One-shot Vercel deploy for businessbrokerinsingapore.com.

Deploys every file in this directory to the Vercel project
`businessbrokerinsingapore` (created if missing), promotes it to production,
attaches the custom domains, and prints the DNS records to configure.

Requires: a Vercel personal access token in env var `vercel` or VERCEL_TOKEN.
Usage:    python3 deploy_vercel.py
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.vercel.com"
PROJECT = "businessbrokerinsingapore"
APEX = "businessbrokerinsingapore.com"
WWW = "www." + APEX
EXCLUDE = {".git", ".gitignore", "build_pages.py", "deploy_vercel.py",
           "deploy.yml.example", "README.md", "gfonts.css"}

TOKEN = os.environ.get("vercel") or os.environ.get("VERCEL_TOKEN")
if not TOKEN:
    sys.exit("No Vercel token: set env var `vercel` or VERCEL_TOKEN")

def api(method, path, body=None, ok_conflict=False):
    req = urllib.request.Request(API + path, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    data = None
    if body is not None:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(req, data) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        if ok_conflict and e.code in (409, 400) and "already" in detail.lower():
            return {"conflict": True}
        raise SystemExit(f"{method} {path} -> HTTP {e.code}: {detail[:500]}")

user = api("GET", "/v2/user")["user"]
print(f"Authenticated as {user.get('username')} ({user.get('email')})")

api("POST", "/v11/projects", {"name": PROJECT, "framework": None}, ok_conflict=True)
print(f"Project ready: {PROJECT}")

root = os.path.dirname(os.path.abspath(__file__))
files, total = [], 0
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE]
    for fn in filenames:
        rel = os.path.relpath(os.path.join(dirpath, fn), root)
        if fn in EXCLUDE or rel in EXCLUDE:
            continue
        raw = open(os.path.join(dirpath, fn), "rb").read()
        total += len(raw)
        files.append({"file": rel, "data": base64.b64encode(raw).decode(),
                      "encoding": "base64"})
print(f"Uploading {len(files)} files ({total // 1024} KB)")

dep = api("POST", "/v13/deployments", {
    "name": PROJECT, "project": PROJECT, "target": "production",
    "files": files, "projectSettings": {"framework": None},
})
dep_id, dep_url = dep["id"], "https://" + dep["url"]
print(f"Deployment created: {dep_url}")

for _ in range(60):
    state = api("GET", f"/v13/deployments/{dep_id}")["readyState"]
    if state == "READY":
        print("Deployment READY")
        break
    if state in ("ERROR", "CANCELED"):
        sys.exit(f"Deployment failed: {state}")
    time.sleep(5)
else:
    sys.exit("Timed out waiting for deployment")

api("POST", f"/v10/projects/{PROJECT}/domains", {"name": WWW}, ok_conflict=True)
api("POST", f"/v10/projects/{PROJECT}/domains",
    {"name": APEX, "redirect": WWW, "redirectStatusCode": 308}, ok_conflict=True)
print(f"Domains attached: {WWW} (primary), {APEX} (308 redirect)")

print("\n--- DNS records to set at the domain registrar ---")
for domain in (APEX, WWW):
    cfg = api("GET", f"/v6/domains/{domain}/config")
    status = "OK" if not cfg.get("misconfigured") else "NEEDS DNS"
    rec = ("A     @    76.76.21.21" if domain == APEX
           else "CNAME www  cname.vercel-dns.com")
    print(f"{domain}: {status}   expected: {rec}")

print(f"\nLive at: {dep_url}  (production alias follows once DNS resolves)")
