"""Build a validated SQLite warehouse, Customer 360 view, and review-only suggestions."""
import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA, OUTPUT = ROOT / "data", ROOT / "outputs"
DB = OUTPUT / "retail_banking.sqlite"
TABLES = ("customers", "accounts", "product_holdings", "transactions")


def build():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    try:
        connection.executescript((ROOT / "sql/schema.sql").read_text(encoding="utf-8"))
        for table in TABLES:
            with (DATA / f"{table}.csv").open(encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                cols = reader.fieldnames
                if not cols:
                    raise ValueError(f"Empty dataset: {table}")
                placeholders = ",".join("?" for _ in cols)
                sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})"
                connection.executemany(sql, ([row[c] for c in cols] for row in reader))
        connection.executescript((ROOT / "sql/customer_360.sql").read_text(encoding="utf-8"))
        rows = connection.execute("SELECT * FROM customer_360 ORDER BY customer_id").fetchall()
        proposals = []
        for r in rows:
            if not r["contactable_for_review"] or r["inactive_over_60d"] or r["returned_txn_90d"]:
                continue
            options = []
            if r["account_type"] == "SAVINGS" and not r["has_fixed_deposit"] and r["snapshot_balance_inr"] >= 80000:
                priority = min(100, 50 + min(30, int((r["snapshot_balance_inr"]-80000)//5000))
                               + min(20, r["successful_txn_90d"]))
                options.append(("FIXED_DEPOSIT", priority,
                    "High synthetic savings snapshot; discuss liquidity needs, term and suitability"))
            avg_salary = r["salary_inflow_90d_inr"] / 3
            if (r["account_type"] == "SAVINGS" and not r["has_credit_card"]
                    and r["salary_credit_count_90d"] >= 2 and avg_salary >= 35000):
                priority = min(100, 50 + min(30, int(avg_salary//4000))
                               + min(20, r["successful_txn_90d"]))
                options.append(("CREDIT_CARD", priority,
                    "Recurring synthetic salary inflows; suitability and affordability checks required"))
            if options:
                offer, score, reason = sorted(options, key=lambda v:(-v[1],v[0]))[0]
                proposals.append((r["customer_id"], offer, score, reason, "REVIEW_REQUIRED"))
        connection.executemany("INSERT INTO recommendations VALUES (?,?,?,?,?)", proposals)
        check = connection.execute("PRAGMA foreign_key_check").fetchall()
        if check:
            raise ValueError(f"Foreign key check failed: {check[:3]}")
        connection.commit()
        c360 = connection.execute("SELECT * FROM customer_360 ORDER BY customer_id")
        with (OUTPUT / "customer_360.csv").open("w",encoding="utf-8",newline="") as f:
            w=csv.writer(f); w.writerow([v[0] for v in c360.description]); w.writerows(c360)
        recs = connection.execute("SELECT * FROM recommendations ORDER BY priority_score DESC, customer_id")
        with (OUTPUT / "recommendations.csv").open("w",encoding="utf-8",newline="") as f:
            w=csv.writer(f); w.writerow([v[0] for v in recs.description]); w.writerows(recs)
        metrics = {
            "as_of_date":"2026-09-30", "data_type":"100% synthetic; not production banking records",
            "customer_count":len(rows),
            "total_successful_transactions":connection.execute("SELECT COUNT(*) FROM transactions WHERE transaction_status='SUCCESS'").fetchone()[0],
            "avg_snapshot_balance_inr":round(sum(r["snapshot_balance_inr"] for r in rows)/len(rows),2),
            "contactable_for_review":sum(r["contactable_for_review"] for r in rows),
            "inactive_over_60d":sum(r["inactive_over_60d"] for r in rows),
            "credit_card_holders":sum(r["has_credit_card"] for r in rows),
            "fixed_deposit_holders":sum(r["has_fixed_deposit"] for r in rows),
            "review_only_opportunities":len(proposals),
            "opportunity_by_product":{r[0]:r[1] for r in connection.execute("SELECT proposed_product,COUNT(*) FROM recommendations GROUP BY 1")},
            "method":"Explainable rules, one proposed product per customer, approval_status=REVIEW_REQUIRED"
        }
        (OUTPUT / "summary.json").write_text(json.dumps(metrics,indent=2)+"\n", encoding="utf-8")
        return metrics
    finally:
        connection.close()


if __name__ == "__main__":
    print(json.dumps(build(),indent=2))