import csv
import sqlite3
import unittest
from pathlib import Path
from src.generate_data import generate
from src.build_database import build, DB, ROOT


class TestBankingProject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generate()
        cls.summary = build()
        cls.con=sqlite3.connect(DB)
        cls.con.row_factory=sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def test_fixed_seed_and_customers(self):
        self.assertEqual(self.summary["customer_count"],1500)
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM customer_360").fetchone()[0],1500)

    def test_foreign_keys(self):
        self.assertEqual(self.con.execute("PRAGMA foreign_key_check").fetchall(),[])

    def test_one_customer_one_recommendation(self):
        total=self.con.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]
        distinct=self.con.execute("SELECT COUNT(DISTINCT customer_id) FROM recommendations").fetchone()[0]
        self.assertEqual(total,distinct)
        self.assertEqual(total,self.summary["review_only_opportunities"])

    def test_no_ineligible_outreach(self):
        bad=self.con.execute('''SELECT COUNT(*) FROM recommendations r
          JOIN customer_360 c ON c.customer_id=r.customer_id
          WHERE c.contactable_for_review<>1 OR c.inactive_over_60d<>0
             OR c.returned_txn_90d<>0''').fetchone()[0]
        self.assertEqual(bad,0)

    def test_no_existing_product_recommended(self):
        bad=self.con.execute('''SELECT COUNT(*) FROM recommendations r
          JOIN customer_360 c ON c.customer_id=r.customer_id
          WHERE (r.proposed_product='CREDIT_CARD' AND c.has_credit_card=1)
             OR (r.proposed_product='FIXED_DEPOSIT' AND c.has_fixed_deposit=1)''').fetchone()[0]
        self.assertEqual(bad,0)

    def test_snapshot_is_not_transaction_revenue(self):
        # Totals displayed separately: customer asset snapshot != bank revenue.
        self.assertNotIn('bank_revenue',self.summary)
        self.assertNotIn('cross_sell_conversion_rate',self.summary)

    def test_all_recommendations_require_review(self):
        bad=self.con.execute("SELECT COUNT(*) FROM recommendations WHERE approval_status <> 'REVIEW_REQUIRED' OR priority_score NOT BETWEEN 0 AND 100").fetchone()[0]
        self.assertEqual(bad,0)

    def test_outputs_present(self):
        for path in (ROOT/'outputs/customer_360.csv', ROOT/'outputs/recommendations.csv',ROOT/'outputs/summary.json'):
            self.assertTrue(path.exists(),str(path))


if __name__ == '__main__':
    unittest.main()