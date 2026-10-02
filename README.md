# Retail Banking Customer 360 & Cross-Sell Analytics

**Independent portfolio project for banking business analytics | Python · SQL/SQLite · Plotly · Streamlit · data quality · customer segmentation · explainable rules**

> **Privacy and provenance:** This repository uses 100% randomly generated, fictitious customer/account/transaction data (fixed seed). It is **not** an ICICI Bank project, not derived from any real bank's customer records, and not evidence of actual product conversions, commercial impact, account balances or credit decisions. The reference date is 30 September 2026. No real names, contact details or protected attributes are generated.

## Business question

How could a hypothetical retail bank combine separate customer, account, product and transaction datasets into a trustworthy **Customer 360** view, use it to understand product penetration and transactional activity, and produce **consent-aware, review-only** fixed-deposit or credit-card discussion opportunities?

## Verified demonstration results (seed `20261002`)

| Indicator | Result | Meaning |
|---|---:|---|
| Synthetic customers | 1,500 | Fictitious customer IDs only |
| Generated transactions | 79,422 | Successful and returned simulated transactions |
| Successful transactions | 78,370 | Across January–September 2026 |
| Average snapshot account balance | ₹112,340.78 | Independently simulated snapshot; **not** bank revenue |
| Potentially contactable records | 985 | Consented, not opted out, verified KYC, active account; further checks still required |
| Dormant > 60 days | 124 | Last successful transaction more than 60 days before 30 Sep |
| Existing credit-card holders | 420 | Customers holding a simulated active credit card |
| Existing fixed-deposit holders | 347 | Customers holding a simulated active FD |
| Review-only cross-sell suggestions | 436 | Up to one proposal per synthetic customer |
| Credit-card discussion opportunities | 221 | Not an approval or conversion |
| FD discussion opportunities | 215 | Not an approval or conversion |

*Figures depend on the included fixed seed and rules; rerun the pipeline to reproduce them. `outputs/summary.json` is the authoritative generated summary after running the pipeline; `docs/verified_summary.json` records the verified reference run.*

## Repository structure

This GitHub repository tracks source code, SQL, tests, and documentation. **Generated synthetic CSVs, SQLite database, and the self-contained HTML dashboard are reproducible** using `python run_pipeline.py`, and are intentionally excluded from the Git history to keep the repository lightweight. A complete pre-generated ZIP is also available from the project author.

```text
Retail-Banking-Customer-360-Cross-Sell-Analytics/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── run_pipeline.py              # reproducible end-to-end command
├── app.py                       # optional Streamlit dashboard
├── src/
│   ├── __init__.py
│   ├── generate_data.py         # synthetic relational CSVs
│   ├── build_database.py       # SQLite loader, SQL view, rules, exports
│   └── make_dashboard.py       # offline HTML dashboard generator
├── data/                        # synthetic CSVs generated locally
├── sql/
│   ├── schema.sql
│   ├── customer_360.sql
│   └── analysis.sql
├── outputs/                     # generated SQLite, CSVs, JSON
├── dashboard/                   # generated offline dashboard
├── tests/
│   └── test_pipeline.py
└── docs/
    ├── architecture.md
    ├── interview_guide.md
    ├── analysis_report.md
    └── verified_summary.json   # sample verified seeded run
```

## Run locally (Windows 11 / VS Code)

1. Install Python 3.10+ and open this project folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Run the following commands:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_pipeline.py
python -m unittest discover -s tests -v
streamlit run app.py
```

If PowerShell prevents activation, you can run `.venv\Scripts\python.exe -m pip install -r requirements.txt`, `.venv\Scripts\python.exe run_pipeline.py` and `.venv\Scripts\python.exe -m streamlit run app.py` without changing execution policy.

**No Streamlit installation needed to see the offline dashboard:** open `dashboard/index.html` in your browser after the project pipeline has run. The HTML embeds Plotly and does not fetch external banking data.

On macOS/Linux, use `python3 -m venv .venv`, `source .venv/bin/activate`, then the same Python commands.

## Workflow explained

1. **Generate** four normalized CSV datasets (`customers`, `accounts`, `product_holdings`, `transactions`) with a reproducible random seed and no personal information.
2. **Validate/load** the CSVs into SQLite with primary/foreign keys, type and value constraints, and indexes.
3. **Build Customer 360** via separate aggregate CTEs for recent transactions, last activity and existing products. Join the CTEs back to one row per customer—this avoids inflating transaction totals when a customer has multiple products.
4. **Segment** customer account snapshot balances into entry (<₹40,000), mid (₹40,000–<₹100,000), and high (≥₹100,000). All thresholds are **illustrative** and are not any bank's real segmentation rules.
5. **Gate suggestions** on consent, do-not-contact, synthetic verified KYC, active account, last activity within 60 days and absence of returned transactions in the last three calendar months.
6. **Generate review-only proposals:** FD discussion for an active savings customer without an FD and a synthetic account snapshot ≥₹80,000; credit-card discussion for a savings customer without a card with ≥2 salary credits and three-month average monthly salary credits ≥₹35,000. Every proposal is marked `REVIEW_REQUIRED` and uses an explainable *priority index*, **not** a probability or credit-risk score. Maximum one proposal per customer.
7. **Export** `customer_360.csv`, `recommendations.csv`, `summary.json`, SQLite and two dashboard options (offline HTML and Streamlit).
8. **Test** source/warehouse integrity, eligibility gates, product duplication prevention and the review-only restriction.

## Sample SQL

```sql
SELECT region,
       COUNT(*) AS customers,
       ROUND(AVG(snapshot_balance_inr), 2) AS avg_balance_inr,
       SUM(has_credit_card) AS card_holders
FROM customer_360
GROUP BY region
ORDER BY customers DESC;
```

Other sample queries are in [`sql/analysis.sql`](sql/analysis.sql).

## Explainable priority index (NOT a probability)

The project uses a bounded **0–100 heuristic sorting index** for human review, based on recent successful activity and an illustrative financial signal (snapshot balance for FD, salary inflows for credit-card discussions). It is not trained on historical responses, has no estimated predictive performance or validation against actual customers, and does not estimate creditworthiness, affordability, acceptance, suitability or conversion probability.

The filter stops generation when the illustrative contact/quality checks fail. For an actual bank, stronger legal, privacy, consent, eligibility, product suitability, model governance and audit procedures would be required before any operational use.

## Limitations and safeguards

- **No real-world outcomes:** Opportunity counts are not approvals, contacts, accepted offers, profit or conversion lift. Nothing here proves actual business impact.
- **No automated decisioning:** Do not use this tool for lending, credit approval, eligibility decisions, customer exclusion, or real marketing messages.
- **No real financial ledger:** `snapshot_balance_inr` is a separate synthetic snapshot and does not reconcile to the generated cash-flow transactions. Deposits and transaction inflows are not bank revenues.
- **No sensitive personal attributes:** No names, phones, email, government IDs, race, religion, health, age or gender are included. A real privacy/security review would still be required.
- **Synthetic labels:** Product-holding status and salary events are simulated, not observed behavior.
- **Scope:** One simulated savings/current account per customer; a real core banking environment has many-to-many ownership, multiple accounts per customer, currencies, reversals, entity resolution and complex product hierarchies.
- **Time window:** Analysis uses July 1–September 30, 2026 as the complete three-month period and September 30, 2026 as the inactivity reference date.

## Resume-ready, verifiable description

**Retail Banking Customer 360 & Cross-Sell Analytics** | Python, SQL, SQLite, Plotly, Streamlit
- Built a synthetic end-to-end retail banking pipeline integrating **1,500 customer profiles and 79K+ transactions** into a SQL-based Customer 360 view with product, segment and activity KPIs.
- Developed a consent-aware, explainable rules framework producing **436 review-only cross-sell suggestions** and interactive dashboards; validated pipeline integrity with **8 automated tests**.

For interview preparation, see [`docs/interview_guide.md`](docs/interview_guide.md). For formulas, schema and controls, see [`docs/architecture.md`](docs/architecture.md). For results and interpretation, see [`docs/analysis_report.md`](docs/analysis_report.md).