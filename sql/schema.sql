PRAGMA foreign_keys = ON;
CREATE TABLE customers (
 customer_id TEXT PRIMARY KEY,
 region TEXT NOT NULL,
 onboarding_date TEXT NOT NULL,
 marketing_consent INTEGER NOT NULL CHECK(marketing_consent IN (0,1)),
 do_not_contact INTEGER NOT NULL CHECK(do_not_contact IN (0,1)),
 kyc_status TEXT NOT NULL CHECK(kyc_status IN ('VERIFIED','REVIEW_REQUIRED'))
);
CREATE TABLE accounts (
 account_id TEXT PRIMARY KEY,
 customer_id TEXT NOT NULL UNIQUE REFERENCES customers(customer_id),
 account_type TEXT NOT NULL CHECK(account_type IN ('SAVINGS','CURRENT')),
 account_status TEXT NOT NULL CHECK(account_status IN ('ACTIVE','INACTIVE')),
 snapshot_balance_inr REAL NOT NULL CHECK(snapshot_balance_inr >= 0)
);
CREATE TABLE product_holdings (
 holding_id TEXT PRIMARY KEY,
 customer_id TEXT NOT NULL REFERENCES customers(customer_id),
 product_code TEXT NOT NULL CHECK(product_code IN ('FIXED_DEPOSIT','CREDIT_CARD','PERSONAL_LOAN')),
 holding_status TEXT NOT NULL CHECK(holding_status IN ('ACTIVE','CLOSED')),
 UNIQUE(customer_id, product_code)
);
CREATE TABLE transactions (
 transaction_id TEXT PRIMARY KEY,
 account_id TEXT NOT NULL REFERENCES accounts(account_id),
 transaction_date TEXT NOT NULL,
 direction TEXT NOT NULL CHECK(direction IN ('CREDIT','DEBIT')),
 transaction_type TEXT NOT NULL CHECK(transaction_type IN ('SALARY','TRANSFER_IN','REFUND','PURCHASE','BILL_PAYMENT','TRANSFER_OUT')),
 amount_inr REAL NOT NULL CHECK(amount_inr > 0),
 transaction_status TEXT NOT NULL CHECK(transaction_status IN ('SUCCESS','RETURNED'))
);
CREATE TABLE recommendations (
 customer_id TEXT PRIMARY KEY REFERENCES customers(customer_id),
 proposed_product TEXT NOT NULL CHECK(proposed_product IN ('FIXED_DEPOSIT','CREDIT_CARD')),
 priority_score INTEGER NOT NULL CHECK(priority_score BETWEEN 0 AND 100),
 rationale TEXT NOT NULL,
 approval_status TEXT NOT NULL CHECK(approval_status = 'REVIEW_REQUIRED')
);
CREATE INDEX idx_tx_account_date ON transactions(account_id,transaction_date);
CREATE INDEX idx_holding_customer ON product_holdings(customer_id);