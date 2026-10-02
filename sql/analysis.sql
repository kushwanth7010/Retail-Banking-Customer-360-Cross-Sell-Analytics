-- Query 1: customer and product footprint; no inference about revenue or bank profit.
SELECT region, COUNT(*) AS customers,
 ROUND(AVG(snapshot_balance_inr),2) AS avg_snapshot_balance_inr,
 SUM(has_fixed_deposit) AS fixed_deposit_holders,
 SUM(has_credit_card) AS credit_card_holders,
 SUM(has_personal_loan) AS personal_loan_holders
FROM customer_360 GROUP BY region ORDER BY customers DESC;

-- Query 2: successful transaction activity per month.
SELECT substr(transaction_date,1,7) AS month, COUNT(*) AS successful_transactions,
 ROUND(SUM(CASE WHEN direction='CREDIT' THEN amount_inr ELSE 0 END),2) AS credit_inflow_inr,
 ROUND(SUM(CASE WHEN direction='DEBIT' THEN amount_inr ELSE 0 END),2) AS debit_outflow_inr
FROM transactions WHERE transaction_status='SUCCESS'
GROUP BY substr(transaction_date,1,7) ORDER BY month;

-- Query 3: proposed cross-sell opportunities pending human review.
SELECT proposed_product, COUNT(*) AS customer_opportunities,
 ROUND(AVG(priority_score),1) AS avg_heuristic_priority
FROM recommendations GROUP BY proposed_product ORDER BY customer_opportunities DESC;