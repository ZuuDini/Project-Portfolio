# Sanctions & Complaints Risk Monitor

**Status: v0, in progress.** This is a starter scaffold. No analysis results yet; every results section below is TODO.

## Problem
Compliance teams have to answer two questions over and over: *does any customer or counterparty name resemble a sanctioned party?* and *what are consumers complaining about, and are complaints being handled on time?* This project builds a small, reproducible monitor for both, using public data, a Power BI semantic model, and an AI summary layer with human review.

## Data (public, official sources)
| Source | Link | Notes |
|---|---|---|
| OFAC Sanctions List Service | https://ofac.treasury.gov/sanctions-list-service | Landing page |
| OFAC SDN list (CSV) | https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV | No header row; `-0-` = null. Related files: ALT.CSV, ADD.CSV |
| CFPB Consumer Complaint Database | https://www.consumerfinance.gov/data-research/consumer-complaints/ | Published after company response or 15 days; not a statistical sample |
| CFPB API docs | https://cfpb.github.io/api/ccdb/ | Used for filtered subsets |

Customer names used for sanctions screening will be **synthetic**, not real people.

## Get the data
```bash
python3 scripts/download_data.py --state NY --from 2026-07-01 --to 2026-09-30
```
This writes a filtered CFPB CSV (one state, one quarter) and `SDN.CSV` into `data/`, which is gitignored. It needs only the Python standard library. Data is never committed.

## Model
Star schema with one fact table (complaints) and three dimensions (date, company, product/issue). See [docs/star-schema.md](docs/star-schema.md).

## AI use
Planned: an LLM classifies and summarizes complaint narratives. Every AI label goes to a human review queue, and accuracy is measured against a hand-labeled sample. AI output is treated as a suggestion, never a decision. Sanctions fuzzy matches are review candidates, not hits. TODO.

## Setup (Power BI on a Mac)
Power BI Desktop is Windows-only, so this project uses the **Power BI service** in the browser (app.powerbi.com):
1. Sign in to the Power BI service (a free or work account).
2. Upload the cleaned CSVs, or connect via OneDrive/SharePoint so refresh works.
3. Build the semantic model and relationships in the service's web modeling view, following `docs/star-schema.md`.
4. Build report pages on top of the model.

(Alternatives: a Windows VM/Parallels for Desktop. Not required.)

## Dashboard pages (planned)
Alerts · Complaint trends · Data-quality score · Review backlog. TODO.

## Results
TODO. No results yet.

## Data-quality checks
TODO.

## Limitations
- CFPB does not publish the company's actual response date, so timeliness relies on CFPB's `Timely response?` flag.
- Fuzzy name matching produces false positives by design; human review is required.

## Walkthrough
TODO (Loom link).
