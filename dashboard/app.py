"""
Global Conflict Impact Analyzer - Dashboard
Fixed & Upgraded Version
Run: streamlit run app.py
"""

import os
import time
import pathlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

# Load .env from project root — works from any directory
_env_path = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

# ═══════════════════════════════════════════════════════
#  PAGE CONFIG  (must be first Streamlit call)
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="Global Conflict Impact Analyzer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════
#  STYLES
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
body, .stApp { background-color: #060e1a; color: #c8d8f0; }
h1, h2, h3, h4 { color: #e8f4ff; }
[data-testid="metric-container"] {
    background: #0d1929; border: 1px solid #1a2f50;
    border-radius: 10px; padding: 14px 18px;
}
[data-testid="stMetricValue"]  { color: #60a5fa; font-size: 26px !important; font-weight: 800; }
[data-testid="stMetricDelta"]  { font-size: 13px; }
.news-box {
    background: linear-gradient(90deg, #ff3b3b22, #ff3b3b11);
    border: 1px solid #ff3b3b44; border-radius: 8px;
    padding: 10px 18px; margin-bottom: 12px;
    color: #ffcccc; font-size: 13px;
}
.tag {
    display: inline-block; padding: 5px 14px; border-radius: 20px;
    color: white; font-weight: 700; font-size: 12px;
    margin-right: 8px; margin-bottom: 6px;
}
.tag-red    { background: #ff3b3b44; border: 1px solid #ff3b3b; color: #ff8080; }
.tag-orange { background: #ffaa0044; border: 1px solid #ffaa00; color: #ffcc60; }
.tag-green  { background: #00e5a044; border: 1px solid #00e5a0; color: #00e5a0; }
.alert-high { background:#2a0a0a; border:1px solid #ff3b3b66; border-radius:8px; padding:10px 14px; margin-bottom:8px; }
.alert-med  { background:#2a1a00; border:1px solid #ffaa0066; border-radius:8px; padding:10px 14px; margin-bottom:8px; }
.alert-low  { background:#0a1a10; border:1px solid #00e5a066; border-radius:8px; padding:10px 14px; margin-bottom:8px; }
.stProgress > div > div { background-color: #1a2f50; }
.pulse {
    height: 12px; width: 12px; background: #2ECC40; border-radius: 50%;
    display: inline-block; box-shadow: 0 0 8px #2ECC40; animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%   { transform: scale(0.8); opacity: 0.7; }
    50%  { transform: scale(1.2); opacity: 1;   }
    100% { transform: scale(0.8); opacity: 0.7; }
}
.stTabs [data-baseweb="tab-list"]  { background: #0d1929; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"]       { color: #4a6080; font-weight: 600; }
.stTabs [aria-selected="true"]     { background: #1a3a6e !important; color: #60a5fa !important; border-radius: 8px; }
[data-testid="stSidebar"] { background: #0a1220; border-right: 1px solid #1a2f50; }
hr { border-color: #1a2f50; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  CONFLICT DATA
# ═══════════════════════════════════════════════════════
CONFLICTS = [
    {"name": "Middle East Tensions",     "region": "Middle East",  "severity": "HIGH",   "started": "Oct 2024", "sectors": ["Oil", "Shipping", "Markets"]},
    {"name": "Eastern Europe Sanctions", "region": "Europe",       "severity": "MEDIUM", "started": "Feb 2022", "sectors": ["Energy", "Tech", "Markets"]},
    {"name": "South Asia Dispute",       "region": "Asia",         "severity": "LOW",    "started": "Jan 2025", "sectors": ["Tech", "Shipping"]},
    {"name": "Taiwan Strait Tensions",   "region": "Asia-Pacific", "severity": "HIGH",   "started": "Aug 2024", "sectors": ["Tech", "Shipping", "Markets"]},
]

SEVERITY_COLOR = {"HIGH": "tag-red", "MEDIUM": "tag-orange", "LOW": "tag-green"}
RISK_COLOR     = {"HIGH": "#ff3b3b", "MEDIUM": "#ffaa00",    "LOW": "#00e5a0"}

SHIPPING_DATA = pd.DataFrame({
    "Route":          ["Strait of Hormuz", "Suez Canal", "Taiwan Strait", "Black Sea", "South China Sea"],
    "Disruption (%)": [85, 70, 65, 45, 55],
    "Delay (days)":   [7,  5,  4,  3,  4],
    "Status":         ["CRITICAL", "HIGH", "HIGH", "MODERATE", "MODERATE"],
})

SUPPLY_DATA = pd.DataFrame({
    "Component":    ["TSMC Chips", "Rare Earth Metals", "Crude Oil", "Wheat/Grain", "Lithium", "Copper"],
    "Shortage (%)": [72,           58,                  80,          45,            62,        38],
    "Risk":         ["CRITICAL",   "HIGH",              "CRITICAL",  "MODERATE",    "HIGH",    "LOW"],
})

SECTOR_VOLATILITY = pd.DataFrame({
    "Sector":     ["Energy", "Tech", "Defense", "Finance", "Consumer", "Healthcare"],
    "Volatility": [82,       65,     28,        54,        38,         22],
    "Beta":       [1.42,     1.18,   0.71,      0.95,      0.82,       0.58],
})

# ── Curated conflict-only news (no entertainment/music) ──
FALLBACK_NEWS = [
    "OPEC+ emergency summit called as Middle East tensions escalate",
    "US deploys naval fleet to Strait of Hormuz amid conflict fears",
    "Brent crude surges 8% on geopolitical supply disruption threat",
    "G7 nations agree on coordinated sanctions against aggressor states",
    "Red Sea shipping routes face critical disruption — 34% rate surge",
    "IMF warns conflict spread could cut global GDP by 0.5%",
    "Taiwan Strait military exercises trigger chip supply chain fears",
    "NATO emergency session called over Eastern Europe border violations",
    "Russia-Ukraine ceasefire talks resume in Geneva with mediators",
    "TSMC warns of 6-week semiconductor delivery delays due to tensions",
    "UN Security Council emergency session on Middle East escalation",
    "Energy stocks rally as oil prices breach $90 per barrel",
    "European gas storage falls below 40% amid supply disruptions",
    "China military drills near Taiwan cause shipping rerouting",
    "Saudi Arabia increases oil output to stabilize global markets",
    "Black Sea grain corridor threatened by renewed hostilities",
    "Pentagon confirms additional carrier group deployment to Gulf region",
    "Semiconductor shortage worsens as Taiwan tensions remain elevated",
    "Global defense spending hits record high amid conflict uncertainty",
    "Oil tanker insurance premiums spike 40% on route disruption fears",
]

# Keywords that identify a headline as conflict-related
CONFLICT_KEYWORDS = [
    "oil", "conflict", "war", "sanction", "military", "nato",
    "crude", "opec", "shipping", "geopolit", "iran", "russia",
    "china", "taiwan", "middle east", "ukraine", "nuclear",
    "missile", "ceasefire", "troops", "tanker", "energy",
    "supply chain", "semiconductor", "chip", "brent", "wti",
    "escalat", "tension", "attack", "strike", "defense",
    "pentagon", "un security", "g7", "imf", "sanction",
]

# ═══════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(PROJECT_DIR, "data")

PLOTLY_THEME  = dict(template="plotly_dark")
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0d1929",
    plot_bgcolor="#060e1a",
    font=dict(color="#8aa0c0", size=11),
)

def risk_bar_color(pct):
    if pct >= 70: return "#ff3b3b"
    if pct >= 45: return "#ffaa00"
    return "#00e5a0"


def filter_conflict_news(titles):
    """Return only headlines containing at least one conflict keyword."""
    filtered = [
        t for t in titles
        if any(kw in t.lower() for kw in CONFLICT_KEYWORDS)
    ]
    return filtered if len(filtered) >= 3 else []


def load_csv(filename, label):
    """Auto-detects yfinance 2-row header vs clean single header."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        st.error(f"❌ `{filename}` not found in `data/`. Run `scripts/data_collection.py` first.")
        return None
    try:
        peek        = pd.read_csv(path, nrows=2, header=None)
        first_cell  = str(peek.iloc[0, 0]).strip()
        second_cell = str(peek.iloc[1, 0]).strip()

        is_two_row = (
            first_cell == "Price" or
            second_cell.lower() in ("ticker", "cl=f", "^gspc", "soxx", "nvda", "date")
        )

        if is_two_row:
            df = pd.read_csv(path, header=[0, 1], index_col=0)
            df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            df.rename(columns={df.columns[0]: "Date"}, inplace=True)
        else:
            df = pd.read_csv(path)
            if df.columns[0] != "Date":
                df.rename(columns={df.columns[0]: "Date"}, inplace=True)
        return df
    except Exception as e:
        st.error(f"❌ Error reading `{filename}`: {e}")
        return None


def clean_market_data(df):
    """Handles yfinance 2-row header and clean single-header CSVs."""
    first_col = str(df.columns[0]).strip()
    first_val = str(df.iloc[0, 0]).strip() if len(df) > 0 else ""

    if first_col == "Price" or first_val.lower() in ("ticker", "cl=f", "^gspc", "soxx", "nvda"):
        df = df.iloc[1:].reset_index(drop=True)

    if df.columns[0] != "Date":
        df.rename(columns={df.columns[0]: "Date"}, inplace=True)

    df = df[df["Date"].astype(str).str.strip() != "Date"]
    df["Date"]  = pd.to_datetime(df["Date"], dayfirst=False, errors="coerce")
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df.dropna(subset=["Date", "Close"])
    return df.sort_values("Date").reset_index(drop=True)


def compute_risk_score(oil_chg, sp_chg, chip_chg, news_count=0):
    """Weighted risk score 0–100."""
    score = 0
    if   oil_chg > 10: score += 35
    elif oil_chg > 5:  score += 25
    elif oil_chg > 2:  score += 15
    elif oil_chg > 0:  score += 5
    if   sp_chg < -5:  score += 30
    elif sp_chg < -2:  score += 20
    elif sp_chg < 0:   score += 10
    if   chip_chg < -5: score += 25
    elif chip_chg < -3: score += 18
    elif chip_chg < -1: score += 10
    elif chip_chg < 0:  score += 4
    if   news_count > 15: score += 10
    elif news_count > 8:  score += 6
    elif news_count > 3:  score += 3
    return min(score, 100)


def risk_label(score):
    if score >= 65: return "HIGH",     "#ff3b3b"
    if score >= 35: return "MODERATE", "#ffaa00"
    return                 "LOW",      "#00e5a0"


# ═══════════════════════════════════════════════════════
#  LOAD & CLEAN DATA
# ═══════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def load_all_data():
    oil_raw  = load_csv("oil_prices.csv",    "Oil Prices")
    sp_raw   = load_csv("sp500_data.csv",    "S&P 500")
    chip_raw = load_csv("chip_data.csv",     "Chips")
    news_raw = load_csv("conflict_news.csv", "News")

    oil  = clean_market_data(oil_raw)  if oil_raw  is not None else None
    sp   = clean_market_data(sp_raw)   if sp_raw   is not None else None
    chip = clean_market_data(chip_raw) if chip_raw is not None else None

    if news_raw is not None:
        if "title" not in news_raw.columns:
            news_raw.rename(columns={news_raw.columns[0]: "title"}, inplace=True)
        news = news_raw
    else:
        news = pd.DataFrame({"title": FALLBACK_NEWS})

    return oil, sp, chip, news

oil_df, sp_df, chip_df, news_df = load_all_data()

def safe_change(df):
    if df is None or len(df) < 2: return 0.0
    return round(float(df["Close"].iloc[-1]) - float(df["Close"].iloc[0]), 2)

oil_change  = safe_change(oil_df)
sp_change   = safe_change(sp_df)
chip_change = safe_change(chip_df)

risk_score        = compute_risk_score(oil_change, sp_change, chip_change, len(news_df))
r_label, r_color  = risk_label(risk_score)
current_oil_price = round(float(oil_df["Close"].iloc[-1]), 2) if oil_df is not None else 0.0

# ═══════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    st.markdown("---")
    conflict_names    = [c["name"] for c in CONFLICTS]
    selected_conflict = st.selectbox("🎯 Focus Conflict", ["All"] + conflict_names)
    days_back         = st.slider("📅 Data Window (days)", min_value=7, max_value=90, value=30, step=7)
    st.markdown("---")
    st.markdown("### 🔔 Alert Threshold")
    oil_threshold = st.number_input("Oil change alert ($)", value=35.0, step=0.5)
    vix_threshold = st.number_input("Volatility alert (VIX)", value=25.0, step=1.0)
    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.markdown(
        f"<small style='color:#3a5a80'>Last updated:<br>{time.strftime('%Y-%m-%d %H:%M:%S')}</small>",
        unsafe_allow_html=True
    )

def tail_days(df, n):
    if df is None: return None
    cutoff   = pd.Timestamp.now() - pd.Timedelta(days=n)
    filtered = df[df["Date"] >= cutoff]
    return filtered if len(filtered) > 2 else df.tail(n)

oil_view  = tail_days(oil_df,  days_back)
sp_view   = tail_days(sp_df,   days_back)
chip_view = tail_days(chip_df, days_back)

# ═══════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════
header_col, pulse_col = st.columns([10, 1])
with header_col:
    st.markdown("# 🔴 GLOBAL CONFLICT IMPACT ANALYZER")
    st.markdown("**GEOPOLITICAL RISK INTELLIGENCE SYSTEM v3.0 • LIVE**")
with pulse_col:
    st.markdown("<br><span class='pulse'></span>", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("🛢 BRENT CRUDE ($)",  f"{current_oil_price:.2f}", f"{oil_change:+.2f}")
m2.metric("📊 RISK INDEX",        f"{risk_score}/100",        r_label)
m3.metric("⚔️ ACTIVE CONFLICTS",  str(len(CONFLICTS)),         "+1 this week")
m4.metric("🚢 ROUTES DISRUPTED",  "3 / 5",                    "↑ from last week")

if abs(oil_change) >= oil_threshold:
    st.error(f"⚠️ ALERT: Oil price moved {oil_change:+.2f} — exceeds your ${oil_threshold} threshold!")

st.markdown("---")

# ── Live news ticker — conflict news only ──
if "news_idx" not in st.session_state:
    st.session_state.news_idx = 0

raw_titles      = news_df["title"].dropna().tolist()
conflict_titles = filter_conflict_news(raw_titles)
headlines       = conflict_titles if len(conflict_titles) >= 3 else FALLBACK_NEWS

current_headline = headlines[st.session_state.news_idx % len(headlines)]
st.markdown(
    f"<div class='news-box'>📢 LIVE FEED &nbsp;|&nbsp; {current_headline}</div>",
    unsafe_allow_html=True
)

col_prev, col_next, _ = st.columns([1, 1, 10])
if col_prev.button("◀ Prev"):
    st.session_state.news_idx = max(0, st.session_state.news_idx - 1)
if col_next.button("Next ▶"):
    st.session_state.news_idx += 1

tags_html = "".join([
    f"<span class='tag {SEVERITY_COLOR[c['severity']]}'>{c['name']}</span>"
    for c in CONFLICTS
    if selected_conflict == "All" or c["name"] == selected_conflict
])
st.markdown(f"<div style='margin-bottom:16px'>{tags_html}</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌐 Overview", "🛢 Oil Market", "📈 Stock Markets", "🚢 Supply Chain", "🧠 AI Analysis"
])

# ── TAB 1 — OVERVIEW ────────────────────────────────────
with tab1:
    st.subheader("📌 Conflict Impact Chain")
    chain_cols = st.columns(9)
    chain = [
        ("⚔️", "Conflict",      "#ff3b3b"),
        ("→",  "",              "#3a5a80"),
        ("🛢", "Oil Spike",     "#ffaa00"),
        ("→",  "",              "#3a5a80"),
        ("📉", "Markets Drop",  "#ff6b6b"),
        ("→",  "",              "#3a5a80"),
        ("🚢", "Route Delays",  "#60a5fa"),
        ("→",  "",              "#3a5a80"),
        ("💻", "Chip Shortage", "#a78bfa"),
    ]
    for col, (icon, label, color) in zip(chain_cols, chain):
        if label:
            col.markdown(
                f"<div style='text-align:center;background:{color}22;"
                f"border:1px solid {color}55;border-radius:10px;padding:10px 4px'>"
                f"<div style='font-size:22px'>{icon}</div>"
                f"<div style='font-size:10px;color:{color};font-weight:700'>{label}</div></div>",
                unsafe_allow_html=True
            )
        else:
            col.markdown(
                f"<div style='text-align:center;padding-top:18px;font-size:20px;color:{color}'>→</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.subheader("📊 30-Day Market Snapshot")
    c1, c2, c3 = st.columns(3)
    if oil_view is not None:
        with c1:
            fig = px.area(oil_view, x="Date", y="Close", title="Brent Crude ($)",
                          color_discrete_sequence=["#ffaa00"], **PLOTLY_THEME)
            fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
    if sp_view is not None:
        with c2:
            fig = px.line(sp_view, x="Date", y="Close", title="S&P 500",
                          color_discrete_sequence=["#00e5a0"], **PLOTLY_THEME)
            fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
    if chip_view is not None:
        with c3:
            fig = px.line(chip_view, x="Date", y="Close", title="Semiconductor Index",
                          color_discrete_sequence=["#a78bfa"], **PLOTLY_THEME)
            fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, margin=dict(t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🗂 Active Conflict Profiles")
    display_conflicts = [c for c in CONFLICTS if selected_conflict == "All" or c["name"] == selected_conflict]
    for c in display_conflicts:
        with st.expander(f"{c['name']} — {c['severity']} RISK"):
            cols = st.columns(4)
            cols[0].markdown(f"**Region:** {c['region']}")
            cols[1].markdown(f"**Since:** {c['started']}")
            sev = c['severity']
            cols[2].markdown(
                f"**Severity:** <span style='color:{RISK_COLOR[sev]};font-weight:800'>{sev}</span>",
                unsafe_allow_html=True
            )
            cols[3].markdown(f"**Sectors:** {', '.join(c['sectors'])}")

# ── TAB 2 — OIL MARKET ──────────────────────────────────
with tab2:
    st.subheader("🛢 Oil Market Analysis")
    if oil_view is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=oil_view["Date"], y=oil_view["Close"],
            name="Brent Crude", fill="tozeroy",
            line=dict(color="#ffaa00", width=2),
            fillcolor="rgba(255,170,0,0.12)"
        ))
        if "Volume" in oil_view.columns:
            fig.add_trace(go.Bar(
                x=oil_view["Date"], y=oil_view["Volume"],
                name="Volume", yaxis="y2",
                marker_color="rgba(96,165,250,0.25)"
            ))
            fig.update_layout(**PLOTLY_LAYOUT, yaxis2=dict(overlaying="y", side="right", showgrid=False))
        fig.update_layout(
            **PLOTLY_LAYOUT,
            title="Brent Crude — Price Trend",
            margin=dict(t=50, b=30),
            xaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Load oil_prices.csv to see price chart.")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📋 Supply Risk Factors")
        risks = [
            ("OPEC Production Cut Risk",       72),
            ("Pipeline Infrastructure Threat",  58),
            ("Tanker Route Disruption",          85),
            ("Refinery Capacity Loss",           41),
            ("Strategic Reserve Depletion",      33),
        ]
        for label, pct in risks:
            color = risk_bar_color(pct)
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px'>"
                f"<span style='color:#8aa0c0'>{label}</span>"
                f"<span style='color:{color};font-weight:700'>{pct}%</span></div>",
                unsafe_allow_html=True
            )
            st.progress(pct / 100)

    with col_b:
        st.markdown("### ⚠️ Price Alerts")
        alerts = [
            ("HIGH",   "Brent surpasses $90 threshold",         "2h ago"),
            ("HIGH",   "OPEC emergency meeting called",          "5h ago"),
            ("MEDIUM", "Tanker insurance premiums +23%",         "1d ago"),
            ("LOW",    "Strategic reserves drawdown announced",  "2d ago"),
            ("MEDIUM", "Libya output falls 15% on civil unrest", "3d ago"),
        ]
        for level, msg, t in alerts:
            css   = {"HIGH": "alert-high", "MEDIUM": "alert-med", "LOW": "alert-low"}[level]
            color = RISK_COLOR[level]
            st.markdown(
                f"<div class='{css}'>"
                f"<span style='color:{color};font-weight:800;font-size:11px'>{level}</span>"
                f"&nbsp;&nbsp;<span style='color:#c8d8f0;font-size:13px'>{msg}</span>"
                f"<span style='color:#3a5a80;font-size:11px;float:right'>{t}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

# ── TAB 3 — STOCK MARKETS ───────────────────────────────
with tab3:
    st.subheader("📈 Stock Market Performance")
    if sp_view is not None and chip_view is not None:
        fig = go.Figure()
        def normalise(df):
            s = df["Close"].copy()
            return (s / s.iloc[0]) * 100
        fig.add_trace(go.Scatter(x=sp_view["Date"],   y=normalise(sp_view),   name="S&P 500",      line=dict(color="#00e5a0", width=2)))
        fig.add_trace(go.Scatter(x=chip_view["Date"], y=normalise(chip_view), name="Chips (SOX)",  line=dict(color="#a78bfa", width=2)))
        if oil_view is not None:
            fig.add_trace(go.Scatter(x=oil_view["Date"], y=normalise(oil_view), name="Energy (Oil)", line=dict(color="#ffaa00", width=2)))
        fig.update_layout(
            **PLOTLY_LAYOUT,
            title="Normalised Performance (Base = 100)",
            margin=dict(t=50, b=30),
            yaxis_title="Index (rebased)",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🏭 Sector Volatility")
        fig = px.bar(
            SECTOR_VOLATILITY, x="Sector", y="Volatility",
            color="Volatility",
            color_continuous_scale=["#00e5a0", "#ffaa00", "#ff3b3b"],
            title="Volatility Index by Sector", **PLOTLY_THEME,
        )
        fig.update_layout(**PLOTLY_LAYOUT, margin=dict(t=50, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("### 📐 Beta Exposure")
        fig = px.scatter(
            SECTOR_VOLATILITY, x="Beta", y="Volatility",
            text="Sector", size="Volatility", color="Volatility",
            color_continuous_scale=["#00e5a0", "#ffaa00", "#ff3b3b"],
            title="Risk vs. Market Sensitivity", **PLOTLY_THEME,
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(**PLOTLY_LAYOUT, margin=dict(t=50, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Index Changes")
    idx_data = {
        "Index":      ["S&P 500", "Brent Crude", "Semiconductor", "VIX"],
        "Current":    [
            f"{sp_df['Close'].iloc[-1]:.0f}"   if sp_df   is not None else "N/A",
            f"${current_oil_price:.2f}",
            f"{chip_df['Close'].iloc[-1]:.0f}" if chip_df is not None else "N/A",
            "28.4",
        ],
        "30d Change": [f"{sp_change:+.2f}", f"{oil_change:+.2f}", f"{chip_change:+.2f}", "+4.1"],
        "Risk":       ["MODERATE", "HIGH", "HIGH", "ELEVATED"],
    }
    st.dataframe(pd.DataFrame(idx_data), use_container_width=True, hide_index=True)

# ── TAB 4 — SUPPLY CHAIN ────────────────────────────────
with tab4:
    st.subheader("🚢 Global Supply Chain Disruptions")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 🗺 Shipping Route Status")
        fig = px.bar(
            SHIPPING_DATA, x="Disruption (%)", y="Route",
            orientation="h", color="Disruption (%)",
            color_continuous_scale=["#00e5a0", "#ffaa00", "#ff3b3b"],
            title="Route Disruption Level",
            hover_data=["Delay (days)", "Status"], **PLOTLY_THEME,
        )
        fig.update_layout(**PLOTLY_LAYOUT, margin=dict(t=50, b=20), coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
        for _, row in SHIPPING_DATA.iterrows():
            color = risk_bar_color(row["Disruption (%)"])
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;font-size:12px;margin-bottom:8px'>"
                f"<span style='color:#c8d8f0'>🚢 {row['Route']}</span>"
                f"<span style='color:#3a5a80'>+{row['Delay (days)']}d delay</span>"
                f"<span style='color:{color};font-weight:700'>{row['Disruption (%)']}% disrupted</span>"
                f"</div>",
                unsafe_allow_html=True
            )
            st.progress(row["Disruption (%)"] / 100)

    with col_b:
        st.markdown("### 🔩 Component Shortage Index")
        fig = px.bar(
            SUPPLY_DATA, x="Shortage (%)", y="Component",
            orientation="h", color="Shortage (%)",
            color_continuous_scale=["#00e5a0", "#ffaa00", "#ff3b3b"],
            title="Critical Component Shortages", **PLOTLY_THEME,
        )
        fig.update_layout(**PLOTLY_LAYOUT, margin=dict(t=50, b=20), coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
        for _, row in SUPPLY_DATA.iterrows():
            color = {"CRITICAL": "#ff3b3b", "HIGH": "#ffaa00", "MODERATE": "#60a5fa", "LOW": "#00e5a0"}[row["Risk"]]
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"background:#0d1929;border:1px solid {color}33;border-radius:8px;padding:8px 12px;margin-bottom:6px'>"
                f"<span style='color:#c8d8f0;font-size:13px'>{row['Component']}</span>"
                f"<span style='color:{color};font-weight:800;font-size:15px'>{row['Shortage (%)']}%</span>"
                f"<span style='color:{color};font-size:11px;font-weight:700'>{row['Risk']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

# ── TAB 5 — AI ANALYSIS ─────────────────────────────────
with tab5:
    st.subheader("🧠 AI-Powered Geopolitical Intelligence")

    focus      = selected_conflict if selected_conflict != "All" else CONFLICTS[0]["name"]
    focus_data = next((c for c in CONFLICTS if c["name"] == focus), CONFLICTS[0])
    fd_sev = focus_data['severity']
    st.markdown(
        f"Analysing: <span style='color:#60a5fa;font-weight:700'>{focus_data['name']}</span> "
        f"— Severity: <span style='color:{RISK_COLOR[fd_sev]};font-weight:700'>{fd_sev}</span>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    if "ai_result"   not in st.session_state: st.session_state.ai_result   = None
    if "ai_conflict" not in st.session_state: st.session_state.ai_conflict = ""

    def run_ai_analysis():
        """Call Google Gemini API and store result in session state."""
        try:
            from google import genai as google_genai
            import json

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                st.error("❌ GEMINI_API_KEY not found. Add it to your .env file.")
                return

            client = google_genai.Client(api_key=api_key)
            prompt = f"""You are a senior geopolitical risk analyst. Provide a structured intelligence briefing.

Conflict:         {focus_data['name']}
Region:           {focus_data['region']}
Severity:         {focus_data['severity']}
Affected Sectors: {', '.join(focus_data['sectors'])}
Oil price change (30d): ${oil_change:+.2f}
S&P 500 change   (30d): {sp_change:+.2f}
Chip index change (30d): {chip_change:+.2f}
Overall risk score: {risk_score}/100

Return ONLY a JSON object. No markdown, no backticks, no extra text. Just raw JSON:
{{
  "executive_summary": "3-sentence overview of the conflict and its global economic impact",
  "risk_score": <integer 0-100>,
  "oil_impact": "1-sentence assessment of oil market impact",
  "market_impact": "1-sentence assessment of stock market impact",
  "shipping_impact": "1-sentence assessment of shipping route impact",
  "tech_impact": "1-sentence assessment of tech supply chain impact",
  "30_day_forecast": "1 sentence forecast for next 30 days",
  "recommendation": "1 actionable risk mitigation sentence",
  "alerts": ["alert 1 under 10 words", "alert 2 under 10 words", "alert 3 under 10 words"]
}}"""

            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=prompt,
            )
            raw = response.text.strip().replace("```json", "").replace("```", "").strip()
            st.session_state.ai_result   = json.loads(raw)
            st.session_state.ai_conflict = focus_data["name"]

        except ImportError:
            st.error("❌ Install Google Generative AI SDK: `pip install google-genai`")
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                st.error("⏳ Rate limit hit. Please wait 1 minute and try again.")
                st.info("💡 Free tier has limited calls per minute.")
            else:
                st.error(f"❌ AI analysis failed: {e}")
                st.info("💡 Check your GEMINI_API_KEY in the .env file.")

    col_btn, _ = st.columns([2, 8])
    with col_btn:
        if st.button("🔄 Run AI Analysis", type="primary"):
            with st.spinner("🤖 Gemini AI is analysing geopolitical data... please wait"):
                run_ai_analysis()

    if st.session_state.ai_conflict != focus_data["name"]:
        st.session_state.ai_result = None

    result = st.session_state.ai_result

    if result is None:
        st.info("👆 Click **Run AI Analysis** to generate a live Gemini AI-powered intelligence report.")
    else:
        st.markdown("### 📋 Executive Intelligence Summary")
        st.markdown(
            f"<div style='background:#0d1929;border:1px solid #1a3060;border-radius:12px;"
            f"padding:18px;font-size:14px;color:#c8d8f0;line-height:1.8'>"
            f"{result.get('executive_summary', '')}</div>",
            unsafe_allow_html=True
        )

        ai_score           = result.get("risk_score", risk_score)
        ai_label, ai_color = risk_label(ai_score)
        st.markdown("---")

        gauge_col, metrics_col = st.columns([1, 2])
        with gauge_col:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ai_score,
                title={"text": "AI Risk Score", "font": {"color": "#c8d8f0", "size": 14}},
                gauge={
                    "axis":  {"range": [0, 100], "tickcolor": "#3a5a80"},
                    "bar":   {"color": ai_color},
                    "bgcolor": "#0d1929",
                    "steps": [
                        {"range": [0,  35], "color": "#0a1a10"},
                        {"range": [35, 65], "color": "#2a1a00"},
                        {"range": [65, 100],"color": "#2a0a0a"},
                    ],
                    "threshold": {
                        "line":      {"color": "white", "width": 3},
                        "thickness": 0.75,
                        "value":     ai_score,
                    }
                }
            ))
            fig_gauge.update_layout(
                **PLOTLY_LAYOUT,
                height=220,
                margin=dict(t=40, b=10, l=20, r=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with metrics_col:
            g1, g2, g3 = st.columns(3)
            g1.metric("AI Risk Score",     f"{ai_score}/100",  ai_label)
            g2.metric("System Score",      f"{risk_score}/100", r_label)
            g3.metric("Conflict Severity",  focus_data["severity"])

        st.markdown("### 🎯 Sector Impact Assessment")
        s1, s2 = st.columns(2)
        impacts = [
            ("🛢 Oil Market",       "oil_impact",      "#ffaa00", s1),
            ("📈 Stock Markets",    "market_impact",   "#00e5a0", s2),
            ("🚢 Shipping Routes",  "shipping_impact", "#60a5fa", s1),
            ("💻 Tech / Chips",     "tech_impact",     "#a78bfa", s2),
        ]
        for title, key, color, col in impacts:
            col.markdown(
                f"<div style='background:#0d1929;border:1px solid {color}44;border-radius:10px;"
                f"padding:14px;margin-bottom:12px'>"
                f"<div style='color:{color};font-size:11px;font-weight:700;letter-spacing:2px;margin-bottom:6px'>{title.upper()}</div>"
                f"<div style='color:#8aa0c0;font-size:13px;line-height:1.6'>{result.get(key, '')}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown("### 🚨 AI-Generated Alerts")
        for alert in result.get("alerts", []):
            st.markdown(
                f"<div class='alert-high'><span style='color:#ff3b3b'>⚠ </span>"
                f"<span style='color:#c8d8f0;font-size:13px'>{alert}</span></div>",
                unsafe_allow_html=True
            )

        f1, f2 = st.columns(2)
        with f1:
            st.markdown("### 📅 30-Day Forecast")
            st.markdown(
                f"<div style='background:#0d1929;border:1px solid #00e5a044;border-radius:10px;"
                f"padding:14px;color:#8aa0c0;font-size:13px;line-height:1.7'>"
                f"{result.get('30_day_forecast', '')}</div>",
                unsafe_allow_html=True
            )
        with f2:
            st.markdown("### 🛡 Risk Mitigation")
            st.markdown(
                f"<div style='background:#0d1929;border:1px solid #6366f144;border-radius:10px;"
                f"padding:14px;color:#8aa0c0;font-size:13px;line-height:1.7'>"
                f"{result.get('recommendation', '')}</div>",
                unsafe_allow_html=True
            )

# ═══════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#3a5a80;font-size:12px;padding:10px'>"
    f"Global Conflict Impact Analyzer v3.0 &nbsp;•&nbsp; "
    f"Data refreshes every 5 minutes &nbsp;•&nbsp; "
    f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
    f"</div>",
    unsafe_allow_html=True
)