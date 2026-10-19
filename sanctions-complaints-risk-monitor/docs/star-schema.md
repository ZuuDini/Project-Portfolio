# Star schema (v0 sketch)

Grain of the fact table: one row per CFPB complaint (`complaint_id`).

```mermaid
erDiagram
    DIM_DATE ||--o{ FACT_COMPLAINTS : "date_received_key"
    DIM_COMPANY ||--o{ FACT_COMPLAINTS : "company_key"
    DIM_PRODUCT_ISSUE ||--o{ FACT_COMPLAINTS : "product_issue_key"

    FACT_COMPLAINTS {
        int complaint_id PK
        int date_received_key FK
        int date_sent_key FK
        int company_key FK
        int product_issue_key FK
        string state
        string zip_code
        string submitted_via
        string tags
        string company_response
        string company_public_response
        bool timely_response
        int days_received_to_sent
        bool has_narrative
        string ai_category
        float ai_confidence
        string review_status
        bool sdn_flag
    }
    DIM_DATE {
        int date_key PK
        date date
        int year
        int quarter
        int month
        string month_name
        int week_of_year
        string day_of_week
    }
    DIM_COMPANY {
        int company_key PK
        string company_name
        string company_name_normalized
        bool sdn_candidate_match
        float sdn_best_score
        string sdn_review_outcome
    }
    DIM_PRODUCT_ISSUE {
        int product_issue_key PK
        string product
        string sub_product
        string issue
        string sub_issue
    }
```

## Column notes

| Table | Column | Source |
|---|---|---|
| fact | complaint_id, state, zip_code, submitted_via, tags, company_response, company_public_response, timely_response | CFPB CSV columns as published |
| fact | date_received_key / date_sent_key | CFPB `Date received` / `Date sent to company` → `dim_date` |
| fact | days_received_to_sent | derived. CFPB does not publish the company's actual response date, so response-time checks rely on the `Timely response?` flag |
| fact | has_narrative | derived. The narrative text is not in the default CSV export; it needs the `complaint_what_happened` field (TODO) |
| fact | ai_category, ai_confidence, review_status | AI summary/classification layer (TODO, not built yet) |
| fact / dim_company | sdn_flag, sdn_candidate_match, sdn_best_score, sdn_review_outcome | fuzzy match against OFAC SDN plus human review (TODO). A candidate match is **not** a sanctions hit until it has been reviewed |
| dim_product_issue | product … sub_issue | CFPB columns, deduplicated |
