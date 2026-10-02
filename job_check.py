#!/usr/bin/env python3
"""SWE / Data / ML intern + new-grad roles from the SimplifyJobs lists.

  python3 job_check.py 2.5            -> text digest of roles added in the last 2.5 hours (NO_NEW_ROLES if none)
  python3 job_check.py --json 14 OUT  -> write OUT (json) with roles from the last 14 days, for the web page
"""
import json, sys, time, urllib.request
from datetime import datetime, timezone, timedelta

REPOS = {"Intern": "Summer2027-Internships", "New Grad": "New-Grad-Positions"}
CATS = {"software", "ai/ml/data", "software engineering", "data science, ai & machine learning"}
ET = timezone(timedelta(hours=-4))

US_STATES = set("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC PR".split())
US_STATE_NAMES = {"alabama","alaska","arizona","arkansas","california","colorado","connecticut","delaware","florida","georgia","hawaii","idaho","illinois","indiana","iowa","kansas","kentucky","louisiana","maine","maryland","massachusetts","michigan","minnesota","mississippi","missouri","montana","nebraska","nevada","new hampshire","new jersey","new mexico","new york","north carolina","north dakota","ohio","oklahoma","oregon","pennsylvania","rhode island","south carolina","south dakota","tennessee","texas","utah","vermont","virginia","washington","west virginia","wisconsin","wyoming"}
US_ALIASES = {"nyc","sf","south sf","la","remote in usa","united states","usa","us","remote"}

def is_us(loc):
    s = loc.strip(); low = s.lower()
    if low in US_ALIASES or low in US_STATE_NAMES: return True
    if "usa" in low or "united states" in low: return True
    parts = [p.strip() for p in s.split(",")]
    return len(parts) >= 2 and parts[-1].upper() in US_STATES

def fetch(hours):
    cutoff = time.time() - hours * 3600
    rows = []
    for kind, repo in REPOS.items():
        url = f"https://raw.githubusercontent.com/SimplifyJobs/{repo}/dev/.github/scripts/listings.json"
        data = json.load(urllib.request.urlopen(url, timeout=120))
        for l in data:
            if not (l.get("active") and l.get("is_visible")): continue
            if l.get("category", "").lower() not in CATS: continue
            ts = l.get("date_posted", 0)  # original posting date; ignore later edits to the entry
            if ts < cutoff: continue
            us = [x for x in l.get("locations", []) if is_us(x)]
            if not us: continue  # US roles only
            l = dict(l, locations=us)
            rows.append((ts, kind, l))
    rows.sort(key=lambda r: -r[0])
    return rows

def norm_cat(c):
    return "AI/ML/Data" if "data" in c.lower() or "ml" in c.lower() else "Software"

if len(sys.argv) >= 2 and sys.argv[1] == "--json":
    days = float(sys.argv[2]); out = sys.argv[3]
    rows = fetch(days * 24)
    slim = [{
        "ts": ts, "kind": kind, "company": l["company_name"], "title": l["title"],
        "cat": norm_cat(l["category"]), "locs": l.get("locations", []), "url": l["url"],
        "spons": l.get("sponsorship", ""), "terms": l.get("terms", []),
        "degrees": l.get("degrees", []),
    } for ts, kind, l in rows]
    json.dump({"generated": time.time(), "days": days, "roles": slim}, open(out, "w"))
    print(f"wrote {len(slim)} roles to {out}")
    sys.exit(0)

SCHEDULE_ET = [3, 6, 11, 19, 22]  # hours (ET) at which the routine runs, minute :05

def auto_window():
    """Hours since the previous scheduled run, plus a little overlap, so each digest covers exactly the gap."""
    now = datetime.now(ET)
    slots = sorted(SCHEDULE_ET)
    prev = max((h for h in slots if h < now.hour or (h == now.hour and now.minute >= 5)), default=None)
    if prev is None:  # before the first slot today: previous run was the last slot yesterday
        prev_dt = now.replace(hour=slots[-1], minute=5, second=0, microsecond=0) - timedelta(days=1)
    else:
        prev_dt = now.replace(hour=prev, minute=5, second=0, microsecond=0)
    if (now - prev_dt).total_seconds() < 600:  # we are the run that just started; go back one more slot
        i = slots.index(prev_dt.hour)
        prev_dt = (prev_dt.replace(hour=slots[i-1]) if i > 0 else prev_dt.replace(hour=slots[-1]) - timedelta(days=1))
    return (now - prev_dt).total_seconds() / 3600 + 0.25

HOURS = auto_window() if len(sys.argv) > 1 and sys.argv[1] == "auto" else (float(sys.argv[1]) if len(sys.argv) > 1 else 2.5)
rows = fetch(HOURS)
if not rows:
    print("NO_NEW_ROLES"); sys.exit(0)
print(f"{len(rows)} new role(s) in the last {HOURS:g}h\n")
for ts, kind, l in rows:
    t = datetime.fromtimestamp(ts, ET).strftime("%b %d %I:%M%p ET")
    loc = "; ".join(l.get("locations", []))[:80]
    spons = l.get("sponsorship", "")
    flag = "" if spons in ("Offers Sponsorship", "Other") else f" [{spons}]"
    print(f"- [{kind}] {l['company_name']} — {l['title']} ({l['category']}){flag}\n  {loc} | {t}\n  {l['url']}")
