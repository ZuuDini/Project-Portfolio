#!/usr/bin/env python3
"""Download a small CFPB complaint subset and the OFAC SDN list into ./data (gitignored).

CFPB subset: complaints for one state over a date range, via the public CCDB API
  https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/
  docs: https://cfpb.github.io/api/ccdb/
OFAC SDN: https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV
  (no header row; "-0-" means null)

Usage: python scripts/download_data.py --state NY --from 2026-07-01 --to 2026-09-30 --size 10000
Standard library only.
"""
import argparse, json, pathlib, urllib.parse, urllib.request

CFPB_API = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
SDN_URL = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV"
DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
UA = {"User-Agent": "python-urllib"}  # descriptive UAs were 403d by the CFPB WAF in testing


def fetch(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    print(f"saved {dest} ({dest.stat().st_size:,} bytes)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", default="NY")
    p.add_argument("--from", dest="date_from", default="2026-07-01")
    p.add_argument("--to", dest="date_to", default="2026-09-30")
    p.add_argument("--size", type=int, default=10000, help="max rows (note: in testing the CSV export ignored this and returned the full filtered set)")
    a = p.parse_args()
    DATA.mkdir(exist_ok=True)
    q = urllib.parse.urlencode({
        "format": "csv", "no_aggs": "true", "state": a.state, "size": a.size,
        "date_received_min": a.date_from, "date_received_max": a.date_to,
        "sort": "created_date_desc",
    })
    fetch(f"{CFPB_API}?{q}", DATA / f"cfpb_{a.state}_{a.date_from}_{a.date_to}.csv")
    fetch(SDN_URL, DATA / "SDN.CSV")


if __name__ == "__main__":
    main()
