"""
PoultryPro Analytics — Commercial Farm Profitability, FCR & EPEF Efficiency Suite (v2.0)
Interactive Flock Batch Evaluator + Unit Cost Auditor + 3-Sheet Excel Workbook Export
"""

import io
from datetime import datetime, timezone
import streamlit as st
import pandas as pd
import plotly.express as px
from poultry_engine import DEFAULT_FLOCKS, evaluate_poultry_flocks

st.set_page_config(page_title="PoultryPro Analytics — FCR & Flock Profitability Engine", page_icon="🐔", layout="wide")
st.title("🐔 PoultryPro Analytics — Commercial Farm Profitability & FCR Engine")
st.caption("Feed Conversion Ratio (FCR) • European Production Efficiency Factor (EPEF) • Livability % • Cost per Kg Live Weight • Excel Flock Audit")
st.divider()

uploaded = st.sidebar.file_uploader("Upload Custom Flock Batch Ledger (.csv or .xlsx)", type=["csv", "xlsx"])
base_df = (pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)) if uploaded else pd.DataFrame(DEFAULT_FLOCKS)

st.subheader("Interactive Flock House & Batch Production Ledger")
st.caption("Edit bird placement, mortality/harvest counts, feed consumed, or farm-gate prices below to recalculate FCR, EPEF, and net batch profit.")
edited_flocks = st.data_editor(base_df, width="stretch", num_rows="dynamic")

res = evaluate_poultry_flocks(edited_flocks)
out_df = res["df"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Average Flock FCR", f"{res['avg_fcr']:.3f}", delta=f"Livability: {res['avg_livability']:.2f}%")
c2.metric("Average EPEF Score", f"{res['avg_epef']:.1f}", delta="Target Benchmark >= 350")
c3.metric("Avg Production Cost / Kg", f"${res['avg_cost_per_kg']:.3f}", delta="Feed + DOC + Health + Ops")
c4.metric("Total Net Flock Profit", f"${res['total_profit']:,.2f}", delta=f"Across {len(out_df)} Active Houses")

tab1, tab2, tab3 = st.tabs(["📊 Flock Efficiency & Margin Ledger", "📈 FCR, EPEF & Profit Charts", "📥 3-Sheet Excel Flock Workbook"])

with tab1:
    st.dataframe(out_df[["Flock_ID", "House", "Livability_Pct", "Total_Live_Weight_Kg", "FCR", "EPEF_Score", "Performance_Tier", "Cost_Per_Kg_Live_USD", "Net_Batch_Profit_USD", "Net_Margin_Pct"]], width="stretch")

with tab2:
    col1, col2 = st.columns(2)
    col1.plotly_chart(px.bar(out_df, x="Flock_ID", y="EPEF_Score", color="Performance_Tier", title="European Production Efficiency Factor (EPEF) by Flock"), width="stretch")
    col2.plotly_chart(px.bar(out_df, x="Flock_ID", y="Net_Batch_Profit_USD", color="House", title="Net Batch Profit by Flock House ($ USD)"), width="stretch")

with tab3:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        pd.DataFrame([
            {"Audit_Metric": "Report Generated (UTC)", "Value": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")},
            {"Audit_Metric": "Average Feed Conversion Ratio (FCR)", "Value": f"{res['avg_fcr']:.3f}"},
            {"Audit_Metric": "Average European Efficiency (EPEF)", "Value": f"{res['avg_epef']:.1f}"},
            {"Audit_Metric": "Average Flock Livability (%)", "Value": f"{res['avg_livability']:.2f}%"},
            {"Audit_Metric": "Average Production Cost per Kg ($)", "Value": f"${res['avg_cost_per_kg']:.3f}"},
            {"Audit_Metric": "Total Net Profit Across Batches ($)", "Value": f"${res['total_profit']:,.2f}"},
        ]).to_excel(writer, sheet_name="01_Farm_Executive_Summary", index=False)
        out_df.to_excel(writer, sheet_name="02_Flock_Performance_Audit", index=False)

    st.download_button("📊 Download PoultryPro Flock Profitability Workbook (.xlsx)", buf.getvalue(), "PoultryPro_Analytics_Flock_Profitability.xlsx")
