import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ================= CONFIG =================
st.set_page_config(
    page_title="National DISCO Performance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

NEPRA_LOSS_LIMIT = 4.1

# ================= COMPANY COLOR SCHEME =================
COLORS = {
    "primary": "#800000",      # Maroon (Company Primary)
    "secondary": "#fd8c17",    # Orange (Company Secondary)
    "accent": "#FFFFFF",       # White
    "success": "#4CAF50",      # Green
    "warning": "#FFC107",      # Amber
    "danger": "#FF5252",       # Red
    "info": "#2196F3",         # Light Blue
    "dark": "#263238",         # Dark Blue Gray
    "light": "#F5F5F5",        # Light Gray
    "white": "#FFFFFF",
    "maroon_light": "#A00000",
    "orange_light": "#FFA726",
    "gradient_start": "#800000",
    "gradient_mid": "#fd8c17",
    "gradient_end": "#FFD700"
}

# ================= EXECUTIVE UI STYLES =================
st.markdown(f"""
<style>
/* Executive Dashboard Theme */
:root {{
    --primary: {COLORS["primary"]};
    --secondary: {COLORS["secondary"]};
    --accent: {COLORS["accent"]};
    --success: #4CAF50;
    --warning: #FFC107;
    --danger: #FF5252;
    --dark: #1a1a1a;
    --light: #f8f9fa;
}}

/* Executive Header */
.executive-header {{
    background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["secondary"]});
    padding: 30px;
    border-radius: 15px;
    margin-bottom: 30px;
    text-align: center;
    color: white;
    box-shadow: 0 8px 32px rgba(128, 0, 0, 0.2);
    border: 1px solid rgba(253, 140, 23, 0.3);
}}

/* Executive Cards */
.executive-card {{
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 25px;
    border: 1px solid rgba(128, 0, 0, 0.1);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}}

.executive-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]});
}}

/* Executive KPI Cards */
.kpi-executive {{
    background: linear-gradient(135deg, {COLORS["dark"]}, #2c3e50);
    border-radius: 12px;
    padding: 20px;
    color: white;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    border-left: 4px solid {COLORS["primary"]};
}}

.kpi-executive.primary {{ 
    background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["maroon_light"]});
    border-left: 4px solid {COLORS["secondary"]};
}}
.kpi-executive.success {{ 
    background: linear-gradient(135deg, #2E7D32, #4CAF50);
    border-left: 4px solid #81C784;
}}
.kpi-executive.warning {{ 
    background: linear-gradient(135deg, #F57C00, #FFA726);
    border-left: 4px solid {COLORS["primary"]};
}}
.kpi-executive.danger {{ 
    background: linear-gradient(135deg, {COLORS["danger"]}, #EF5350);
    border-left: 4px solid #FF8A80;
}}
.kpi-executive.info {{ 
    background: linear-gradient(135deg, #1565C0, #2196F3);
    border-left: 4px solid #64B5F6;
}}

.kpi-executive:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}}

.kpi-value {{
    font-size: 28px;
    font-weight: 800;
    color: white;
    line-height: 1.2;
    margin: 10px 0 5px;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}}

.kpi-label {{
    font-size: 13px;
    color: rgba(255, 255, 255, 0.9);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}}

.kpi-icon {{
    font-size: 22px;
    margin-bottom: 10px;
    opacity: 0.9;
}}

/* Executive Status Badges */
.status-executive {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.status-good {{
    background: linear-gradient(135deg, #4CAF50, #66BB6A);
    color: white;
    box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}}

.status-warning {{
    background: linear-gradient(135deg, #FFC107, #FFD54F);
    color: {COLORS["dark"]};
    box-shadow: 0 2px 8px rgba(255, 193, 7, 0.3);
}}

.status-bad {{
    background: linear-gradient(135deg, {COLORS["danger"]}, #EF5350);
    color: white;
    box-shadow: 0 2px 8px rgba(255, 82, 82, 0.3);
}}

/* Executive Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 2px;
    background: {COLORS["light"]};
    padding: 3px;
    border-radius: 10px;
    border: 1px solid rgba(128, 0, 0, 0.1);
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    padding: 10px 20px;
    background: transparent;
    font-weight: 600;
    color: {COLORS["dark"]};
    border: 2px solid transparent;
    transition: all 0.3s ease;
    font-size: 14px;
}}

.stTabs [data-baseweb="tab"]:hover {{
    background: rgba(128, 0, 0, 0.05);
    border-color: rgba(128, 0, 0, 0.1);
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["secondary"]});
    color: white;
    box-shadow: 0 3px 10px rgba(128, 0, 0, 0.2);
    border-color: transparent;
}}

/* Executive Filters */
.filter-executive {{
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 25px;
    border: 1px solid rgba(128, 0, 0, 0.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}}

/* Responsive Design */
@media (max-width: 768px) {{
    .kpi-value {{
        font-size: 22px;
    }}
    
    .executive-card {{
        padding: 20px;
    }}
}}
</style>
""", unsafe_allow_html=True)

# ================= EXECUTIVE HEADER =================
st.markdown(f"""
<div class="executive-header">
    <h1 style="margin: 0; font-size: 32px; font-weight: 800;">
        ⚡ NATIONAL DISCO PERFORMANCE DASHBOARD
    </h1>
    <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.95; font-weight: 500;">
        Executive Level Monitoring | NEPRA Compliance | Power Sector Analytics
    </p>
</div>
""", unsafe_allow_html=True)

# ================= DATA UPLOAD =================
with st.container():
    st.markdown('<div class="filter-executive">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader("📤 Upload DISCO Performance Dataset", 
                                        type=["xlsx", "csv"], 
                                        help="Upload Excel or CSV file with DISCO performance data")
    
    with col2:
        if uploaded_file:
            st.success("✅ Data loaded successfully", icon="🎯")
    st.markdown('</div>', unsafe_allow_html=True)

if not uploaded_file:
    st.info("👑 Please upload a DISCO dataset to begin executive analysis", icon="ℹ️")
    st.stop()

# Load data
try:
    if uploaded_file.name.endswith("xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"❌ Error loading file: {str(e)}")
    st.stop()

# ================= DATA PREP =================
df["BILLING_MONTH"] = pd.to_datetime(df["BILLING_MONTH"])
df["MONTH"] = df["BILLING_MONTH"].dt.strftime("%b %Y")
df["YEAR"] = df["BILLING_MONTH"].dt.year
df["MONTH_NUM"] = df["BILLING_MONTH"].dt.month

# Sort months chronologically
months = sorted(df["MONTH"].unique(), 
                key=lambda x: pd.to_datetime(x, format="%b %Y"))

# ================= EXECUTIVE FILTERS =================
with st.container():
    st.markdown('<div class="filter-executive">', unsafe_allow_html=True)
    st.markdown("### 🎯 Executive View Selector")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Time period selection
        time_option = st.selectbox(
            "📅 Time Period",
            ["Single Month", "All Months", "Year-to-Date", "Last 6 Months", "Last 12 Months"],
            help="Choose time period for analysis"
        )
        
        if time_option == "Single Month":
            selected_month = st.selectbox(
                "Select Month",
                months,
                index=len(months)-1 if months else 0,
                help="Select specific month for analysis"
            )
            month_filter = [selected_month]
        elif time_option == "All Months":
            month_filter = months
            selected_month = "All Months"
        elif time_option == "Year-to-Date":
            current_year = datetime.now().year
            month_filter = [m for m in months if pd.to_datetime(m, format="%b %Y").year == current_year]
            selected_month = f"Year {current_year}"
        elif time_option == "Last 6 Months":
            month_filter = months[-6:] if len(months) >= 6 else months
            selected_month = "Last 6 Months"
        else:  # Last 12 Months
            month_filter = months[-12:] if len(months) >= 12 else months
            selected_month = "Last 12 Months"
    
    with col2:
        # DISCO selection
        disco_options = sorted(df["SDIV_NAME"].unique())
        selected_discos = st.multiselect(
            "🏢 Select DISCOs",
            disco_options,
            default=disco_options,
            help="Select one or more DISCOs"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Filter data
filtered_df = df[(df["MONTH"].isin(month_filter)) & 
                 (df["SDIV_NAME"].isin(selected_discos))].copy()

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters. Please adjust your selection.")
    st.stop()

# ================= HELPER FUNCTIONS =================
def format_number(num, include_sign=False):
    """Format numbers for executive display"""
    if pd.isna(num):
        return "N/A"
    
    num_abs = abs(num)
    if num_abs >= 1_000_000_000:
        formatted = f"{num/1_000_000_000:.1f}B"
    elif num_abs >= 1_000_000:
        formatted = f"{num/1_000_000:.1f}M"
    elif num_abs >= 1_000:
        formatted = f"{num/1_000:.1f}K"
    else:
        formatted = f"{num:,.0f}"
    
    if include_sign and num != 0:
        sign = "+" if num > 0 else ""
        return f"{sign}{formatted}"
    return formatted

def create_comparison_bar_chart(data_dict, title, y_title, is_percentage=False):
    """Create bar chart for three-month comparison"""
    fig = go.Figure()
    
    periods = list(data_dict.keys())
    
    for period in periods:
        period_data = data_dict[period]
        
        x_values = list(period_data.keys())
        y_values = list(period_data.values())
        
        fig.add_trace(go.Bar(
            name=period,
            x=x_values,
            y=y_values,
            text=[f"{v:.1f}%" if is_percentage else format_number(v) for v in y_values],
            textposition='auto',
            textfont=dict(size=11)
        ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color=COLORS["dark"])
        ),
        barmode='group',
        xaxis_title="DISCO",
        yaxis_title=y_title,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS["dark"], size=12),
        margin=dict(t=60, b=100, l=60, r=30),
        xaxis_tickangle=-45
    )
    
    return fig

def create_trend_chart(data, disco_name, title):
    """Create trend chart for multiple metrics"""
    fig = go.Figure()
    
    # Add T&D Loss trend
    fig.add_trace(go.Scatter(
        x=data["MONTH"],
        y=data["MON_PERC_LOSS_TD"],
        mode='lines+markers',
        name='T&D Loss %',
        line=dict(color=COLORS["danger"], width=3),
        marker=dict(size=8),
        yaxis='y'
    ))
    
    # Add Collection % trend
    fig.add_trace(go.Scatter(
        x=data["MONTH"],
        y=data["COLL_PERC"],
        mode='lines+markers',
        name='Collection %',
        line=dict(color=COLORS["success"], width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"{disco_name} - {title}",
            font=dict(size=16, color=COLORS["dark"])
        ),
        xaxis_title="Month",
        yaxis=dict(
            title="T&D Loss %",
            titlefont=dict(color=COLORS["danger"]),
            tickfont=dict(color=COLORS["danger"])
        ),
        yaxis2=dict(
            title="Collection %",
            titlefont=dict(color=COLORS["success"]),
            tickfont=dict(color=COLORS["success"]),
            anchor="x",
            overlaying="y",
            side="right"
        ),
        height=450,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS["dark"], size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=60, b=60, l=60, r=60)
    )
    
    return fig

# ================= DASHBOARD LAYOUT =================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Executive Overview", 
    "📊 Performance Analysis", 
    "📈 Trend & Comparison", 
    "🔍 Deep Insights"
])

# ================= TAB 1: EXECUTIVE OVERVIEW =================
with tab1:
    st.markdown(f"### 🏆 NATIONAL PERFORMANCE DASHBOARD - {selected_month}")
    
    # Calculate aggregated data
    if time_option == "Single Month":
        analysis_df = filtered_df.copy()
    else:
        # Aggregate data for multiple months
        agg_dict = {
            'MONTHLY_ENERGY': 'sum',
            'CUMULATIVE_ENERGY': 'last',
            'MON_UNITS_BILLED': 'sum',
            'PRO_UNITS_BILLED': 'last',
            'MON_UNITS_RECVD': 'sum',
            'PRO_UNITS_RECVD': 'last',
            'MON_UNITS_LOST': 'sum',
            'PRO_UNITS_LOST': 'last',
            'MON_ATC_LOSS': 'mean',
            'PRO_ATC_LOSS': 'mean',
            'MON_PERC_LOSS_TD': 'mean',
            'PRO_PERC_LOSS_TD': 'mean',
            'MON_UNITS_NET_MET': 'sum',
            'PRO_UNITS_NET_MET': 'sum',
            'MON_WHEELED_UNITS': 'sum',
            'PRO_WHEELED_UNITS': 'sum',
            'ASSMNT_MON': 'sum',
            'ASSMNT_PRO': 'sum',
            'PAY_TOT_MON': 'sum',
            'PAY_TOT_PRO': 'sum',
            'COLL_PERC': 'mean',
            'ACTIVE_CONS': 'last'
        }
        
        analysis_df = filtered_df.groupby('SDIV_NAME').agg(agg_dict).reset_index()
    
    # Executive KPIs
    st.markdown('<div class="executive-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_energy = analysis_df["MONTHLY_ENERGY"].sum()
        st.markdown(f"""
        <div class="kpi-executive primary">
            <div class="kpi-icon">⚡</div>
            <div class="kpi-value">{format_number(total_energy)}</div>
            <div class="kpi-label">Total Energy</div>
            <div style="font-size: 11px; opacity: 0.8;">MKWh</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_billed = analysis_df["MON_UNITS_BILLED"].sum()
        st.markdown(f"""
        <div class="kpi-executive success">
            <div class="kpi-icon">💰</div>
            <div class="kpi-value">{format_number(total_billed)}</div>
            <div class="kpi-label">Units Billed</div>
            <div style="font-size: 11px; opacity: 0.8;">Monthly</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_net_meter = analysis_df["MON_UNITS_NET_MET"].sum()
        st.markdown(f"""
        <div class="kpi-executive info">
            <div class="kpi-icon">🔌</div>
            <div class="kpi-value">{format_number(total_net_meter)}</div>
            <div class="kpi-label">Net Metering</div>
            <div style="font-size: 11px; opacity: 0.8;">Total Units</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_td_loss = analysis_df["MON_PERC_LOSS_TD"].mean()
        status = "✅" if avg_td_loss <= NEPRA_LOSS_LIMIT else "❌"
        st.markdown(f"""
        <div class="kpi-executive {"danger" if avg_td_loss > NEPRA_LOSS_LIMIT else "success"}">
            <div class="kpi-icon">📉</div>
            <div class="kpi-value">{avg_td_loss:.1f}% {status}</div>
            <div class="kpi-label">Avg T&D Loss</div>
            <div style="font-size: 11px; opacity: 0.8;">Limit: {NEPRA_LOSS_LIMIT}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        avg_collection = analysis_df["COLL_PERC"].mean()
        st.markdown(f"""
        <div class="kpi-executive {"success" if avg_collection >= 90 else "warning" if avg_collection >= 70 else "danger"}">
            <div class="kpi-icon">📊</div>
            <div class="kpi-value">{avg_collection:.1f}%</div>
            <div class="kpi-label">Collection Rate</div>
            <div style="font-size: 11px; opacity: 0.8;">National Average</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance Distribution
    st.markdown('<div class="executive-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Performance Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Energy Distribution Pie Chart
        energy_by_disco = analysis_df.groupby("SDIV_NAME")["MONTHLY_ENERGY"].sum().reset_index()
        fig = px.pie(
            energy_by_disco,
            values="MONTHLY_ENERGY",
            names="SDIV_NAME",
            title="Energy Distribution by DISCO",
            hole=0.4,
            color_discrete_sequence=[COLORS["primary"], COLORS["secondary"], COLORS["info"], 
                                   COLORS["success"], COLORS["warning"], COLORS["danger"]]
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>Energy: %{value:,.0f} MKWh<br>Share: %{percent}<extra></extra>"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # NEPRA Compliance Status
        compliant_df = analysis_df.copy()
        compliant_df["STATUS"] = compliant_df["MON_PERC_LOSS_TD"].apply(
            lambda x: "Compliant" if x <= NEPRA_LOSS_LIMIT else "Non-Compliant"
        )
        status_counts = compliant_df["STATUS"].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.4,
            marker=dict(colors=[COLORS["success"], COLORS["danger"]]),
            textinfo='label+percent',
            textposition='inside',
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>"
        )])
        
        compliant_count = len(compliant_df[compliant_df["STATUS"] == "Compliant"])
        total_count = len(compliant_df)
        
        fig.update_layout(
            title="NEPRA Compliance Status",
            annotations=[dict(
                text=f'{compliant_count}/{total_count}<br>DISCOs',
                x=0.5, y=0.5, font_size=14, showarrow=False
            )],
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance Matrix
    st.markdown('<div class="executive-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Performance Matrix")
    
    fig = px.scatter(
        analysis_df,
        x="MON_PERC_LOSS_TD",
        y="COLL_PERC",
        size="MONTHLY_ENERGY",
        color="SDIV_NAME",
        hover_name="SDIV_NAME",
        hover_data={
            "MON_PERC_LOSS_TD": ":.1f",
            "PRO_PERC_LOSS_TD": ":.1f",
            "COLL_PERC": ":.1f",
            "MON_UNITS_NET_MET": ":,.0f",
            "MONTHLY_ENERGY": ":,.0f",
            "SDIV_NAME": False
        },
        labels={
            "MON_PERC_LOSS_TD": "T&D Loss % (MON)",
            "COLL_PERC": "Collection %",
            "MONTHLY_ENERGY": "Monthly Energy (Size)",
            "SDIV_NAME": "DISCO"
        },
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Add performance quadrants
    fig.add_hline(y=90, line_dash="dash", line_color=COLORS["success"], 
                 annotation_text="Target: 90%", annotation_position="top right")
    fig.add_vline(x=NEPRA_LOSS_LIMIT, line_dash="dash", line_color=COLORS["danger"],
                 annotation_text=f"NEPRA Limit: {NEPRA_LOSS_LIMIT}%", 
                 annotation_position="top left")
    
    fig.update_layout(
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color=COLORS["dark"], size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB 2: PERFORMANCE ANALYSIS =================
with tab2:
    st.markdown("### 📊 DETAILED PERFORMANCE ANALYSIS")
    
    # Metrics Selection
    st.markdown('<div class="filter-executive">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        metric_category = st.selectbox(
            "Select Metric Category",
            ["All Metrics", "Loss Analysis", "Commercial Performance", "Energy Metrics", "Consumer Metrics"],
            key="metric_category"
        )
    
    with col2:
        if metric_category == "All Metrics":
            selected_metrics = st.multiselect(
                "Select Metrics",
                ["T&D Loss % (MON)", "T&D Loss % (PRO)", "AT&C Loss % (MON)", "AT&C Loss % (PRO)",
                 "Collection %", "Assessment (PRO)", "Recovery (PRO)",
                 "Monthly Energy", "Units Billed (MON)", "Net Metering (MON)",
                 "Active Consumers"],
                default=["T&D Loss % (MON)", "Collection %", "Monthly Energy"],
                key="all_metrics"
            )
        elif metric_category == "Loss Analysis":
            selected_metrics = st.multiselect(
                "Select Metrics",
                ["T&D Loss % (MON)", "T&D Loss % (PRO)", "AT&C Loss % (MON)", "AT&C Loss % (PRO)"],
                default=["T&D Loss % (MON)", "AT&C Loss % (MON)"],
                key="loss_metrics"
            )
        elif metric_category == "Commercial Performance":
            selected_metrics = st.multiselect(
                "Select Metrics",
                ["Collection %", "Assessment (PRO)", "Recovery (PRO)"],
                default=["Collection %"],
                key="commercial_metrics"
            )
        elif metric_category == "Energy Metrics":
            selected_metrics = st.multiselect(
                "Select Metrics",
                ["Monthly Energy", "Units Billed (MON)", "Net Metering (MON)"],
                default=["Monthly Energy"],
                key="energy_metrics"
            )
        else:
            selected_metrics = st.multiselect(
                "Select Metrics",
                ["Active Consumers"],
                default=["Active Consumers"],
                key="consumer_metrics"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if selected_metrics:
        # Metric mapping
        metric_map = {
            "T&D Loss % (MON)": "MON_PERC_LOSS_TD",
            "T&D Loss % (PRO)": "PRO_PERC_LOSS_TD",
            "AT&C Loss % (MON)": "MON_ATC_LOSS",
            "AT&C Loss % (PRO)": "PRO_ATC_LOSS",
            "Collection %": "COLL_PERC",
            "Assessment (PRO)": "ASSMNT_PRO",
            "Recovery (PRO)": "PAY_TOT_PRO",
            "Monthly Energy": "MONTHLY_ENERGY",
            "Units Billed (MON)": "MON_UNITS_BILLED",
            "Net Metering (MON)": "MON_UNITS_NET_MET",
            "Active Consumers": "ACTIVE_CONS"
        }
        
        # Performance Charts for each selected metric
        for metric_name in selected_metrics:
            st.markdown(f'<div class="executive-card">', unsafe_allow_html=True)
            st.markdown(f"### 📈 {metric_name} - {selected_month}")
            
            metric_col = metric_map[metric_name]
            
            # Sort data for better visualization
            chart_df = analysis_df.sort_values(metric_col, 
                                             ascending=("Loss" in metric_name))
            
            fig = go.Figure()
            
            # Add bars
            fig.add_trace(go.Bar(
                x=chart_df["SDIV_NAME"],
                y=chart_df[metric_col],
                marker_color=COLORS["primary"],
                text=[f"{v:,.0f}" if metric_col in ["MONTHLY_ENERGY", "MON_UNITS_BILLED", 
                                                  "MON_UNITS_NET_MET", "ACTIVE_CONS", 
                                                  "ASSMNT_PRO", "PAY_TOT_PRO"]
                     else f"{v:.1f}%" for v in chart_df[metric_col]],
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>" +
                             f"{metric_name}: " +
                             ("%{y:,.0f}" if metric_col in ["MONTHLY_ENERGY", "MON_UNITS_BILLED", 
                                                          "MON_UNITS_NET_MET", "ACTIVE_CONS",
                                                          "ASSMNT_PRO", "PAY_TOT_PRO"]
                             else "%{y:.1f}%") +
                             "<extra></extra>"
            ))
            
            # Add threshold line for loss metrics
            if "Loss" in metric_name:
                fig.add_hline(
                    y=NEPRA_LOSS_LIMIT,
                    line_dash="dash",
                    line_color=COLORS["danger"],
                    annotation_text=f"NEPRA Limit: {NEPRA_LOSS_LIMIT}%",
                    annotation_position="top right"
                )
            
            fig.update_layout(
                height=400,
                xaxis_title="DISCO",
                yaxis_title=metric_name,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color=COLORS["dark"], size=12),
                margin=dict(t=50, b=100, l=60, r=30),
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_value = chart_df[metric_col].mean()
                st.metric(
                    label="Average",
                    value=f"{avg_value:,.1f}" + ("%" if "%" in metric_name else ""),
                    delta=None
                )
            
            with col2:
                max_value = chart_df[metric_col].max()
                max_disco = chart_df.loc[chart_df[metric_col].idxmax(), "SDIV_NAME"]
                st.metric(
                    label="Highest",
                    value=f"{max_value:,.1f}" + ("%" if "%" in metric_name else ""),
                    delta=f"{max_disco}"
                )
            
            with col3:
                min_value = chart_df[metric_col].min()
                min_disco = chart_df.loc[chart_df[metric_col].idxmin(), "SDIV_NAME"]
                st.metric(
                    label="Lowest",
                    value=f"{min_value:,.1f}" + ("%" if "%" in metric_name else ""),
                    delta=f"{min_disco}"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📊 Please select at least one metric to display")

# ================= TAB 3: TREND & COMPARISON =================
with tab3:
    st.markdown("### 📈 TREND & COMPARATIVE ANALYSIS")
    
    # Three Month Comparison Section
    st.markdown('<div class="executive-card">', unsafe_allow_html=True)
    st.markdown("### 🔄 Three-Month Comparison Analysis")
    
    # Get available months for comparison
    available_months = sorted(df["BILLING_MONTH"].unique(), reverse=True)
    
    if len(available_months) >= 3:
        # Get three comparison periods
        current_month_date = available_months[0]
        previous_month_date = available_months[1]
        
        # Find same month previous year
        same_month_last_year = None
        for month in available_months:
            if month.year == current_month_date.year - 1 and month.month == current_month_date.month:
                same_month_last_year = month
                break
        
        # If not found, use the third most recent month
        if same_month_last_year is None and len(available_months) >= 3:
            same_month_last_year = available_months[2]
        
        if same_month_last_year:
            # Create month labels
            month1_label = current_month_date.strftime("%b %Y")
            month2_label = previous_month_date.strftime("%b %Y")
            month3_label = same_month_last_year.strftime("%b %Y")
            
            col1, col2 = st.columns(2)
            
            with col1:
                compare_metric = st.selectbox(
                    "Select Metric for Comparison",
                    ["T&D Loss %", "Collection %", "Monthly Energy", "Net Metering"],
                    key="trend_metric"
                )
            
            with col2:
                st.info(f"""
                **Comparison Periods:**
                - Current: {month1_label}
                - Previous: {month2_label}
                - Year Ago: {month3_label}
                """)
            
            # Get data for three periods
            metric_map = {
                "T&D Loss %": "MON_PERC_LOSS_TD",
                "Collection %": "COLL_PERC",
                "Monthly Energy": "MONTHLY_ENERGY",
                "Net Metering": "MON_UNITS_NET_MET"
            }
            
            metric_col = metric_map[compare_metric]
            
            # Prepare data for chart
            comparison_data = {}
            
            # Current month
            current_data = df[(df["BILLING_MONTH"] == current_month_date) & 
                             (df["SDIV_NAME"].isin(selected_discos))]
            if not current_data.empty:
                comparison_data[month1_label] = dict(zip(current_data["SDIV_NAME"], current_data[metric_col]))
            
            # Previous month
            prev_data = df[(df["BILLING_MONTH"] == previous_month_date) & 
                          (df["SDIV_NAME"].isin(selected_discos))]
            if not prev_data.empty:
                comparison_data[month2_label] = dict(zip(prev_data["SDIV_NAME"], prev_data[metric_col]))
            
            # Same month last year
            year_ago_data = df[(df["BILLING_MONTH"] == same_month_last_year) & 
                              (df["SDIV_NAME"].isin(selected_discos))]
            if not year_ago_data.empty:
                comparison_data[month3_label] = dict(zip(year_ago_data["SDIV_NAME"], year_ago_data[metric_col]))
            
            if comparison_data:
                # Create comparison chart
                fig = create_comparison_bar_chart(
                    comparison_data,
                    f"{compare_metric} - Three Period Comparison",
                    compare_metric + (" (%)" if "%" in compare_metric else ""),
                    is_percentage=("%" in compare_metric)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Month-over-Month Change Table
                st.markdown("### 📋 Month-over-Month Change Analysis")
                
                change_data = []
                for disco in selected_discos:
                    # Get values for each period
                    val1 = comparison_data.get(month1_label, {}).get(disco, np.nan)
                    val2 = comparison_data.get(month2_label, {}).get(disco, np.nan)
                    val3 = comparison_data.get(month3_label, {}).get(disco, np.nan)
                    
                    if not (pd.isna(val1) and pd.isna(val2) and pd.isna(val3)):
                        change_current = val1 - val2 if not (pd.isna(val1) or pd.isna(val2)) else np.nan
                        change_year = val1 - val3 if not (pd.isna(val1) or pd.isna(val3)) else np.nan
                        
                        change_data.append({
                            "DISCO": disco,
                            f"{month1_label}": f"{val1:.1f}" if not pd.isna(val1) else "N/A",
                            f"{month2_label}": f"{val2:.1f}" if not pd.isna(val2) else "N/A",
                            f"Δ Current vs Prev": f"{change_current:+.1f}" if not pd.isna(change_current) else "N/A",
                            f"{month3_label}": f"{val3:.1f}" if not pd.isna(val3) else "N/A",
                            f"Δ vs Year Ago": f"{change_year:+.1f}" if not pd.isna(change_year) else "N/A"
                        })
                
                if change_data:
                    change_df = pd.DataFrame(change_data)
                    st.dataframe(
                        change_df,
                        hide_index=True,
                        use_container_width=True,
                        height=300
                    )
        else:
            st.warning("⚠️ Not enough historical data for year-over-year comparison")
    else:
        st.warning("⚠️ Need at least 3 months of data for comparison analysis")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Individual DISCO Trend Analysis
    st.markdown('<div class="executive-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Individual DISCO Trend Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trend_disco = st.selectbox(
            "Select DISCO for Trend Analysis",
            selected_discos,
            key="trend_disco"
        )
    
    with col2:
        trend_months_count = st.selectbox(
            "Select Trend Period",
            ["Last 6 Months", "Last 12 Months", "All Available Months"],
            key="trend_period"
        )
    
    # Get trend data
    if trend_months_count == "Last 6 Months":
        trend_month_list = months[-6:] if len(months) >= 6 else months
    elif trend_months_count == "Last 12 Months":
        trend_month_list = months[-12:] if len(months) >= 12 else months
    else:
        trend_month_list = months
    
    trend_data = df[(df["MONTH"].isin(trend_month_list)) & 
                   (df["SDIV_NAME"] == trend_disco)].sort_values("BILLING_MONTH")
    
    if not trend_data.empty:
        fig = create_trend_chart(
            trend_data,
            trend_disco,
            f"{trend_months_count} Performance Trend"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate trends (only numeric columns)
        numeric_cols = trend_data.select_dtypes(include=[np.number]).columns.tolist()
        if len(trend_data) >= 2 and len(numeric_cols) > 0:
            latest = trend_data.iloc[-1]
            previous = trend_data.iloc[-2]
            
            # Calculate changes only for numeric columns that exist
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if "MON_PERC_LOSS_TD" in numeric_cols:
                    td_change = latest["MON_PERC_LOSS_TD"] - previous["MON_PERC_LOSS_TD"]
                    st.metric(
                        "T&D Loss Trend",
                        f"{latest['MON_PERC_LOSS_TD']:.1f}%",
                        delta=f"{td_change:+.1f}%",
                        delta_color="inverse"
                    )
            
            with col2:
                if "COLL_PERC" in numeric_cols:
                    coll_change = latest["COLL_PERC"] - previous["COLL_PERC"]
                    st.metric(
                        "Collection Trend",
                        f"{latest['COLL_PERC']:.1f}%",
                        delta=f"{coll_change:+.1f}%"
                    )
            
            with col3:
                if "MON_UNITS_NET_MET" in numeric_cols:
                    nm_change = latest["MON_UNITS_NET_MET"] - previous["MON_UNITS_NET_MET"]
                    st.metric(
                        "Net Metering Trend",
                        format_number(latest["MON_UNITS_NET_MET"]),
                        delta=format_number(nm_change, include_sign=True)
                    )
            
            with col4:
                if "MONTHLY_ENERGY" in numeric_cols:
                    energy_change = latest["MONTHLY_ENERGY"] - previous["MONTHLY_ENERGY"]
                    st.metric(
                        "Energy Trend",
                        format_number(latest["MONTHLY_ENERGY"]),
                        delta=format_number(energy_change, include_sign=True)
                    )
    else:
        st.info(f"📊 No trend data available for {trend_disco} in selected period")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ================= TAB 4: DEEP INSIGHTS =================
with tab4:
    st.markdown("### 🔍 DEEP INSIGHTS & ANALYTICS")
    
    # Time Series Analysis
    st.markdown('<div class="executive-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Time Series Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        insight_disco = st.selectbox(
            "Select DISCO for Insights",
            selected_discos,
            key="insight_disco"
        )
    
    with col2:
        insight_period = st.selectbox(
            "Select Analysis Period",
            ["Last 6 Months", "Last 12 Months", "All Available"],
            key="insight_period"
        )
    
    # Get time series data
    if insight_period == "Last 6 Months":
        insight_months = months[-6:] if len(months) >= 6 else months
    elif insight_period == "Last 12 Months":
        insight_months = months[-12:] if len(months) >= 12 else months
    else:
        insight_months = months
    
    time_series_data = df[(df["MONTH"].isin(insight_months)) & 
                         (df["SDIV_NAME"] == insight_disco)].sort_values("BILLING_MONTH")
    
    if not time_series_data.empty:
        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=[f"{insight_disco} - Performance Trends", "Monthly Metrics Overview"],
            vertical_spacing=0.2,
            row_heights=[0.6, 0.4]
        )
        
        # Add T&D Loss trend
        fig.add_trace(
            go.Scatter(
                x=time_series_data["MONTH"],
                y=time_series_data["MON_PERC_LOSS_TD"],
                mode='lines+markers',
                name='T&D Loss %',
                line=dict(color=COLORS["danger"], width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Add Collection % trend
        fig.add_trace(
            go.Scatter(
                x=time_series_data["MONTH"],
                y=time_series_data["COLL_PERC"],
                mode='lines+markers',
                name='Collection %',
                line=dict(color=COLORS["success"], width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Add Net Metering as bar chart in second subplot
        fig.add_trace(
            go.Bar(
                x=time_series_data["MONTH"],
                y=time_series_data["MON_UNITS_NET_MET"] / 1_000_000,
                name='Net Metering (M Units)',
                marker_color=COLORS["info"],
                hovertemplate="<b>Net Metering</b><br>Month: %{x}<br>Value: %{y:.2f}M<extra></extra>"
            ),
            row=2, col=1
        )
        
        # Add Units Billed as line in second subplot
        fig.add_trace(
            go.Scatter(
                x=time_series_data["MONTH"],
                y=time_series_data["MON_UNITS_BILLED"] / 1_000_000,
                mode='lines',
                name='Units Billed (M Units)',
                line=dict(color=COLORS["primary"], width=2),
                hovertemplate="<b>Units Billed</b><br>Month: %{x}<br>Value: %{y:.2f}M<extra></extra>"
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=700,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color=COLORS["dark"], size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=80, b=50, l=60, r=30)
        )
        
        fig.update_yaxes(title_text="Percentage (%)", row=1, col=1)
        fig.update_yaxes(title_text="Million Units", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance Summary
        st.markdown("### 📋 Performance Summary")
        
        if len(time_series_data) >= 2:
            # Get only numeric columns for averaging
            numeric_cols = time_series_data.select_dtypes(include=[np.number]).columns
            
            # Calculate 3-month average only for numeric columns
            if len(time_series_data) >= 3:
                avg_3m = time_series_data.tail(3)[numeric_cols].mean()
            else:
                avg_3m = time_series_data[numeric_cols].mean()
            
            latest = time_series_data.iloc[-1]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if "MON_PERC_LOSS_TD" in numeric_cols:
                    td_trend = "Improving" if latest["MON_PERC_LOSS_TD"] < avg_3m["MON_PERC_LOSS_TD"] else "Declining"
                    st.metric(
                        "T&D Loss Trend",
                        f"{latest['MON_PERC_LOSS_TD']:.1f}%",
                        delta=td_trend,
                        delta_color="inverse"
                    )
            
            with col2:
                if "COLL_PERC" in numeric_cols:
                    coll_trend = "Improving" if latest["COLL_PERC"] > avg_3m["COLL_PERC"] else "Declining"
                    st.metric(
                        "Collection Trend",
                        f"{latest['COLL_PERC']:.1f}%",
                        delta=coll_trend
                    )
            
            with col3:
                if "MONTHLY_ENERGY" in numeric_cols:
                    energy_growth = ((latest["MONTHLY_ENERGY"] - avg_3m["MONTHLY_ENERGY"]) / avg_3m["MONTHLY_ENERGY"]) * 100
                    st.metric(
                        "Energy Growth",
                        format_number(latest["MONTHLY_ENERGY"]),
                        delta=f"{energy_growth:+.1f}%"
                    )
            
            with col4:
                if "MON_UNITS_NET_MET" in numeric_cols:
                    nm_growth = ((latest["MON_UNITS_NET_MET"] - avg_3m["MON_UNITS_NET_MET"]) / avg_3m["MON_UNITS_NET_MET"]) * 100
                    st.metric(
                        "Net Metering Growth",
                        format_number(latest["MON_UNITS_NET_MET"]),
                        delta=f"{nm_growth:+.1f}%"
                    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Executive Summary
    st.markdown('<div class="executive-card">', unsafe_allow_html=True)
    st.markdown("### 📄 Executive Summary")
    
    # Calculate key insights using only numeric columns
    numeric_analysis_df = analysis_df.select_dtypes(include=[np.number])
    
    if "MON_PERC_LOSS_TD" in numeric_analysis_df.columns:
        compliant_discos = analysis_df[analysis_df["MON_PERC_LOSS_TD"] <= NEPRA_LOSS_LIMIT]
        non_compliant_discos = analysis_df[analysis_df["MON_PERC_LOSS_TD"] > NEPRA_LOSS_LIMIT]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Key Achievements")
            st.markdown(f"""
            - **{len(compliant_discos)}/{len(analysis_df)} DISCOs** compliant with NEPRA loss limits
            - **{format_number(analysis_df['MON_UNITS_NET_MET'].sum())}** total net metering units
            - **{analysis_df['COLL_PERC'].mean():.1f}%** average collection rate
            - **{format_number(analysis_df['MON_UNITS_BILLED'].sum())}** total units billed
            """)
        
        with col2:
            st.markdown("#### ⚠️ Areas for Improvement")
            if len(non_compliant_discos) > 0:
                non_compliant_list = ", ".join(non_compliant_discos["SDIV_NAME"].tolist()[:3])
                if len(non_compliant_discos) > 3:
                    non_compliant_list += f" and {len(non_compliant_discos)-3} more"
                
                st.markdown(f"""
                - **{len(non_compliant_discos)} DISCOs** exceed NEPRA loss limits
                - **{non_compliant_discos['MON_PERC_LOSS_TD'].mean():.1f}%** average loss in non-compliant DISCOs
                - **{format_number(analysis_df['MON_UNITS_LOST'].sum())}** total units lost
                - **Lowest collection**: {analysis_df['COLL_PERC'].min():.1f}%
                """)
            else:
                st.markdown("""
                - ✅ All DISCOs compliant with NEPRA standards
                - ⚡ Excellent performance across all metrics
                - 📈 Continue monitoring for sustained performance
                """)
    else:
        st.info("📊 Performance metrics analysis requires numeric data")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ================= EXECUTIVE FOOTER =================
st.markdown("---")
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {COLORS["primary"]}, {COLORS["dark"]});
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    margin-top: 30px;
    border: 1px solid rgba(253, 140, 23, 0.3);
">
    <div style="font-weight: 800; margin-bottom: 10px; font-size: 16px;">
        NATIONAL POWER SECTOR EXECUTIVE DASHBOARD
    </div>
    <div style="font-size: 14px; margin-bottom: 15px; opacity: 0.9;">
        ⚡ Real-time Performance Monitoring | 📊 NEPRA Compliance | 🎯 Executive Decision Support
    </div>
    <div style="font-size: 12px; opacity: 0.7;">
        📅 Last Updated: {pd.Timestamp.now().strftime("%d %b %Y %H:%M")} | 📊 Data Source: DISCO Performance Reports
    </div>
</div>
""", unsafe_allow_html=True)
