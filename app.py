"""Optional interactive Streamlit dashboard: streamlit run app.py"""
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DB = ROOT / "outputs/retail_banking.sqlite"
st.set_page_config(page_title="Retail Banking Customer 360",page_icon="🏦",layout="wide")
st.title("🏦 Retail Banking Customer 360 & Cross-Sell Analytics")
st.caption("100% synthetic portfolio demonstration · As of 30 September 2026 · Review only; not credit decisions")
if not DB.exists():
    st.error("Run `python run_pipeline.py` in the project folder first.")
    st.stop()
with sqlite3.connect(DB) as con:
    c = pd.read_sql_query("SELECT * FROM customer_360",con)
    recommendations = pd.read_sql_query("SELECT * FROM recommendations",con)
    trends = pd.read_sql_query("SELECT substr(transaction_date,1,7) AS month, COUNT(*) AS successful_transactions FROM transactions WHERE transaction_status='SUCCESS' GROUP BY 1 ORDER BY 1",con)
region=st.sidebar.multiselect("Regions",sorted(c.region.unique()),default=sorted(c.region.unique()))
segment=st.sidebar.multiselect("Balance segments",sorted(c.balance_segment.unique()),default=sorted(c.balance_segment.unique()))
filtered=c[c.region.isin(region)&c.balance_segment.isin(segment)]
recs=recommendations[recommendations.customer_id.isin(filtered.customer_id)]
a,b,d,e=st.columns(4)
a.metric("Customers",f"{len(filtered):,}")
b.metric("Average snapshot balance",f"₹{filtered.snapshot_balance_inr.mean():,.0f}" if len(filtered) else "N/A")
d.metric("Contactable for review",f"{filtered.contactable_for_review.sum():,}")
e.metric("Cross-sell suggestions",f"{len(recs):,}")
left,right=st.columns(2)
with left:
    st.subheader("Customers by region")
    st.bar_chart(filtered.groupby("region").size().rename("Customers"))
    st.subheader("Monthly successful transaction activity (all synthetic accounts)")
    st.line_chart(trends.set_index("month"))
with right:
    st.subheader("Product suggestions awaiting human review")
    if len(recs): st.bar_chart(recs.groupby("proposed_product").size().rename("Suggestions"))
    else: st.info("No suggestions for the selected filters.")
    st.subheader("Customer balance segmentation")
    st.bar_chart(filtered.groupby("balance_segment").size().rename("Customers"))
st.subheader("Customer 360 — fictitious IDs only")
st.dataframe(filtered,hide_index=True,use_container_width=True)
st.subheader("Explainable suggestions — not preapproved offers")
st.dataframe(recs,hide_index=True,use_container_width=True)
st.download_button("Download filtered synthetic suggestions",recs.to_csv(index=False),"synthetic_recommendations.csv","text/csv")
st.warning("Do not use these heuristic scores for lending, credit approval, real marketing outreach or any automated suitability decision. Consent and KYC flags are synthetic; a human must verify actual product suitability, applicable law and policy.")