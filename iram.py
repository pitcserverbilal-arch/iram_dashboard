import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ================= CONFIG =================
st.set_page_config(
    page_title="National Power Sector Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

NEPRA_LOSS_LIMIT = 4.1

# ================= HEADER =================
st.markdown("""
<div style="background:linear-gradient(90deg,#0b3d91,#1f78b4);
padding:22px;border-radius:14px">
<h1 style="color:white;text-align:center;font-size:36px;">
⚡ Pakistan Power Distribution – Executive Insight Dashboard
</h1>
<p style="color:#dce9ff;text-align:center;font-size:18px;">
NEPRA-Anchored | DISCO Performance | Policy & Risk Visibility
</p>
</div>
""", unsafe_allow_html=True)

# ================= DATA UPLOAD =================
uploaded_file = st.file_uploader("📤 Upload DISCO Excel / CSV", type=["xlsx", "csv"])

if not uploaded_file:
    st.warning("Please upload the DISCO dataset to proceed.")
    st.stop()

df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith("xlsx") else pd.read_csv(uploaded_file)

# ================= DATA PREP =================
df["BILLING_MONTH"] = pd.to_datetime(df["BILLING_MONTH"])
df["MONTH"] = df["BILLING_MONTH"].dt.to_period("M").astype(str)

months = sorted(df["MONTH"].unique())
months_with_all = ["All Months"] + months
selected_months = st.multiselect(
    "📅 Select Month(s)",
    months_with_all,
    default=[months[-1]]
)

if "All Months" in selected_months:
    filtered_df = df.copy()
else:
    filtered_df = df[df["MONTH"].isin(selected_months)].copy()

if filtered_df.empty:
    st.warning("No data available for the selected month(s). Please select another period.")
    st.stop()

# ================= ANALYSIS DATASET (EXCLUDE ALL DISCOs) =================
analysis_df = filtered_df[
    (filtered_df["SDIV_NAME"] != "ALL DISCOs") &
    (filtered_df["ACTIVE_CONS"] > 0)
].copy()

# ================= TABS =================
tab1, tab2 = st.tabs(["National Overview", "DISCO Comparison"])

# ================= TAB 1: NATIONAL OVERVIEW =================
with tab1:
    st.markdown("## National LEVEL SNAPSHOT")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("⚡ Energy Purchased (GWh)", f"{filtered_df['MONTHLY_ENERGY'].sum():,.0f}")
    c2.metric("📨 Units Billed (GWh)", f"{filtered_df['MON_UNITS_BILLED'].sum():,.0f}")
    c3.metric("📉 Avg Loss %", f"{filtered_df['MON_UNITS_LOST'].mean():.2f}%")
    c4.metric("💰 Collection %", f"{filtered_df['COLL_PERC'].mean():.2f}%")
    c5.metric("👥 Active Consumers", f"{filtered_df['ACTIVE_CONS'].sum():,.0f}")
    st.divider()

    # --- Worst Performer Panel ---
    worst_df = analysis_df.groupby("SDIV_NAME").agg({
        "PRO_PERC_LOSS_TD": "mean",
        "PRO_ATC_LOSS": "mean",
        "COLL_PERC": "mean",
        "ACTIVE_CONS": "max",
        "PRO_UNITS_LOST": "sum",
        "PRO_WHEELED_UNITS": "sum",
        "PRO_UNITS_NET_MET": "sum",
        "ASSMNT_PRO": "sum",
        "PAY_TOT_PRO": "sum"
    }).reset_index()
    worst_df["NEPRA_VIOLATION"] = worst_df["PRO_PERC_LOSS_TD"] > NEPRA_LOSS_LIMIT

    if not worst_df[worst_df["NEPRA_VIOLATION"]].empty:
        worst = (
            worst_df[worst_df["NEPRA_VIOLATION"]]
            .sort_values(by=["PRO_PERC_LOSS_TD", "PRO_ATC_LOSS", "ACTIVE_CONS"], ascending=[False, False, False])
            .iloc[0]
        )

        st.markdown("## 🚨 National Worst Performing DISCO")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "📉 Avg Loss %",
            f"{worst['PRO_PERC_LOSS_TD']:.2f}%",
            delta=f"+{worst['PRO_PERC_LOSS_TD'] - NEPRA_LOSS_LIMIT:.2f}% vs NEPRA",
            delta_color="inverse"
        )
        c2.metric("🔥 AT&C Loss %", f"{worst['PRO_ATC_LOSS']:.2f}%")
        c3.metric("💰 Collection %", f"{worst['COLL_PERC']:.2f}%")
        c4.metric("👥 Consumers Affected", f"{int(worst['ACTIVE_CONS']):,}")

        st.error(
            f"""
**{worst['SDIV_NAME']}** is the **worst performing DISCO** for the selected period.

**Key Policy Concerns**
• Loss far exceeds NEPRA limit (4.1%)  
• High AT&C loss indicates theft / inefficiency  
• Recovery pressure despite large consumer base  
• Wheeled & system losses worsening fiscal stress  
"""
        )

    # --- Loss vs Collection Scatter ---
    st.markdown("## 📊 Loss vs Collection (Policy Quadrant View)")
    fig = px.scatter(
        worst_df,
        x="PRO_PERC_LOSS_TD",
        y="COLL_PERC",
        size="ACTIVE_CONS",
        text="SDIV_NAME",
        labels={"PRO_PERC_LOSS_TD": "Loss %", "COLL_PERC": "Collection %"},
        color=worst_df["NEPRA_VIOLATION"].map({True: "❌ Violation", False: "✅ Compliant"})
    )
    fig.add_vline(x=NEPRA_LOSS_LIMIT, line_dash="dash", line_color="red", annotation_text="NEPRA Limit 4.1%")
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

    # --- Historical Loss Trend ---
    st.markdown("## 📉 Historical Loss Trend (Progressive)")
    trend_df = analysis_df.groupby(["BILLING_MONTH", "SDIV_NAME"])["PRO_PERC_LOSS_TD"].mean().reset_index()
    fig = px.line(trend_df, x="BILLING_MONTH", y="PRO_PERC_LOSS_TD", color="SDIV_NAME", markers=True)
    fig.add_hline(y=NEPRA_LOSS_LIMIT, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

    # --- Wheeled & Net-Metered Units ---
    st.markdown("## 🔌 Wheeled & Net-Metered Units Impact")
    wheel_df = analysis_df.groupby("SDIV_NAME").agg({"PRO_WHEELED_UNITS": "sum", "PRO_UNITS_NET_MET": "sum"}).reset_index()
    fig = px.bar(wheel_df, x="SDIV_NAME", y=["PRO_WHEELED_UNITS", "PRO_UNITS_NET_MET"], barmode="group", title="Wheeled vs Net-Metered Units")
    st.plotly_chart(fig, use_container_width=True)

    # --- Recovery vs Assessment ---
    st.markdown("## 💰 Recovery vs Assessment (Progressive)")
    rec_df = analysis_df.groupby("SDIV_NAME").agg({"ASSMNT_PRO": "sum", "PAY_TOT_PRO": "sum"}).reset_index()
    fig = px.bar(rec_df, x="SDIV_NAME", y=["ASSMNT_PRO", "PAY_TOT_PRO"], barmode="group", title="Assessment vs Recovery")
    st.plotly_chart(fig, use_container_width=True)

# ================= TAB 2: DISCO COMPARISON =================
with tab2:
    st.markdown("## 📊 Compare Multiple DISCOs")
    disco_options = sorted(analysis_df["SDIV_NAME"].unique())
    selected_discos = st.multiselect("Select 2 or more DISCOs to compare", disco_options)

    if len(selected_discos) < 2:
        st.info("Please select at least 2 DISCOs to enable comparison.")
    else:
        compare_df = analysis_df[analysis_df["SDIV_NAME"].isin(selected_discos)]

        # --- Loss % Comparison ---
        st.markdown("### 📉 Loss % Trend")
        trend_df = compare_df.groupby(["BILLING_MONTH", "SDIV_NAME"])["PRO_PERC_LOSS_TD"].mean().reset_index()
        fig = px.line(trend_df, x="BILLING_MONTH", y="PRO_PERC_LOSS_TD", color="SDIV_NAME", markers=True)
        fig.add_hline(y=NEPRA_LOSS_LIMIT, line_dash="dash", line_color="red", annotation_text="NEPRA Limit")
        st.plotly_chart(fig, use_container_width=True)

        # --- Collection % Comparison ---
        st.markdown("### 💰 Collection % Trend")
        coll_df = compare_df.groupby(["BILLING_MONTH", "SDIV_NAME"])["COLL_PERC"].mean().reset_index()
        fig = px.line(coll_df, x="BILLING_MONTH", y="COLL_PERC", color="SDIV_NAME", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # --- AT&C Loss Comparison ---
        st.markdown("### 🔥 AT&C Loss % Trend")
        atc_df = compare_df.groupby(["BILLING_MONTH", "SDIV_NAME"])["PRO_ATC_LOSS"].mean().reset_index()
        fig = px.line(atc_df, x="BILLING_MONTH", y="PRO_ATC_LOSS", color="SDIV_NAME", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # --- Wheeled vs Net-Metered Comparison ---
        st.markdown("### 🔌 Wheeled vs Net-Metered Units")
        wheel_df = compare_df.groupby("SDIV_NAME").agg({"PRO_WHEELED_UNITS": "sum", "PRO_UNITS_NET_MET": "sum"}).reset_index()
        fig = px.bar(wheel_df, x="SDIV_NAME", y=["PRO_WHEELED_UNITS", "PRO_UNITS_NET_MET"], barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        # --- Assessment vs Recovery Comparison ---
        st.markdown("### 💰 Assessment vs Recovery")
        rec_df = compare_df.groupby("SDIV_NAME").agg({"ASSMNT_PRO": "sum", "PAY_TOT_PRO": "sum"}).reset_index()
        fig = px.bar(rec_df, x="SDIV_NAME", y=["ASSMNT_PRO", "PAY_TOT_PRO"], barmode="group")
        st.plotly_chart(fig, use_container_width=True)

# ================= FOOTER =================
st.markdown("""
<hr>
<p style="text-align:center;color:gray">
National Power Sector Monitoring Dashboard | NEPRA-Anchored | Executive View
</p>
""", unsafe_allow_html=True)
