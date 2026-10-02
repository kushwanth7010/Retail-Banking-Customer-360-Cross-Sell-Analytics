# Business analysis report — reproducible synthetic example

**Reference date:** 30 September 2026. **Data:** 100% synthetic, independently generated; no financial institution supplied these records.

## Executive summary

A Python data generator produced 1,500 fictitious customers, one account per customer, 904 active product holdings and 79,422 transaction events. SQLite constraints validated the relational links. A SQL Customer 360 view joined aggregated product footprint and transaction activity into one row per customer; a bounded, explainable heuristic generated 436 **review-only** suggestions (221 credit-card discussions and 215 FD discussions). These are possible conversation topics pending further suitability and governance checks, not offers made or sales achieved.

## Portfolio metrics

| Measure | Computed value |
|---|---:|
| Customers | 1,500 |
| Transactions generated | 79,422 |
| Successful transactions | 78,370 |
| Average snapshot account balance | ₹112,340.78 |
| Synthetic consent+KYC+active-account+DNC gate passes | 985 |
| No successful transaction in more than 60 days | 124 |
| Customers with active credit-card holding | 420 |
| Customers with active FD holding | 347 |
| Rule-based suggestions requiring human review | 436 |
| Card discussion suggestions | 221 |
| FD discussion suggestions | 215 |

The contactability figure applies the basic flag gate only, while the final suggestion logic additionally checks recent activity, returned payments and product-specific thresholds. The separate independently generated balance snapshot is not a reconciled bank ledger; it must not be interpreted as bank revenue or deposits under management.

## Segment breakdown

- Entry balance (<₹40,000): 229 fictitious customers.
- Mid balance (₹40,000–<₹100,000): 417 fictitious customers.
- High balance (≥₹100,000): 854 fictitious customers.

These buckets were designed for demonstration, not learned from real customers and not sourced from ICICI Bank policies.

## How a business analyst would use the results

1. Validate joins/aggregates and investigate unusually high/low balances and activity outliers.
2. Monitor product footprint and variation across customer segments and regions.
3. Identify records that appear suitable for **human evaluation**, with consent and product-specific checks before any contact.
4. Review proposed product mix, test whether the heuristics behave reasonably, and check whether false positives occur in an authorized pilot with appropriate privacy/consent controls.
5. Only after a real, governed pilot could conversion, acceptance, uplift, incremental revenue and ROI be measured. None of those outcomes can be estimated reliably from this synthetic dataset.

## Explicit limitations

The project demonstrates engineering and decision-support workflow, not a deployed banking campaign. Synthetic patterns were generated rather than observed; the rule index is not a trained propensity model. A returned transaction is not a valid stand-alone measure of creditworthiness, and simulated KYC/consent flags do not establish operational regulatory compliance. Customer-level marketing suitability, actual credit eligibility and fair-treatment standards would require further authorized processes.