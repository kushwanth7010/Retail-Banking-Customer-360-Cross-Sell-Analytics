-- 90-day window is the three complete calendar months ending 2026-09-30.
-- One account per customer in this synthetic prototype; avoid multi-join fan-out.
CREATE VIEW customer_360 AS
WITH tx_90 AS (
 SELECT account_id,
  COUNT(CASE WHEN transaction_status='SUCCESS' THEN 1 END) AS successful_txn_90d,
  ROUND(SUM(CASE WHEN transaction_status='SUCCESS' AND direction='CREDIT' THEN amount_inr ELSE 0 END),2) AS credit_inflow_90d_inr,
  ROUND(SUM(CASE WHEN transaction_status='SUCCESS' AND direction='DEBIT' THEN amount_inr ELSE 0 END),2) AS debit_outflow_90d_inr,
  COUNT(CASE WHEN transaction_status='SUCCESS' AND transaction_type='SALARY' THEN 1 END) AS salary_credit_count_90d,
  ROUND(SUM(CASE WHEN transaction_status='SUCCESS' AND transaction_type='SALARY' THEN amount_inr ELSE 0 END),2) AS salary_inflow_90d_inr,
  COUNT(CASE WHEN transaction_status='RETURNED' THEN 1 END) AS returned_txn_90d
 FROM transactions
 WHERE transaction_date >= '2026-07-01' AND transaction_date <= '2026-09-30'
 GROUP BY account_id
), last_tx AS (
 SELECT account_id, MAX(transaction_date) AS last_successful_txn_date
 FROM transactions WHERE transaction_status='SUCCESS' AND transaction_date <= '2026-09-30'
 GROUP BY account_id
), products AS (
 SELECT customer_id,
  MAX(CASE WHEN product_code='FIXED_DEPOSIT' AND holding_status='ACTIVE' THEN 1 ELSE 0 END) AS has_fixed_deposit,
  MAX(CASE WHEN product_code='CREDIT_CARD' AND holding_status='ACTIVE' THEN 1 ELSE 0 END) AS has_credit_card,
  MAX(CASE WHEN product_code='PERSONAL_LOAN' AND holding_status='ACTIVE' THEN 1 ELSE 0 END) AS has_personal_loan
 FROM product_holdings GROUP BY customer_id
)
SELECT c.customer_id, c.region, c.onboarding_date, c.marketing_consent,
 c.do_not_contact, c.kyc_status, a.account_type, a.account_status,
 a.snapshot_balance_inr,
 CASE WHEN a.snapshot_balance_inr >= 100000 THEN 'HIGH_BALANCE'
      WHEN a.snapshot_balance_inr >= 40000 THEN 'MID_BALANCE'
      ELSE 'ENTRY_BALANCE' END AS balance_segment,
 COALESCE(p.has_fixed_deposit,0) AS has_fixed_deposit,
 COALESCE(p.has_credit_card,0) AS has_credit_card,
 COALESCE(p.has_personal_loan,0) AS has_personal_loan,
 COALESCE(t.successful_txn_90d,0) AS successful_txn_90d,
 COALESCE(t.credit_inflow_90d_inr,0) AS credit_inflow_90d_inr,
 COALESCE(t.debit_outflow_90d_inr,0) AS debit_outflow_90d_inr,
 COALESCE(t.salary_credit_count_90d,0) AS salary_credit_count_90d,
 COALESCE(t.salary_inflow_90d_inr,0) AS salary_inflow_90d_inr,
 COALESCE(t.returned_txn_90d,0) AS returned_txn_90d,
 l.last_successful_txn_date,
 CASE WHEN l.last_successful_txn_date IS NULL
       OR julianday('2026-09-30')-julianday(l.last_successful_txn_date)>60
      THEN 1 ELSE 0 END AS inactive_over_60d,
 CASE WHEN c.marketing_consent=1 AND c.do_not_contact=0 AND c.kyc_status='VERIFIED'
     AND a.account_status='ACTIVE' THEN 1 ELSE 0 END AS contactable_for_review
FROM customers c
JOIN accounts a ON a.customer_id=c.customer_id
LEFT JOIN tx_90 t ON t.account_id=a.account_id
LEFT JOIN last_tx l ON l.account_id=a.account_id
LEFT JOIN products p ON p.customer_id=c.customer_id;