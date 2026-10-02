"""Deterministically generate fictitious retail banking data (no real customers)."""
import calendar
import csv
import random
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED = 20261002
CUSTOMER_COUNT = 1500
REGIONS = ("Hyderabad", "Bengaluru", "Mumbai", "Delhi NCR", "Chennai", "Pune")
MONTHS = [(2026, m) for m in range(1, 10)]


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def generate(seed=SEED, count=CUSTOMER_COUNT):
    rng = random.Random(seed)
    DATA.mkdir(parents=True, exist_ok=True)
    customers, accounts, holdings, transactions = [], [], [], []
    transaction_no = 1
    holding_no = 1
    for n in range(1, count + 1):
        cid, aid = f"C{n:05d}", f"A{n:05d}"
        account_type = "SAVINGS" if rng.random() < .87 else "CURRENT"
        salary_customer = account_type == "SAVINGS" and rng.random() < .63
        dormant = rng.random() < .08
        balance = round(rng.uniform(4500, 220000), 2)
        customer = dict(customer_id=cid, region=rng.choice(REGIONS),
                        onboarding_date=date(rng.choice((2021, 2022, 2023, 2024, 2025)), rng.randint(1, 12), rng.randint(1, 28)).isoformat(),
                        marketing_consent=int(rng.random() < .76),
                        do_not_contact=int(rng.random() < .055),
                        kyc_status="VERIFIED" if rng.random() < .94 else "REVIEW_REQUIRED")
        customers.append(customer)
        accounts.append(dict(account_id=aid, customer_id=cid, account_type=account_type,
                             account_status="ACTIVE" if rng.random() < .96 else "INACTIVE",
                             snapshot_balance_inr=balance))
        for product, chance in (("FIXED_DEPOSIT", .23), ("CREDIT_CARD", .29), ("PERSONAL_LOAN", .10)):
            if rng.random() < chance:
                holdings.append(dict(holding_id=f"H{holding_no:06d}", customer_id=cid,
                                     product_code=product, holding_status="ACTIVE"))
                holding_no += 1
        # The snapshot balance is a separate synthetic account observation, not a reconciled ledger.
        for year, month in MONTHS:
            if dormant and month >= 8:
                continue
            days = calendar.monthrange(year, month)[1]
            if salary_customer and rng.random() < .93:
                transactions.append(dict(transaction_id=f"T{transaction_no:07d}", account_id=aid,
                    transaction_date=date(year, month, rng.randint(1, min(days, 7))).isoformat(),
                    direction="CREDIT", transaction_type="SALARY", amount_inr=round(rng.uniform(28000, 115000), 2),
                    transaction_status="SUCCESS"))
                transaction_no += 1
            for _ in range(rng.randint(3, 8)):
                credit = rng.random() < (.25 if not salary_customer else .12)
                tx_type = rng.choice(("TRANSFER_IN", "REFUND")) if credit else rng.choice(("PURCHASE", "BILL_PAYMENT", "TRANSFER_OUT"))
                returned = not credit and rng.random() < .018
                transactions.append(dict(transaction_id=f"T{transaction_no:07d}", account_id=aid,
                    transaction_date=date(year, month, rng.randint(1, days)).isoformat(),
                    direction="CREDIT" if credit else "DEBIT", transaction_type=tx_type,
                    amount_inr=round(rng.uniform(250, 10500), 2),
                    transaction_status="RETURNED" if returned else "SUCCESS"))
                transaction_no += 1
    write_csv(DATA / "customers.csv", list(customers[0]), customers)
    write_csv(DATA / "accounts.csv", list(accounts[0]), accounts)
    write_csv(DATA / "product_holdings.csv", ["holding_id", "customer_id", "product_code", "holding_status"], holdings)
    write_csv(DATA / "transactions.csv", list(transactions[0]), transactions)
    return {"customers": len(customers), "accounts": len(accounts), "holdings": len(holdings), "transactions": len(transactions), "seed": seed}


if __name__ == "__main__":
    print(generate())