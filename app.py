"""
MPSIF Earnings Calendar
A Streamlit app for tracking earnings dates across fund holdings.
"""

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, date
import calendar
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MPSIF Earnings Calendar",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    section[data-testid="stSidebar"] .stMarkdown h2 {
        color: #58a6ff;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    /* Main header */
    .main-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.8rem;
        font-weight: 600;
        color: #58a6ff;
        letter-spacing: -0.02em;
        margin-bottom: 0;
    }
    .main-subheader {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.95rem;
        color: #8b949e;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }

    /* Metric cards */
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        text-align: center;
    }
    .metric-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.8rem;
        font-weight: 600;
        color: #58a6ff;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Earnings row badge */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
    }
    .badge-soon {
        background: #1f3a1f;
        color: #3fb950;
        border: 1px solid #3fb950;
    }
    .badge-upcoming {
        background: #1f2d3f;
        color: #58a6ff;
        border: 1px solid #58a6ff;
    }
    .badge-past {
        background: #1e1e1e;
        color: #8b949e;
        border: 1px solid #30363d;
    }
    .badge-bmc {
        background: #2d1f0e;
        color: #d29922;
        border: 1px solid #d29922;
    }

    /* Calendar cell */
    .cal-cell {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 0.4rem;
        min-height: 80px;
        vertical-align: top;
    }
    .cal-cell-today {
        border-color: #58a6ff;
        background: #0d2044;
    }
    .cal-day-num {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        color: #8b949e;
        margin-bottom: 4px;
    }
    .cal-day-num-today {
        color: #58a6ff;
        font-weight: 700;
    }
    .cal-event {
        background: #1f3a1f;
        color: #3fb950;
        border-radius: 3px;
        padding: 1px 4px;
        font-size: 0.7rem;
        font-family: 'IBM Plex Mono', monospace;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
    }
    .cal-event-past {
        background: #1e1e1e;
        color: #8b949e;
    }

    /* Section header */
    .section-header {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        border-bottom: 1px solid #30363d;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    /* Stale data warning */
    .stale-badge {
        font-size: 0.7rem;
        color: #d29922;
        font-family: 'IBM Plex Mono', monospace;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Streamlit table overrides */
    .stDataFrame {
        border: 1px solid #30363d;
        border-radius: 8px;
        overflow: hidden;
    }

    /* Buttons */
    .stButton > button {
        background: #21262d;
        color: #e6edf3;
        border: 1px solid #30363d;
        border-radius: 6px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
    }
    .stButton > button:hover {
        background: #30363d;
        border-color: #58a6ff;
        color: #58a6ff;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        color: #8b949e;
    }
    .stTabs [aria-selected="true"] {
        color: #58a6ff !important;
        border-bottom: 2px solid #58a6ff !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTS & DEFAULT DATA
# ─────────────────────────────────────────────
ANALYSTS = [
    "Augustine", "Zach", "Kartik", "Nihir",
    "Boid", "Jake", "Tejas", "Sina", "Leah", "Rachel"
]

# Default holdings — edit or replace via the sidebar UI
DEFAULT_HOLDINGS = [
    {"ticker": "AAPL",  "company": "Apple Inc.",               "analyst": "Tejas"},
    {"ticker": "MSFT",  "company": "Microsoft Corp.",           "analyst": "Zach"},
    {"ticker": "GOOGL", "company": "Alphabet Inc.",             "analyst": "Kartik"},
    {"ticker": "AMZN",  "company": "Amazon.com Inc.",           "analyst": "Nihir"},
    {"ticker": "META",  "company": "Meta Platforms Inc.",       "analyst": "Boid"},
    {"ticker": "NVDA",  "company": "NVIDIA Corp.",              "analyst": "Jake"},
    {"ticker": "JPM",   "company": "JPMorgan Chase & Co.",      "analyst": "Augustine"},
    {"ticker": "UNH",   "company": "UnitedHealth Group Inc.",   "analyst": "Sina"},
    {"ticker": "V",     "company": "Visa Inc.",                 "analyst": "Leah"},
    {"ticker": "HD",    "company": "The Home Depot Inc.",       "analyst": "Rachel"},
]

HOLDINGS_FILE = "mpsif_holdings.json"
ANALYST_EMAILS_FILE = "mpsif_analyst_emails.json"

DEFAULT_ANALYST_EMAILS = {a: f"{a.lower()}@stern.nyu.edu" for a in ANALYSTS}


# ─────────────────────────────────────────────
# STATE HELPERS
# ─────────────────────────────────────────────
def load_holdings():
    if os.path.exists(HOLDINGS_FILE):
        with open(HOLDINGS_FILE) as f:
            return json.load(f)
    return DEFAULT_HOLDINGS

def save_holdings(holdings):
    with open(HOLDINGS_FILE, "w") as f:
        json.dump(holdings, f, indent=2)

def load_analyst_emails():
    if os.path.exists(ANALYST_EMAILS_FILE):
        with open(ANALYST_EMAILS_FILE) as f:
            return json.load(f)
    return DEFAULT_ANALYST_EMAILS

def save_analyst_emails(emails):
    with open(ANALYST_EMAILS_FILE, "w") as f:
        json.dump(emails, f, indent=2)


# ─────────────────────────────────────────────
# YAHOO FINANCE HELPERS
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_earnings_date(ticker: str):
    """
    Returns (date_obj_or_None, time_str, is_estimate_bool)
    Tries calendar endpoint first, falls back to info dict.
    """
    try:
        tk = yf.Ticker(ticker)

        # --- Primary: earnings_dates DataFrame ---
        try:
            edf = tk.earnings_dates
            if edf is not None and not edf.empty:
                today = pd.Timestamp.today(tz="UTC")
                # Only look up to 365 days out
                window = today + pd.Timedelta(days=365)
                future = edf[edf.index >= today - pd.Timedelta(days=5)]
                future = future[future.index <= window]
                if not future.empty:
                    next_date = future.index.min()
                    eps_estimate = future.loc[next_date, "EPS Estimate"] if "EPS Estimate" in future.columns else None
                    is_estimate = pd.isna(eps_estimate)
                    # "Before Market Open" / "After Market Close" hint from column
                    call_time = ""
                    if "Call Time" in future.columns:
                        call_time = str(future.loc[next_date, "Call Time"]) if not pd.isna(future.loc[next_date, "Call Time"]) else ""
                    return next_date.date(), call_time, is_estimate
        except Exception:
            pass

        # --- Fallback: info dict ---
        info = tk.info
        for key in ("earningsDate", "earningsTimestamp", "earningsTimestampStart"):
            raw = info.get(key)
            if raw:
                if isinstance(raw, (list, tuple)):
                    raw = raw[0]
                try:
                    dt = datetime.fromtimestamp(int(raw)).date()
                    return dt, "", True
                except Exception:
                    pass

    except Exception:
        pass

    return None, "", True


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_info(ticker: str):
    """Returns dict with sector, marketCap, shortName."""
    try:
        info = yf.Ticker(ticker).info
        return {
            "sector": info.get("sector", "—"),
            "market_cap": info.get("marketCap"),
            "name": info.get("shortName", ticker),
        }
    except Exception:
        return {"sector": "—", "market_cap": None, "name": ticker}


def days_until(d):
    if d is None:
        return None
    return (d - date.today()).days


def fmt_market_cap(mc):
    if mc is None:
        return "—"
    if mc >= 1e12:
        return f"${mc/1e12:.1f}T"
    if mc >= 1e9:
        return f"${mc/1e9:.1f}B"
    return f"${mc/1e6:.0f}M"


def earnings_badge(d):
    if d is None:
        return '<span class="badge badge-past">TBD</span>'
    n = days_until(d)
    if n is None:
        return '<span class="badge badge-past">TBD</span>'
    if n < 0:
        return f'<span class="badge badge-past">{d.strftime("%b %d")}</span>'
    if n <= 7:
        return f'<span class="badge badge-soon">in {n}d</span>'
    if n <= 30:
        return f'<span class="badge badge-upcoming">in {n}d</span>'
    return f'<span class="badge badge-bmc">{d.strftime("%b %d")}</span>'


# ─────────────────────────────────────────────
# EMAIL HELPER
# ─────────────────────────────────────────────
def send_earnings_reminder(
    smtp_host, smtp_port, smtp_user, smtp_pass,
    to_email, analyst_name, holdings_rows
):
    """Send an earnings reminder email to one analyst."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"MPSIF Earnings Reminder — {analyst_name}"
    msg["From"] = smtp_user
    msg["To"] = to_email

    rows_html = ""
    for row in holdings_rows:
        d = row["earnings_date"]
        n = days_until(d) if d else None
        days_str = f"in {n} day{'s' if n != 1 else ''}" if n is not None and n >= 0 else (d.strftime("%b %d") if d else "TBD")
        rows_html += f"""
        <tr>
          <td style="padding:8px 12px;font-family:monospace;font-weight:600;">{row['ticker']}</td>
          <td style="padding:8px 12px;">{row['company']}</td>
          <td style="padding:8px 12px;font-family:monospace;">{d.strftime('%B %d, %Y') if d else 'TBD'}</td>
          <td style="padding:8px 12px;color:#3fb950;font-family:monospace;">{days_str}</td>
        </tr>
        """

    html = f"""
    <html><body style="background:#0d1117;color:#e6edf3;font-family:'IBM Plex Sans',sans-serif;padding:24px;">
      <h2 style="color:#58a6ff;font-family:monospace;">MPSIF — Earnings Reminder</h2>
      <p>Hi {analyst_name},</p>
      <p>Here are the upcoming earnings dates for your holdings:</p>
      <table style="border-collapse:collapse;width:100%;background:#161b22;border:1px solid #30363d;border-radius:8px;">
        <thead>
          <tr style="background:#21262d;color:#8b949e;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;">
            <th style="padding:8px 12px;text-align:left;">Ticker</th>
            <th style="padding:8px 12px;text-align:left;">Company</th>
            <th style="padding:8px 12px;text-align:left;">Earnings Date</th>
            <th style="padding:8px 12px;text-align:left;">When</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
      <p style="color:#8b949e;font-size:0.85rem;margin-top:24px;">— MPSIF Earnings Calendar</p>
    </body></html>
    """
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "holdings" not in st.session_state:
    st.session_state.holdings = load_holdings()
if "analyst_emails" not in st.session_state:
    st.session_state.analyst_emails = load_analyst_emails()
if "earnings_cache" not in st.session_state:
    st.session_state.earnings_cache = {}


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 MPSIF")
    st.markdown('<div class="section-header">Filter</div>', unsafe_allow_html=True)

    selected_analysts = st.multiselect(
        "Analyst",
        options=ANALYSTS,
        default=ANALYSTS,
        label_visibility="collapsed",
    )

    show_past = st.checkbox("Show past earnings", value=False)

    st.markdown('<div class="section-header" style="margin-top:1.5rem;">Manage Holdings</div>', unsafe_allow_html=True)

    with st.expander("➕ Add Holding"):
        new_ticker = st.text_input("Ticker", key="new_ticker").upper().strip()
        new_company = st.text_input("Company Name", key="new_company")
        new_analyst = st.selectbox("Analyst", ANALYSTS, key="new_analyst")
        if st.button("Add"):
            if new_ticker:
                existing = [h["ticker"] for h in st.session_state.holdings]
                if new_ticker in existing:
                    st.error("Ticker already exists.")
                else:
                    st.session_state.holdings.append({
                        "ticker": new_ticker,
                        "company": new_company or new_ticker,
                        "analyst": new_analyst,
                    })
                    save_holdings(st.session_state.holdings)
                    st.success(f"Added {new_ticker}")
                    st.rerun()

    with st.expander("🗑️ Remove Holding"):
        tickers_to_remove = [h["ticker"] for h in st.session_state.holdings]
        remove_ticker = st.selectbox("Select ticker", tickers_to_remove, key="remove_ticker")
        if st.button("Remove"):
            st.session_state.holdings = [
                h for h in st.session_state.holdings if h["ticker"] != remove_ticker
            ]
            save_holdings(st.session_state.holdings)
            st.success(f"Removed {remove_ticker}")
            st.rerun()

    st.markdown('<div class="section-header" style="margin-top:1.5rem;">Email Reminders</div>', unsafe_allow_html=True)

    with st.expander("📧 SMTP Settings"):
        smtp_host = st.text_input("SMTP Host", value="smtp.gmail.com", key="smtp_host")
        smtp_port = st.text_input("SMTP Port", value="587", key="smtp_port")
        smtp_user = st.text_input("From Email", key="smtp_user")
        smtp_pass = st.text_input("App Password", type="password", key="smtp_pass")

    with st.expander("📬 Analyst Emails"):
        updated_emails = {}
        for a in ANALYSTS:
            updated_emails[a] = st.text_input(
                a, value=st.session_state.analyst_emails.get(a, ""), key=f"email_{a}"
            )
        if st.button("Save Emails"):
            st.session_state.analyst_emails = updated_emails
            save_analyst_emails(updated_emails)
            st.success("Saved.")

    with st.expander("📨 Send Reminders"):
        send_to = st.multiselect("Send to", ANALYSTS, default=ANALYSTS, key="send_to")
        days_filter = st.slider("Only holdings with earnings within X days", 1, 90, 30)
        if st.button("Send Reminder Emails"):
            if not smtp_user or not smtp_pass:
                st.error("Please fill in SMTP settings above.")
            else:
                sent, failed = 0, 0
                for analyst in send_to:
                    email = st.session_state.analyst_emails.get(analyst, "")
                    if not email:
                        continue
                    rows = []
                    for h in st.session_state.holdings:
                        if h["analyst"] != analyst:
                            continue
                        ed, _, _ = fetch_earnings_date(h["ticker"])
                        n = days_until(ed)
                        if n is not None and 0 <= n <= days_filter:
                            rows.append({**h, "earnings_date": ed})
                    if not rows:
                        continue
                    try:
                        send_earnings_reminder(
                            smtp_host, smtp_port, smtp_user, smtp_pass,
                            email, analyst, rows
                        )
                        sent += 1
                    except Exception as e:
                        failed += 1
                        st.error(f"Failed for {analyst}: {e}")
                st.success(f"Sent {sent} emails. {failed} failed.")


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
st.markdown('<h1 class="main-header">MPSIF Earnings Calendar</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="main-subheader">Long-only equity fund · NYU Stern · Real-time earnings tracking via Yahoo Finance</p>',
    unsafe_allow_html=True
)

# ── Build enriched holdings table ──────────────
filtered = [h for h in st.session_state.holdings if h["analyst"] in selected_analysts]

with st.spinner("Fetching earnings dates…"):
    rows = []
    for h in filtered:
        ed, call_time, is_est = fetch_earnings_date(h["ticker"])
        info = fetch_stock_info(h["ticker"])
        n = days_until(ed)
        rows.append({
            "ticker": h["ticker"],
            "company": h.get("company") or info["name"],
            "analyst": h["analyst"],
            "sector": info["sector"],
            "market_cap": fmt_market_cap(info["market_cap"]),
            "earnings_date": ed,
            "call_time": call_time,
            "is_estimate": is_est,
            "days_until": n,
        })

df = pd.DataFrame(rows)

# ── Summary metrics ────────────────────────────
today = date.today()
this_week = [r for r in rows if r["days_until"] is not None and 0 <= r["days_until"] <= 7]
this_month = [r for r in rows if r["days_until"] is not None and 0 <= r["days_until"] <= 30]
no_date = [r for r in rows if r["earnings_date"] is None]

c1, c2, c3, c4 = st.columns(4)
for col, val, label in [
    (c1, len(rows), "Total Holdings"),
    (c2, len(this_week), "Earnings This Week"),
    (c3, len(this_month), "Earnings This Month"),
    (c4, len(no_date), "Date TBD"),
]:
    col.markdown(f"""
    <div class="metric-card">
      <div class="metric-value">{val}</div>
      <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS: LIST VIEW  |  CALENDAR VIEW
# ─────────────────────────────────────────────
tab_list, tab_cal = st.tabs(["📋  List View", "📅  Calendar View"])


# ── LIST VIEW ─────────────────────────────────
with tab_list:
    # Sort options
    sort_col, _, filter_col = st.columns([2, 3, 2])
    with sort_col:
        sort_by = st.selectbox(
            "Sort by",
            ["Earnings Date (soonest)", "Ticker A→Z", "Analyst", "Market Cap"],
            label_visibility="collapsed",
            key="sort_by"
        )

    sort_map = {
        "Earnings Date (soonest)": ("days_until", True),
        "Ticker A→Z": ("ticker", True),
        "Analyst": ("analyst", True),
        "Market Cap": ("market_cap", True),
    }
    sort_key, asc = sort_map[sort_by]

    display_rows = [r for r in rows if show_past or r["days_until"] is None or r["days_until"] >= 0]
    display_rows = sorted(
        display_rows,
        key=lambda r: (r[sort_key] is None, r[sort_key])
        if sort_key != "days_until"
        else (r["days_until"] is None, r["days_until"] if r["days_until"] is not None else 9999),
        reverse=not asc
    )

    if not display_rows:
        st.info("No holdings match current filters.")
    else:
        # Column headers
        hcols = st.columns([1.2, 3, 1.8, 1.5, 1.5, 1.8, 1.8])
        headers = ["TICKER", "COMPANY", "ANALYST", "SECTOR", "MKT CAP", "EARNINGS DATE", "WHEN"]
        for col, h in zip(hcols, headers):
            col.markdown(f'<div class="section-header" style="margin-bottom:0.25rem;">{h}</div>', unsafe_allow_html=True)

        st.markdown('<hr style="border:none;border-top:1px solid #30363d;margin:0 0 0.5rem 0;">', unsafe_allow_html=True)

        for r in display_rows:
            rcols = st.columns([1.2, 3, 1.8, 1.5, 1.5, 1.8, 1.8])
            rcols[0].markdown(f"**`{r['ticker']}`**")
            rcols[1].markdown(r["company"])
            rcols[2].markdown(r["analyst"])
            rcols[3].markdown(f"<small style='color:#8b949e'>{r['sector']}</small>", unsafe_allow_html=True)
            rcols[4].markdown(f"<small style='color:#8b949e'>{r['market_cap']}</small>", unsafe_allow_html=True)
            ed = r["earnings_date"]
            est_tag = ' <small style="color:#d29922">~est</small>' if r["is_estimate"] and ed else ""
            rcols[5].markdown(
                f"{ed.strftime('%b %d, %Y') if ed else '—'}{est_tag}",
                unsafe_allow_html=True
            )
            rcols[6].markdown(earnings_badge(ed), unsafe_allow_html=True)
            st.markdown('<hr style="border:none;border-top:1px solid #21262d;margin:0.25rem 0;">', unsafe_allow_html=True)


# ── CALENDAR VIEW ──────────────────────────────
with tab_cal:
    cal_col1, cal_col2, _ = st.columns([1.5, 1.5, 5])
    with cal_col1:
        cal_month = st.selectbox(
            "Month", range(1, 13),
            index=today.month - 1,
            format_func=lambda m: calendar.month_name[m],
            label_visibility="collapsed",
            key="cal_month"
        )
    with cal_col2:
        cal_year = st.selectbox(
            "Year", range(today.year, today.year + 2),
            label_visibility="collapsed",
            key="cal_year"
        )

    # Build a map: date → list of (ticker, analyst)
    event_map: dict[date, list] = {}
    for r in rows:
        ed = r["earnings_date"]
        if ed and ed.month == cal_month and ed.year == cal_year:
            event_map.setdefault(ed, []).append((r["ticker"], r["analyst"]))

    # Calendar grid
    cal_matrix = calendar.monthcalendar(cal_year, cal_month)
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Header row
    hcols = st.columns(7)
    for col, dn in zip(hcols, day_names):
        col.markdown(
            f'<div style="text-align:center;font-family:\'IBM Plex Mono\',monospace;font-size:0.75rem;color:#8b949e;padding-bottom:4px;">{dn}</div>',
            unsafe_allow_html=True
        )

    for week in cal_matrix:
        wcols = st.columns(7)
        for col, day in zip(wcols, week):
            if day == 0:
                col.markdown('<div class="cal-cell" style="background:transparent;border-color:transparent;"></div>', unsafe_allow_html=True)
                continue

            this_date = date(cal_year, cal_month, day)
            is_today = this_date == today
            cell_class = "cal-cell-today" if is_today else "cal-cell"
            day_class = "cal-day-num-today" if is_today else "cal-day-num"

            events_html = ""
            for ticker, analyst in event_map.get(this_date, []):
                past_class = " cal-event-past" if this_date < today else ""
                events_html += f'<div class="cal-event{past_class}" title="{ticker} — {analyst}">{ticker}</div>'

            col.markdown(f"""
            <div class="{cell_class}">
              <div class="{day_class}">{day}</div>
              {events_html}
            </div>
            """, unsafe_allow_html=True)

    # Legend for calendar
    st.markdown("""
    <div style="margin-top:1rem;display:flex;gap:1rem;align-items:center;">
      <span style="font-size:0.75rem;color:#8b949e;">Legend:</span>
      <span class="cal-event" style="position:static;">TICKER — future</span>
      <span class="cal-event cal-event-past" style="position:static;">TICKER — past</span>
      <div style="width:12px;height:12px;border:1px solid #58a6ff;background:#0d2044;border-radius:2px;display:inline-block;"></div>
      <span style="font-size:0.75rem;color:#8b949e;">Today</span>
    </div>
    """, unsafe_allow_html=True)

    # Upcoming events list for selected month
    if event_map:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Events This Month</div>', unsafe_allow_html=True)
        for d in sorted(event_map.keys()):
            for ticker, analyst in event_map[d]:
                r = next((x for x in rows if x["ticker"] == ticker), {})
                n = days_until(d)
                tag = earnings_badge(d)
                st.markdown(
                    f"**`{ticker}`** &nbsp;·&nbsp; {r.get('company','')}"
                    f" &nbsp;·&nbsp; {analyst}"
                    f" &nbsp;·&nbsp; {d.strftime('%A, %B %d')} &nbsp; {tag}",
                    unsafe_allow_html=True
                )


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.7rem;color:#30363d;text-align:center;">'
    'MPSIF Earnings Calendar · Data via Yahoo Finance · Earnings dates may be estimates · '
    f'Last refreshed: {datetime.now().strftime("%Y-%m-%d %H:%M")} ET'
    '</div>',
    unsafe_allow_html=True
)
