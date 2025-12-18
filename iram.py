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

# ================= UI STYLES (ONLY UI) =================
st.markdown("""
<style>
.kpi-card {
    background: linear-gradient(135deg, #0b3d91, #1f78b4);
    padding: 20px;
    border-radius: 16px;
    color: white;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.25);
}
.kpi-icon { font-size: 34px; }
.kpi-title { font-size: 15px; opacity: 0.85; }
.kpi-value { font-size: 30px; font-weight: 700; }
.kpi-sub { font-size: 13px; opacity: 0.75; }

.red-card { background: linear-gradient(135deg, #8b0000, #c0392b); }
.green-card { background: linear-gradient(135deg, #0f5132, #198754); }
.orange-card { background: linear-gradient(135deg, #9a3412, #f97316); }
</style>
""", unsafe_allow_html=True)

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

analysis_df = filtered_df[
    (filtered_df["SDIV_NAME"] != "ALL DISCOs") &
    (filtered_df["ACTIVE_CONS"] > 0)
].copy()

# ================= DISCO → PROVINCE MAPPING =================
DISCO_PROVINCE_MAP = {
    "LESCO": "Punjab",
    "GEPCO": "Punjab",
    "FESCO": "Punjab",
    "IESCO": "Punjab",
    "MEPCO": "Punjab",
    "HESCO": "Sindh",
    "SEPCO": "Sindh",
    "PESCO": "KPK",
    "HAZECO": "KPK",
    "TESCO": "KPK",
    "QESCO": "Balochistan"
}

# Add PROVINCE column to analysis_df
analysis_df["PROVINCE"] = analysis_df["SDIV_NAME"].map(DISCO_PROVINCE_MAP)
PROVINCE_COL = "PROVINCE"

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(
    ["National Overview", "DISCO Comparison", "🏆 DISCO Performance Ranking"]
)

# ================= TAB 1 =================
with tab1:

    # =========================================================
    # NATIONAL SNAPSHOT (NEPRA MONTHLY PERFORMANCE VIEW)
    # =========================================================
    st.markdown("## National Power Sector Snapshot")

    st.markdown("""
    This section presents a consolidated national-level view of power sector performance
    based strictly on reported operational and commercial indicators.

    All figures are derived directly from DISCO submissions for the selected billing period(s)
    and reflect aggregate system behavior rather than statistical averages.
    """)

    c1, c2, c3, c4, c5,c6 = st.columns(6)

    total_energy = filtered_df["MONTHLY_ENERGY"].sum()
    total_billed = filtered_df["MON_UNITS_BILLED"].sum()
    total_lost_units = filtered_df["PRO_UNITS_LOST"].sum()
    total_net_meter = filtered_df["PRO_UNITS_NET_MET"].sum()
    total_consumers = filtered_df["ACTIVE_CONS"].sum()
    total_loss_td= filtered_df["MON_PERC_LOSS_TD"].sum()

    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">⚡</div>
            <div class="kpi-title">Energy Purchased</div>
            <div class="kpi-value">{total_energy:,.0f}</div>
            <div class="kpi-sub">Reported Units</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card green-card">
            <div class="kpi-icon">📨</div>
            <div class="kpi-title">Units Billed</div>
            <div class="kpi-value">{total_billed:,.0f}</div>
            <div class="kpi-sub">Reported Units</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card red-card">
            <div class="kpi-icon">📉</div>
            <div class="kpi-title">Units Lost</div>
            <div class="kpi-value">{total_lost_units:,.0f}</div>
            <div class="kpi-sub">Reported T&D Loss Units</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card orange-card">
            <div class="kpi-icon">🔌</div>
            <div class="kpi-title">Net Metered Units</div>
            <div class="kpi-value">{total_net_meter:,.0f}</div>
            <div class="kpi-sub">Structural System Impact</div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">👥</div>
            <div class="kpi-title">Active Consumers</div>
            <div class="kpi-value">{total_consumers:,.0f}</div>
            <div class="kpi-sub">Reported Base</div>
        </div>
        """, unsafe_allow_html=True)
    with c6:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">👥</div>
            <div class="kpi-title">TD Loss </div>
            <div class="kpi-value">{total_loss_td:,.0f}</div>
            <div class="kpi-sub">Reported Base</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # =========================================================
    # HIGH RISK DISCO IDENTIFICATION (NEPRA THRESHOLD BREACH)
    # =========================================================
    st.markdown("## National High-Risk DISCO (NEPRA Threshold Breach)")

    risk_df = analysis_df.groupby("SDIV_NAME").agg({
        "PRO_PERC_LOSS_TD": "mean",
        "PRO_ATC_LOSS": "mean",
        "COLL_PERC": "mean",
        "ACTIVE_CONS": "max"
    }).reset_index()

    risk_df = risk_df[risk_df["PRO_PERC_LOSS_TD"] > NEPRA_LOSS_LIMIT]

    if not risk_df.empty:
        risk_disco = risk_df.sort_values(
            by=["PRO_PERC_LOSS_TD", "PRO_ATC_LOSS", "ACTIVE_CONS"],
            ascending=False
        ).iloc[0]

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
            <div class="kpi-card red-card">
                <div class="kpi-icon">📉</div>
                <div class="kpi-title">T&D Loss %</div>
                <div class="kpi-value">{risk_disco['PRO_PERC_LOSS_TD']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="kpi-card orange-card">
                <div class="kpi-icon">🔥</div>
                <div class="kpi-title">AT&C Loss %</div>
                <div class="kpi-value">{risk_disco['PRO_ATC_LOSS']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="kpi-card green-card">
                <div class="kpi-icon">💰</div>
                <div class="kpi-title">Collection %</div>
                <div class="kpi-value">{risk_disco['COLL_PERC']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">👥</div>
                <div class="kpi-title">Consumer Base</div>
                <div class="kpi-value">{int(risk_disco['ACTIVE_CONS']):,}</div>
            </div>
            """, unsafe_allow_html=True)

        st.error(f"""
        **{risk_disco['SDIV_NAME']}** has exceeded the NEPRA-approved loss threshold
        for the selected billing period.

        Identified risk indicators:
        • Transmission & Distribution losses above regulatory limits  
        • Elevated AT&C losses  
        • Recovery efficiency pressure  
        • System performance concerns requiring management attention
        """)

    st.divider()

    # =========================================================
    # DISCO LOSS VS COLLECTION (NEPRA COMPARATIVE VIEW)
    # =========================================================
    st.markdown("## DISCO Loss vs Collection Performance (NEPRA Comparative View)")

    comp_df = analysis_df.groupby("SDIV_NAME").agg({
        "PRO_PERC_LOSS_TD": "mean",
        "COLL_PERC": "mean",
        "ACTIVE_CONS": "max"
    }).reset_index()

    comp_df["NEPRA_STATUS"] = np.where(
        comp_df["PRO_PERC_LOSS_TD"] > NEPRA_LOSS_LIMIT,
        "❌ Non-Compliant",
        "✅ Compliant"
    )

    fig = px.scatter(
        comp_df,
        x="PRO_PERC_LOSS_TD",
        y="COLL_PERC",
        size="ACTIVE_CONS",
        text="SDIV_NAME",
        color="NEPRA_STATUS"
    )
    fig.add_vline(x=NEPRA_LOSS_LIMIT, line_dash="dash", line_color="red")
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # NET METERING VS NATIONAL ENERGY TREND
    # =========================================================
    st.markdown("## Net Metering Units vs National Energy (Structural Impact Trend)")

    nm_trend = filtered_df.groupby("BILLING_MONTH").agg({
        "PRO_UNITS_NET_MET": "sum",
        "MONTHLY_ENERGY": "sum"
    }).reset_index()

    fig = px.line(
        nm_trend,
        x="BILLING_MONTH",
        y=["PRO_UNITS_NET_MET", "MONTHLY_ENERGY"],
        markers=True,
        labels={"value": "Reported Units", "variable": "Metric"}
    )
    st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # WHEELED VS NET METERED UNITS (SYSTEM IMPACT)
    # =========================================================
    st.markdown("## Wheeled Energy and Net-Metered Units (Reported System Impact)")

    sys_df = filtered_df.groupby("SDIV_NAME").agg({
        "PRO_WHEELED_UNITS": "sum",
        "PRO_UNITS_NET_MET": "sum"
    }).reset_index()

    fig = px.bar(
        sys_df,
        x="SDIV_NAME",
        y=["PRO_WHEELED_UNITS", "PRO_UNITS_NET_MET"],
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # ASSESSMENT VS RECOVERY (COMMERCIAL PERFORMANCE)
    # =========================================================
    st.markdown("## Assessment vs Recovery (Commercial Performance Overview)")

    rec_df = filtered_df.groupby("SDIV_NAME").agg({
        "ASSMNT_PRO": "sum",
        "PAY_TOT_PRO": "sum"
    }).reset_index()

    fig = px.bar(
        rec_df,
        x="SDIV_NAME",
        y=["ASSMNT_PRO", "PAY_TOT_PRO"],
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)
# ================= TAB 2 =================
with tab2:

    st.markdown("## DISCO Comparative Performance (NEPRA Monthly View)")

    st.markdown("""
    This section enables side-by-side comparison of DISCO performance using
    reported monthly indicators as submitted to NEPRA.

    The analysis is trend-based and does not apply normalization, scoring,
    or composite performance calculations.
    """)

    disco_options = sorted(analysis_df["SDIV_NAME"].unique())
    selected_discos = st.multiselect(
        "Select DISCOs for comparison",
        disco_options
    )

    if len(selected_discos) < 2:
        st.info("Please select at least two DISCOs to enable comparative analysis.")
        st.stop()

    compare_df = analysis_df[analysis_df["SDIV_NAME"].isin(selected_discos)]

    # -----------------------------------------------------
    # T&D LOSS TREND (REPORTED)
    # -----------------------------------------------------
    st.markdown("### Transmission & Distribution Loss Trend (Reported %)")

    loss_trend = compare_df.groupby(
        ["BILLING_MONTH", "SDIV_NAME"]
    )["PRO_PERC_LOSS_TD"].mean().reset_index()

    fig = px.line(
        loss_trend,
        x="BILLING_MONTH",
        y="PRO_PERC_LOSS_TD",
        color="SDIV_NAME",
        markers=True
    )
    fig.add_hline(y=NEPRA_LOSS_LIMIT, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # AT&C LOSS TREND (REPORTED)
    # -----------------------------------------------------
    st.markdown("### AT&C Loss Trend (Reported %)")

    atc_trend = compare_df.groupby(
        ["BILLING_MONTH", "SDIV_NAME"]
    )["PRO_ATC_LOSS"].mean().reset_index()

    fig = px.line(
        atc_trend,
        x="BILLING_MONTH",
        y="PRO_ATC_LOSS",
        color="SDIV_NAME",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # COLLECTION PERFORMANCE TREND
    # -----------------------------------------------------
    st.markdown("### Collection Performance Trend (Reported %)")

    coll_trend = compare_df.groupby(
        ["BILLING_MONTH", "SDIV_NAME"]
    )["COLL_PERC"].mean().reset_index()

    fig = px.line(
        coll_trend,
        x="BILLING_MONTH",
        y="COLL_PERC",
        color="SDIV_NAME",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # NET METERING COMPARISON (ABSOLUTE IMPACT)
    # -----------------------------------------------------
    st.markdown("### Net Metering Units Comparison (Reported Units)")

    nm_df = compare_df.groupby("SDIV_NAME")["PRO_UNITS_NET_MET"].sum().reset_index()

    fig = px.bar(
        nm_df,
        x="SDIV_NAME",
        y="PRO_UNITS_NET_MET",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # ASSESSMENT VS RECOVERY
    # -----------------------------------------------------
    st.markdown("### Assessment vs Recovery (Commercial Performance)")

    rec_df = compare_df.groupby("SDIV_NAME").agg({
        "ASSMNT_PRO": "sum",
        "PAY_TOT_PRO": "sum"
    }).reset_index()

    fig = px.bar(
        rec_df,
        x="SDIV_NAME",
        y=["ASSMNT_PRO", "PAY_TOT_PRO"],
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)

# ================= TAB 3 =================
with tab3:

    st.markdown("## DISCO Performance Ranking (NEPRA Reported Indicators)")

    st.markdown("""
    Rankings are presented independently for each performance indicator
    using reported values only. No composite indices or weighted scores
    are applied.
    """)

    # Use latest selected billing month
    latest_month = filtered_df["BILLING_MONTH"].max()
    latest_df = analysis_df[analysis_df["BILLING_MONTH"] == latest_month]

    # -----------------------------------------------------
    # T&D LOSS RANKING
    # -----------------------------------------------------
    st.markdown("### 🔻 T&D Loss Ranking (Higher Loss = Higher Risk)")

    loss_rank = latest_df.groupby("SDIV_NAME")["PRO_PERC_LOSS_TD"].mean().reset_index()
    loss_rank = loss_rank.sort_values("PRO_PERC_LOSS_TD", ascending=False)

    st.dataframe(loss_rank, use_container_width=True)

    # -----------------------------------------------------
    # AT&C LOSS RANKING
    # -----------------------------------------------------
    st.markdown("### 🔥 AT&C Loss Ranking (Higher Loss = Higher Risk)")

    atc_rank = latest_df.groupby("SDIV_NAME")["PRO_ATC_LOSS"].mean().reset_index()
    atc_rank = atc_rank.sort_values("PRO_ATC_LOSS", ascending=False)

    st.dataframe(atc_rank, use_container_width=True)

    # -----------------------------------------------------
    # COLLECTION PERFORMANCE RANKING
    # -----------------------------------------------------
    st.markdown("### 💰 Collection Performance Ranking (Higher is Better)")

    coll_rank = latest_df.groupby("SDIV_NAME")["COLL_PERC"].mean().reset_index()
    coll_rank = coll_rank.sort_values("COLL_PERC", ascending=False)

    st.dataframe(coll_rank, use_container_width=True)

    # -----------------------------------------------------
    # NET METERING IMPACT RANKING
    # -----------------------------------------------------
    st.markdown("### 🔌 Net Metering Impact Ranking (Reported Units)")

    nm_rank = latest_df.groupby("SDIV_NAME")["PRO_UNITS_NET_MET"].sum().reset_index()
    nm_rank = nm_rank.sort_values("PRO_UNITS_NET_MET", ascending=False)

    st.dataframe(nm_rank, use_container_width=True)

    # -----------------------------------------------------
    # PROVINCE-WISE LOSS HEATMAP
    # -----------------------------------------------------
    st.markdown("## Province-wise Loss Overview (Reported %)")

    prov_df = latest_df.groupby(PROVINCE_COL).agg({
        "PRO_PERC_LOSS_TD": "mean",
        "PRO_ATC_LOSS": "mean"
    }).reset_index()

    fig = px.imshow(
        prov_df.set_index(PROVINCE_COL),
        color_continuous_scale="Reds",
        aspect="auto"
    )
    st.plotly_chart(fig, use_container_width=True)


# ================= FOOTER =================
st.markdown("""
<hr>
<p style="text-align:center;color:gray">
National Power Sector Monitoring Dashboard | NEPRA-Anchored | Executive View
</p>
""", unsafe_allow_html=True)
