"""Create a stand-alone offline HTML dashboard with embedded Plotly JS."""
import json
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "outputs/retail_banking.sqlite"


def make_dashboard():
    with sqlite3.connect(DB) as con:
        regions = pd.read_sql_query("SELECT region, COUNT(*) AS customers, ROUND(AVG(snapshot_balance_inr),2) avg_balance FROM customer_360 GROUP BY region ORDER BY customers DESC",con)
        months = pd.read_sql_query("SELECT substr(transaction_date,1,7) month, COUNT(*) transactions FROM transactions WHERE transaction_status='SUCCESS' GROUP BY 1 ORDER BY 1", con)
        products = pd.read_sql_query("SELECT proposed_product product, COUNT(*) opportunities FROM recommendations GROUP BY 1 ORDER BY 1", con)
        segments = pd.read_sql_query("SELECT balance_segment segment,COUNT(*) customers FROM customer_360 GROUP BY 1 ORDER BY 1",con)
    metrics = json.loads((ROOT / "outputs/summary.json").read_text(encoding="utf-8"))
    fig = make_subplots(rows=2,cols=2,
        subplot_titles=("Customers by region", "Monthly successful transactions", "Balance segments", "Suggested products (review only)"),
        specs=[[{"type":"bar"},{"type":"scatter"}],[{"type":"bar"},{"type":"bar"}]],
        vertical_spacing=.18,horizontal_spacing=.14)
    fig.add_trace(go.Bar(x=regions.region,y=regions.customers,name="Customers",marker_color="#1E3A8A"),row=1,col=1)
    fig.add_trace(go.Scatter(x=months.month,y=months.transactions,name="Transactions",mode="lines+markers",line_color="#D97706"),row=1,col=2)
    fig.add_trace(go.Bar(x=segments.segment,y=segments.customers,name="Segments",marker_color="#0F766E"),row=2,col=1)
    fig.add_trace(go.Bar(x=products["product"],y=products["opportunities"],name="Suggestions",marker_color="#7C3AED"),row=2,col=2)
    fig.update_layout(template="plotly_white",height=850,showlegend=False,margin=dict(l=52,r=38,t=75,b=90))
    fig.update_xaxes(tickangle=-18)
    plot_div=plot(fig,output_type="div",include_plotlyjs=True,config={"displaylogo":False,"responsive":True})
    kpis=[("Synthetic customers",f'{metrics["customer_count"]:,}'),
          ("90d suggestions",f'{metrics["review_only_opportunities"]:,}'),
          ("Consent + KYC + active",f'{metrics["contactable_for_review"]:,}'),
          ("Snapshot avg. balance",f'₹{metrics["avg_snapshot_balance_inr"]:,.0f}')]
    cards="".join(f'<article class="card"><span>{title}</span><strong>{value}</strong></article>' for title,value in kpis)
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Retail Banking Customer 360 - Synthetic Portfolio</title>
    <style>body{{font-family:Arial,Helvetica,sans-serif;background:#f5f7fb;color:#172033;max-width:1300px;margin:28px auto;padding:0 16px}}h1{{margin-bottom:6px}}p{{line-height:1.55;color:#465469}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(195px,1fr));gap:14px;margin:25px 0}}.card{{background:white;padding:18px;border-radius:12px;border:1px solid #e6eaf0}}.card span{{display:block;font-size:13px;color:#596579}}.card strong{{font-size:29px;display:block;margin-top:9px}}.plot{{background:white;border:1px solid #e6eaf0;border-radius:12px;padding:8px}}footer{{font-size:13px;margin:20px 0 45px;color:#576275}}</style></head><body>
    <h1>Retail Banking Customer 360</h1><p>Cross-sell opportunities &amp; customer analytics | Synthetic demonstration | As of 30 September 2026</p>
    <div class="cards">{cards}</div><div class="plot">{plot_div}</div>
    <footer><b>Important:</b> Fictitious data and explainable, heuristic review-only suggestions. Scores are <b>not</b> probabilities, credit decisions, or real commercial results. The dashboard contains no identifiable people.</footer>
    </body></html>'''
    output = ROOT / "dashboard/index.html"
    output.write_text(html,encoding="utf-8")
    return output


if __name__ == "__main__":
    print(make_dashboard())