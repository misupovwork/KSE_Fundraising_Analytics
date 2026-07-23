# a

import streamlit as st
import pandas as pd
import re
import altair as alt
import numpy as np
from datetime import date
from html import escape

st.set_page_config(page_title="KSE Donation Analytics", page_icon="📊", layout="wide")


# ── Keep chart labels inside their card ──────────────────────────────
# Vega does not reserve horizontal room for value-label text marks or wide
# axis ticks, so the rightmost "$1,234,567" label used to paint past the
# card border. Wrapping altair_chart once applies padding + fit-x autosize
# to every chart in the app, so content is contained instead of overflowing.
_ORIG_ALTAIR_CHART = st.altair_chart

def _padded_altair_chart(chart, *args, **kwargs):
    try:
        chart = chart.properties(
            padding={"left": 6, "right": 40, "top": 16, "bottom": 6},
            autosize={"type": "fit-x", "contains": "padding"},
        )
    except Exception:
        pass
    return _ORIG_ALTAIR_CHART(chart, *args, **kwargs)

st.altair_chart = _padded_altair_chart


def install_theme():
    """Central visual system for the Streamlit shell — Fundraise Up-inspired Insights design."""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

:root{
  --navy:#0F2A52; --ink:#141A24; --ink-2:#46506A;
  --canvas:#F6F8FC; --paper:#FFFFFF; --paper-2:#F2F5FB;
  --brand:#1B4DB1; --brand-strong:#16409A; --brand-wash:#EAF0FB; --brand-line:#D4E0F4;
  --gold:#C0892B; --gold-wash:#F7EFDD;
  --line:#E5EAF3; --muted:#6B7488;
  --good:#1E9E6A; --neg:#D5524E;
  --card-sh:0 1px 2px rgba(15,42,82,0.05), 0 1px 3px rgba(15,42,82,0.04);
  --card-sh-lg:0 16px 36px -20px rgba(15,42,82,0.32);
  --display:"Space Grotesk", ui-sans-serif, system-ui, -apple-system, sans-serif;
  --body:"Inter", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  --mono:"IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
}

/* ---- base ---- */
.stApp{ background:var(--canvas); color:var(--ink); font-family:var(--body); }
[data-testid="stAppViewContainer"] > .main .block-container{ max-width:1220px; padding:2.2rem 2.4rem 4rem; }
[data-testid="stHeader"]{ background:transparent; }
[data-testid="stToolbar"]{ right:1rem; }
a{ color:var(--brand); }
::selection{ background:rgba(27,77,177,0.15); }

/* ---- sidebar ---- */
[data-testid="stSidebar"]{ background:var(--paper); border-right:1px solid var(--line); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] span{ color:var(--muted); }

.brand-block{ display:flex; gap:0.85rem; padding:0 0 1.15rem; border-bottom:1px solid var(--line); margin-bottom:0.5rem; }
.brand-rule{ flex:0 0 3px; width:3px; border-radius:2px; background:linear-gradient(var(--navy), var(--brand)); }
.brand-kicker{ font-family:var(--mono); font-size:0.6rem; font-weight:600; letter-spacing:0.18em; text-transform:uppercase; color:var(--brand) !important; margin:0 0 0.4rem; }
.brand-title{ font-family:var(--display); font-size:1.18rem; font-weight:700; line-height:1.04; letter-spacing:-0.02em; color:var(--navy) !important; margin:0; }
.brand-subtitle{ font-size:0.78rem; line-height:1.5; color:var(--muted) !important; margin:0.55rem 0 0; }

.side-label{ font-family:var(--mono); font-size:0.62rem !important; font-weight:600; letter-spacing:0.16em; text-transform:uppercase; color:var(--muted) !important; margin:0.2rem 0 0.55rem !important; }

/* ---- labels ---- */
.home-kicker,.page-kicker,.section-kicker{ font-family:var(--mono); font-size:0.64rem; font-weight:600; letter-spacing:0.16em; text-transform:uppercase; color:var(--brand); margin:0 0 0.5rem; }
.section-kicker{ color:var(--muted); }
.kick-slash{ color:var(--gold); margin:0 0.5em; font-weight:600; }

/* ================= HOME ================= */
.home-top{ display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap; margin-bottom:2.1rem; }
.session-chip{ display:inline-flex; align-items:center; gap:0.5rem; font-family:var(--mono); font-size:0.66rem; letter-spacing:0.03em; color:var(--muted); background:var(--paper); border:1px solid var(--line); border-radius:999px; padding:0.36rem 0.8rem; box-shadow:var(--card-sh); }
.session-chip .dot{ width:7px; height:7px; border-radius:50%; background:var(--good); box-shadow:0 0 0 3px rgba(30,158,106,0.16); }

.home-hero{ display:flex; gap:1.4rem; }
.hero-spine{ flex:0 0 4px; width:4px; border-radius:3px; background:linear-gradient(var(--navy), var(--brand) 62%, var(--gold)); align-self:stretch; }
.home-title{ font-family:var(--display); font-weight:700; font-size:clamp(2.1rem,3.4vw,3.05rem); line-height:1.04; letter-spacing:-0.03em; color:var(--navy); margin:0; max-width:30ch; }
.home-title .em{ color:var(--brand); }
.home-copy{ font-size:1.03rem; line-height:1.62; color:var(--ink-2); max-width:64ch; margin:1.15rem 0 0; }
.home-stats{ display:flex; gap:0; margin-top:1.85rem; flex-wrap:wrap; }
.home-stat{ padding:0 1.15rem; }
.home-stat:first-child{ padding-left:0; }
.home-stat + .home-stat{ border-left:1px solid var(--line); }
.home-stat strong{ display:block; font-family:var(--display); font-size:0.92rem; font-weight:600; color:var(--ink); letter-spacing:-0.01em; }
.home-stat span{ font-size:0.76rem; color:var(--muted); line-height:1.4; }

/* upload module header */
.upload-accent{ width:30px; height:3px; border-radius:2px; background:var(--gold); margin:0.15rem 0 0.75rem; }
.upload-title{ font-family:var(--display); font-size:1.18rem; font-weight:600; color:var(--navy); margin:0 0 0.3rem; letter-spacing:-0.015em; }
.upload-sub{ font-size:0.87rem; color:var(--muted); line-height:1.55; margin:0 0 0.2rem; }
.upload-hint{ font-family:var(--mono); font-size:0.68rem; letter-spacing:0.01em; color:var(--muted); margin:0.9rem 0 0; }
.upload-hint b{ color:var(--ink-2); font-weight:600; }

/* real file_uploader -> dropzone card */
[data-testid="stFileUploader"]{ margin-top:0.2rem; }
[data-testid="stFileUploader"] label{ display:none; }
[data-testid="stFileUploaderDropzone"], [data-testid="stFileUploader"] section{
  background:var(--paper); border:1.5px dashed var(--brand-line); border-radius:14px; padding:1.5rem 1.4rem; transition:.18s; box-shadow:var(--card-sh);
}
[data-testid="stFileUploaderDropzone"]:hover, [data-testid="stFileUploader"] section:hover{
  border-color:var(--brand); background:var(--brand-wash);
}
[data-testid="stFileUploader"] small, [data-testid="stFileUploader"] span{ color:var(--muted); }
[data-testid="stFileUploaderDropzoneInstructions"] span{ color:var(--ink) !important; font-weight:600; }
[data-testid="stFileUploader"] svg{ color:var(--brand); fill:var(--brand); }
[data-testid="stFileUploader"] button{ background:var(--brand) !important; color:#fff !important; border:1px solid var(--brand) !important; border-radius:10px !important; font-weight:600 !important; box-shadow:none !important; }
[data-testid="stFileUploader"] button:hover{ border-color:var(--brand-strong) !important; background:var(--brand-strong) !important; color:#fff !important; }

/* section divider */
.sec-head{ display:flex; align-items:center; gap:1rem; margin:2.6rem 0 1.4rem; }
.sec-head .lbl{ font-family:var(--mono); font-size:0.64rem; font-weight:600; letter-spacing:0.14em; text-transform:uppercase; color:var(--muted); white-space:nowrap; }
.sec-head .ln{ height:1px; background:var(--line); flex:1; }

/* capability cards */
.cap{ background:var(--paper); border:1px solid var(--line); border-radius:14px; padding:1.5rem 1.5rem; height:100%; transition:.18s; box-shadow:var(--card-sh); }
.cap:hover{ transform:translateY(-2px); border-color:var(--brand-line); box-shadow:var(--card-sh-lg); }
.cap-top{ display:flex; align-items:center; gap:0.85rem; margin-bottom:0.8rem; }
.cap-ico{ flex:0 0 42px; height:42px; border-radius:11px; background:var(--brand-wash); color:var(--brand); display:flex; align-items:center; justify-content:center; }
.cap-ico svg{ width:20px; height:20px; }
.cap-ico.alt{ background:var(--gold-wash); color:var(--gold); }
.cap-name{ font-family:var(--display); font-size:1.05rem; font-weight:600; color:var(--navy); margin:0; letter-spacing:-0.01em; }
.cap-desc{ font-size:0.88rem; line-height:1.58; color:var(--ink-2); margin:0 0 1rem; }
.cap-tags{ display:flex; flex-wrap:wrap; gap:0.4rem; }
.cap-tag{ font-family:var(--mono); font-size:0.66rem; letter-spacing:0.01em; color:var(--muted); background:var(--paper-2); border:1px solid var(--line); border-radius:7px; padding:0.26rem 0.6rem; }

/* ============ ANALYTICS SHELL ============ */
.page-hero{ display:flex; gap:1.2rem; align-items:flex-start; justify-content:space-between; margin:0 0 1.4rem; }
.page-hero-left{ display:flex; gap:1.15rem; }
.page-spine{ flex:0 0 4px; width:4px; border-radius:3px; background:linear-gradient(var(--navy), var(--brand)); align-self:stretch; }
.page-title{ font-family:var(--display); font-weight:700; font-size:clamp(1.7rem,2.6vw,2.35rem); line-height:1.06; letter-spacing:-0.02em; color:var(--navy); margin:0.05rem 0 0; }
.page-copy{ font-size:0.95rem; line-height:1.58; color:var(--muted); max-width:760px; margin:0.55rem 0 0; }
.hero-pills{ display:flex; flex-wrap:wrap; gap:0.45rem; }
.hero-pill{ display:inline-flex; align-items:center; min-height:28px; border:1px solid var(--line); border-radius:999px; background:var(--paper); color:var(--ink-2); font-family:var(--mono); font-size:0.68rem; letter-spacing:0.01em; padding:0.26rem 0.72rem; white-space:nowrap; }

.data-strip{ display:flex; flex-wrap:wrap; align-items:center; gap:0; border-bottom:1px solid var(--line); padding:0 0 0.95rem; margin:0 0 1.7rem; }
.data-pill{ display:inline-flex; align-items:center; font-family:var(--mono); font-size:0.7rem; letter-spacing:0.02em; color:var(--muted); padding:0.1rem 0; }
.data-pill + .data-pill{ border-left:1px solid var(--line); padding-left:0.85rem; margin-left:0.85rem; }
.data-pill strong{ color:var(--ink); margin-left:0.5rem; font-weight:600; font-variant-numeric:tabular-nums; }

/* KPI metric cards */
div[data-testid="stMetric"]{ background:var(--paper); border:1px solid var(--line); border-radius:12px; padding:0.95rem 1rem 1rem; box-shadow:var(--card-sh); container-type:inline-size; transition:.15s; }
div[data-testid="stMetric"]:hover{ border-color:var(--brand-line); }
div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricLabel"]{ color:var(--muted) !important; overflow:visible !important; max-width:none !important; }
div[data-testid="stMetric"] label p{ font-family:var(--mono); font-size:0.8rem !important; font-weight:600 !important; letter-spacing:0.04em; text-transform:uppercase; color:var(--muted) !important; white-space:normal !important; overflow:visible !important; }
div[data-testid="stMetricValue"]{ font-family:var(--display); color:var(--navy); font-size:clamp(1.05rem,13.5cqi,2rem); font-weight:700; letter-spacing:-0.03em; line-height:1.05; margin-top:0.45rem; white-space:nowrap; font-variant-numeric:tabular-nums; }
div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] *{ overflow:visible !important; text-overflow:clip !important; max-width:none !important; font-weight:700; }
div[data-testid="stMetricDelta"]{ font-family:var(--mono); font-size:0.72rem; background:transparent !important; padding:0.35rem 0 0 !important; font-variant-numeric:tabular-nums; }
div[data-testid="stMetricDelta"] svg{ width:0.85rem; height:0.85rem; fill:currentColor; }
div[data-testid="stMetricDelta"] *{ font-weight:600; color:inherit !important; }
div[data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Up"]){ color:var(--good) !important; }
div[data-testid="stMetricDelta"]:has(svg[data-testid="stMetricDeltaIcon-Down"]){ color:var(--neg) !important; }

/* buttons */
.stButton > button, [data-testid="stBaseButton-secondary"]{ border-radius:10px !important; border:1px solid var(--line) !important; font-weight:600 !important; color:var(--ink-2) !important; box-shadow:var(--card-sh); }
.stButton > button:hover{ border-color:var(--brand) !important; color:var(--brand-strong) !important; background:var(--brand-wash) !important; }

/* sidebar radio nav */
[data-testid="stSidebar"] [role="radiogroup"]{ gap:0.3rem; }
[data-testid="stSidebar"] [role="radiogroup"] label{ position:relative; border:1px solid transparent; border-radius:9px; padding:0.55rem 0.75rem; font-family:var(--body); font-size:0.9rem; font-weight:500; color:var(--ink-2) !important; transition:.15s; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover{ background:var(--paper-2); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){ background:var(--brand-wash); border-color:var(--brand-line); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked)::before{ content:""; position:absolute; left:0; top:50%; transform:translateY(-50%); width:3px; height:18px; border-radius:0 2px 2px 0; background:var(--gold); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) span,
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p{ color:var(--brand-strong) !important; font-weight:600; }

/* tabs */
.stTabs [data-baseweb="tab-list"]{ gap:0.4rem; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"]{ background:transparent !important; border:none !important; border-radius:0; color:var(--muted); font-weight:600; font-size:0.88rem; padding:0.6rem 0.4rem; }
.stTabs [data-baseweb="tab"]:hover{ color:var(--ink); }
.stTabs [aria-selected="true"]{ background:transparent !important; color:var(--brand-strong) !important; border:none !important; }
.stTabs [data-baseweb="tab-highlight"]{ background-color:var(--brand) !important; height:2.5px; }
.stTabs [data-baseweb="tab-border"]{ background-color:var(--line) !important; }

/* headings */
h2,h3,h4,h5{ font-family:var(--display); color:var(--navy); letter-spacing:-0.015em; }
h3{ font-size:1.1rem !important; margin-top:0.4rem !important; font-weight:600 !important; }
h4,h5{ font-weight:600 !important; }

/* chart cards: each chart sits in a soft white card */
[data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"]{
  background:var(--paper); border:1px solid var(--line); border-radius:12px;
  padding:1.05rem 1.15rem 0.7rem; box-shadow:var(--card-sh); margin:0.2rem 0 0.5rem;
}
.vega-embed summary, .vega-embed .vega-actions{ display:none !important; }

/* dataframe / table -> card */
[data-testid="stDataFrame"], [data-testid="stTable"]{ border:1px solid var(--line); border-radius:12px; overflow:hidden; box-shadow:var(--card-sh); }

/* generic bordered container -> soft card */
div[data-testid="stVerticalBlockBorderWrapper"]{ background:var(--paper); border:1px solid var(--line); border-radius:14px; box-shadow:var(--card-sh); }

/* alerts */
[data-testid="stAlert"]{ border-radius:12px; border:1px solid var(--line); font-size:0.88rem; }

/* multiselect filter chips */
[data-baseweb="tag"]{ background:var(--brand-wash) !important; border-radius:7px !important; }
[data-baseweb="tag"] span{ color:var(--brand-strong) !important; }
[data-baseweb="tag"] svg{ fill:var(--brand-strong) !important; }

/* dividers */
hr{ margin:1.5rem 0; border-color:var(--line); }

/* inputs */
[data-baseweb="select"] > div{ border-radius:9px; border-color:var(--line); }
[data-baseweb="input"] > div{ border-radius:9px; }

/* page-load reveal */
@keyframes riseIn{ from{ opacity:0; transform:translateY(10px);} to{ opacity:1; transform:none;} }
@keyframes spineGrow{ from{ transform:scaleY(0);} to{ transform:scaleY(1);} }
.reveal{ animation:riseIn .55s cubic-bezier(.2,.7,.3,1) both; }
.reveal-1{ animation-delay:.03s; } .reveal-2{ animation-delay:.12s; } .reveal-3{ animation-delay:.2s; }
.hero-spine,.page-spine{ transform-origin:top; animation:spineGrow .6s cubic-bezier(.2,.7,.3,1) both; }
@media (prefers-reduced-motion: reduce){ .reveal,.hero-spine,.page-spine{ animation:none !important; } }

@media (max-width: 900px){
  [data-testid="stAppViewContainer"] > .main .block-container{ padding:1.3rem 1rem 2rem; }
  .page-hero{ flex-direction:column; }
  .home-hero{ gap:1rem; }
}
</style>
""",
        unsafe_allow_html=True,
    )


# ── Brand palette: single source of truth for every chart (mirrors CSS) ──
NAVY      = "#0F2A52"
BRAND     = "#1B4DB1"
BLUE_MID  = "#5B8BE0"
BLUE_SOFT = "#9DBDEE"
GOLD      = "#C0892B"
GOOD      = "#1E9E6A"
NEG       = "#D5524E"
INK       = "#141A24"
MUTED     = "#6B7488"
GRID      = "#EEF2F8"
AXIS      = "#E5EAF3"
# Categorical palette — distinct hues so many categories / years side by side read
# apart at a glance, anchored on the institutional blue + gold so it stays on-brand.
CAT = ["#1B4DB1", "#C0892B", "#2C8C7C", "#B5495B", "#6E59A5", "#5B8BE0", "#4C9A4E", "#0F2A52", "#C2702F", "#8A8F9C"]


def install_chart_theme():
    """Register the KSE Altair theme: institutional blue ramp, one gold highlight, quiet greys."""
    cfg = {
        "background": "transparent",
        "view": {"stroke": "transparent", "fill": "transparent", "continuousHeight": 290},
        "font": "Inter, ui-sans-serif, system-ui, sans-serif",
        "axis": {
            "labelColor": MUTED, "titleColor": MUTED,
            "gridColor": GRID, "domainColor": AXIS, "tickColor": AXIS,
            "labelFont": "IBM Plex Mono, ui-monospace, monospace", "labelFontSize": 10,
            "titleFont": "IBM Plex Mono, ui-monospace, monospace", "titleFontWeight": 600, "titleFontSize": 10.5,
        },
        "legend": {
            "labelColor": "#46506A", "titleColor": MUTED,
            "labelFont": "Inter, sans-serif", "titleFont": "IBM Plex Mono, monospace",
            "titleFontSize": 9.5, "labelFontSize": 11, "symbolType": "circle", "symbolSize": 70,
        },
        "title": {
            "color": NAVY, "font": "Space Grotesk, sans-serif",
            "fontWeight": 600, "fontSize": 13.5, "anchor": "start", "dy": -4,
        },
        "range": {
            "category": CAT,
            "heatmap": ["#EFF4FB", BRAND],
            "ramp": ["#EFF4FB", BRAND],
        },
        "bar": {"color": BRAND},
        "line": {"color": BRAND, "strokeWidth": 2.4},
        "point": {"color": BRAND, "size": 50},
        "area": {"color": BRAND, "opacity": 0.10},
    }
    try:
        @alt.theme.register("kse", enable=True)
        def _kse_theme():
            return {"config": cfg}
    except Exception:
        try:
            alt.themes.register("kse", lambda: {"config": cfg})
            alt.themes.enable("kse")
        except Exception:
            pass


def render_page_header(kicker, title, copy, pills=None):
    pills_html = ""
    if pills:
        chips = "".join(f'<span class="hero-pill">{escape(str(p))}</span>' for p in pills)
        pills_html = f'<div class="hero-pills">{chips}</div>'
    st.markdown(
        f"""
<section class="page-hero">
  <div class="page-hero-left">
    <div class="page-spine"></div>
    <div>
      <p class="page-kicker">{escape(kicker)}</p>
      <h1 class="page-title">{escape(title)}</h1>
      <p class="page-copy">{escape(copy)}</p>
    </div>
  </div>
  {pills_html}
</section>
""",
        unsafe_allow_html=True,
    )


def render_data_strip(df, file_name):
    date_min = df["date"].min().strftime("%Y-%m-%d")
    date_max = df["date"].max().strftime("%Y-%m-%d")
    st.markdown(
        f"""
<div class="data-strip">
  <span class="data-pill">File <strong>{escape(file_name)}</strong></span>
  <span class="data-pill">Period <strong>{date_min} → {date_max}</strong></span>
  <span class="data-pill">Revenue <strong>{fmt(df["amount"].sum())}</strong></span>
  <span class="data-pill">Donors <strong>{df["donor_key"].nunique():,}</strong></span>
  <span class="data-pill">Transactions <strong>{len(df):,}</strong></span>
</div>
""",
        unsafe_allow_html=True,
    )


install_theme()
install_chart_theme()


# ══════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ══════════════════════════════════════════════════════════════════

def clean_money(val) -> float:
    """Parse a money value robustly.

    Handles: plain numbers, currency symbols/codes, thin/nbsp spaces,
    accounting-style negatives ``(1,234)``, scientific notation from Excel
    (``1e7``), and both US (``1,234.56``) and European (``1.234,56``)
    separator conventions. Previously large or oddly-formatted wire amounts
    could silently become 0.0 or a tiny number; this version keeps them.
    """
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)

    s = str(val).strip()
    if not s:
        return 0.0

    # accounting-style negative: (1,234.00) -> -1234.00
    neg = s.startswith("(") and s.endswith(")")
    if neg:
        s = s[1:-1]

    # normalise unicode spaces, then keep only number-relevant characters
    s = s.replace("\u00a0", "").replace("\u202f", "").replace(" ", "")
    s = re.sub(r"[^0-9eE\.,\-+]", "", s)
    if s in {"", "-", "+", ".", ","}:
        return 0.0

    # scientific notation (e.g. Excel exporting 10,000,000 as 1e7)
    if re.fullmatch(r"[-+]?\d*\.?\d+[eE][-+]?\d+", s):
        try:
            v = float(s)
            return -v if neg else v
        except ValueError:
            return 0.0

    s = s.lstrip("+")
    has_comma, has_dot = "," in s, "." in s
    if has_comma and has_dot:
        # the separator that appears last is the decimal separator
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")   # European: 1.234.567,89
        else:
            s = s.replace(",", "")                       # US: 1,234,567.89
    elif has_comma:
        parts = s.split(",")
        # a single comma with 1-2 trailing digits is a decimal comma; else thousands
        if len(parts) == 2 and len(parts[1]) in (1, 2):
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    elif has_dot:
        parts = s.split(".")
        # more than one dot => dots are thousands separators (1.234.567)
        if len(parts) > 2:
            s = s.replace(".", "")
        # a single dot is treated as a decimal point (USD data), left as-is

    try:
        v = float(s)
        return -v if neg else v
    except ValueError:
        return 0.0

def normalize_text(v) -> str:
    return "" if pd.isna(v) else str(v).strip()

def parse_recurring_flag(series):
    return series.astype(str).str.strip().str.lower().isin({"true","yes","1","y","recurring","✓","x"})

def extract_name_from_donation_name(s) -> str:
    """Extract donor name from 'Donor Name - $ 12345' style strings."""
    if pd.isna(s) or not str(s).strip():
        return ""
    import re
    m = re.match(r'^(.+?)\s*-\s*[\$₴€£¥]\s*[\d,\.]+', str(s).strip())
    if m:
        return m.group(1).strip()
    return str(s).strip()

def canon_name(s) -> str:
    """Normalize a person/org name so it matches across columns:
    lowercase, drop surrounding punctuation/quotes, collapse whitespace."""
    s = normalize_text(s).lower()
    if s in {"nan", "none"}:
        return ""
    s = re.sub(r"[\"'`.,;:()\[\]]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def donor_key_row(r):
    # Email is the strongest identifier when present.
    email = normalize_text(r.get("email", "")).lower()
    if email and email not in {"nan", "none"}:
        return f"email:{email}"
    # Otherwise match on the name from ANY name column, so the same party
    # doesn't split just because it's typed in Contact on some rows and in
    # Entity or Donation Name on others.
    name = (canon_name(r.get("contact_name", ""))
            or canon_name(r.get("entity_name", ""))
            or canon_name(r.get("donation_name", "")))
    return f"name:{name}" if name else "unknown"

def donor_display_name(r):
    if r["contact_name"]:  return r["contact_name"]
    if r["entity_name"]:   return r["entity_name"]
    if r["email"]:         return r["email"]
    if r["donation_name"]: return r["donation_name"]
    return r["donor_key"]

def fmt(v): return f"${v:,.0f}"
def fmt2(v): return f"${v:,.2f}"

def mom_delta(curr, prev):
    if prev == 0: return "+∞%" if curr > 0 else "—"
    return f"{(curr - prev) / prev * 100:+.1f}%"

pct_delta = mom_delta


# ══════════════════════════════════════════════════════════════════
# SHARED LOADER
# ══════════════════════════════════════════════════════════════════

def load_and_normalise(uploaded_file):
    name = uploaded_file.name
    is_csv = name.endswith(".csv")

    uploaded_file.seek(0)
    try:
        peek = pd.read_csv(uploaded_file, header=None, nrows=10) if is_csv \
               else pd.read_excel(uploaded_file, header=None, nrows=10)
    except Exception:
        peek = pd.DataFrame()
    header_row = next(
        (i for i, row in peek.iterrows() if any("Donation amount in USD" in str(v) for v in row.values)),
        0
    )

    uploaded_file.seek(0)
    try:
        df = pd.read_csv(uploaded_file, header=header_row) if is_csv \
             else pd.read_excel(uploaded_file, header=header_row)
    except Exception:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file) if is_csv else pd.read_excel(uploaded_file)

    df.columns = df.columns.astype(str).str.strip()
    if not {"Donation amount in USD", "Date of donation"}.issubset(df.columns):
        return None, "❌ Missing required columns."

    email_col    = next((c for c in ["Email","Email (Donations)"] if c in df.columns), None)
    source_col   = next((c for c in ["SOURCE (Donations)","SOURCE"] if c in df.columns), None)
    platform_col = next((c for c in ["Payment Platform","Platform"] if c in df.columns), None)
    entity_col   = next((c for c in ["Entity (Donations)","Entity Name","Entity"] if c in df.columns), None)
    contact_col  = next((c for c in ["Full Name","Contact Name","Contact Name Entity Name","Contact of the donor"] if c in df.columns), None)
    donation_name_col = next((c for c in ["Donation Name"] if c in df.columns), None)

    rmap = {"Donation amount in USD": "amount_raw", "Date of donation": "date"}
    if "Designations"           in df.columns: rmap["Designations"]            = "designation"
    if email_col:                               rmap[email_col]                 = "email"
    if source_col:                              rmap[source_col]                = "source"
    if platform_col:                            rmap[platform_col]              = "platform"
    if entity_col:                              rmap[entity_col]                = "entity_name"
    if contact_col:                             rmap[contact_col]               = "contact_name"
    if donation_name_col:                       rmap[donation_name_col]         = "donation_name_raw"
    if "Is Recurring Donation"  in df.columns: rmap["Is Recurring Donation"]   = "is_recurring"
    if "Donor status"           in df.columns: rmap["Donor status"]            = "donor_status"

    df = df.rename(columns=rmap)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["date"]).reset_index(drop=True)

    for col in ["email","contact_name","entity_name"]:
        df[col] = df.get(col, pd.Series([""] * len(df))).astype(str).fillna("").map(normalize_text)
    df.loc[df["email"].isin(["nan","none",""]), "email"] = ""

    # Extract donor name from Donation Name as fallback when contact/entity are absent
    if "donation_name_raw" in df.columns:
        df["donation_name"] = df["donation_name_raw"].apply(extract_name_from_donation_name)
    else:
        df["donation_name"] = ""
    df["designation"] = df.get("designation", pd.Series([""] * len(df))).fillna("").astype(str).str.strip().replace("nan","")

    df["donor_key"]  = df.apply(donor_key_row, axis=1)
    # Bridge: if the same name appears both with and without an email on
    # different rows, unify those rows under the email so one donor doesn't
    # split. No-op when the file carries no emails.
    if (df["email"].str.len() > 0).any():
        df["_canon"] = df.apply(
            lambda r: canon_name(r["contact_name"]) or canon_name(r["entity_name"]) or canon_name(r["donation_name"]),
            axis=1,
        )
        emailed = df[df["email"].str.len() > 0]
        name2email = (emailed.groupby("_canon")["email"]
                             .agg(lambda s: s.str.lower().value_counts().index[0])
                             .to_dict())
        mapped = df["_canon"].map(name2email)
        need = df["donor_key"].str.startswith("name:") & mapped.notna()
        df.loc[need, "donor_key"] = "email:" + mapped[need].str.lower()
        df.drop(columns=["_canon"], inplace=True)
    df["donor_name"] = df.apply(donor_display_name, axis=1)
    df["amount"]     = df["amount_raw"].apply(clean_money)
    # Donor-level lifetime stats across the WHOLE upload. Informational only —
    # no filtering is applied to them; every donation is included in the analytics.
    df["donor_total_all"]    = df.groupby("donor_key")["amount"].transform("sum")
    df["donor_max_gift_all"] = df.groupby("donor_key")["amount"].transform("max")
    df["month_key"]  = df["date"].dt.to_period("M")
    df["year"]       = df["date"].dt.year
    df["month_num"]  = df["date"].dt.month
    df["month_label"]= df["date"].dt.strftime("%b")
    df["is_recurring"] = parse_recurring_flag(df["is_recurring"]) if "is_recurring" in df.columns else False
    df["is_wire"]    = df.get("platform", pd.Series([""] * len(df))).astype(str).str.strip().str.lower().eq("wire transfers")

    # global first-donation → new vs repeat
    first = df.groupby("donor_key")["month_key"].min().rename("first_month")
    df    = df.join(first, on="donor_key")
    df["is_new_donor"] = df["month_key"] == df["first_month"]
    df["designation_label"] = df["designation"].replace("", "(no designation)")

    # cohort = first recurring month per donor
    rec_first = df[df["is_recurring"]].groupby("donor_key")["month_key"].min().rename("cohort_month")
    df = df.join(rec_first, on="donor_key")
    df["cohort_year"] = df["cohort_month"].apply(lambda x: str(x.year) if pd.notna(x) else "unknown")

    return df.sort_values("date").reset_index(drop=True), "OK"


# ══════════════════════════════════════════════════════════════════
# SIDEBAR — adaptive: navigation when loaded, caption when not
# ══════════════════════════════════════════════════════════════════

page = "General Analysis"

with st.sidebar:
    st.markdown(
        """
<div class="brand-block">
  <div class="brand-rule"></div>
  <div>
    <p class="brand-kicker">KSE&nbsp;Foundation</p>
    <p class="brand-title">Donation<br>Analytics</p>
    <p class="brand-subtitle">Fundraising performance, donor behavior, and recurring revenue health.</p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if "file_data" in st.session_state:
        st.markdown('<p class="section-kicker">Workspace</p>', unsafe_allow_html=True)
        page = st.radio(
            "Select view:",
            options=[
                "General Analysis",
                "Recurring Analysis",
            ],
            label_visibility="collapsed",
        )
        st.divider()
        if st.button("Change file", use_container_width=True):
            st.session_state.pop("file_data", None)
            st.session_state.pop("file_name", None)
            st.rerun()
    else:
        st.caption("Upload a Zoho CRM export to begin.")


# ══════════════════════════════════════════════════════════════════
# HOME PAGE — shown until a file is stored in session state
# ══════════════════════════════════════════════════════════════════

if "file_data" not in st.session_state:
    # --- top eyebrow + session chip ---
    st.markdown(
        """
<div class="home-top">
  <p class="home-kicker">KSE Foundation<span class="kick-slash">/</span>Donation Analytics</p>
  <span class="session-chip"><span class="dot"></span>Session only · nothing is stored</span>
</div>
""",
        unsafe_allow_html=True,
    )

    hero_col, up_col = st.columns([1.5, 0.95], gap="large")
    with hero_col:
        st.markdown(
            """
<section class="home-hero reveal reveal-1">
  <div class="hero-spine"></div>
  <div>
    <h1 class="home-title">Your fundraising numbers, <span class="em">ready in one upload.</span></h1>
    <p class="home-copy">Drop in your latest Zoho donation export and go straight to revenue trends, donor acquisition, recurring health, cohorts, and your largest gifts — no spreadsheet wrangling.</p>
    <div class="home-stats">
      <div class="home-stat"><strong>CSV or XLSX</strong><span>Straight from Zoho CRM</span></div>
      <div class="home-stat"><strong>Two workspaces</strong><span>General &amp; recurring</span></div>
      <div class="home-stat"><strong>In-session only</strong><span>Cleared when you leave</span></div>
    </div>
  </div>
</section>
""",
            unsafe_allow_html=True,
        )
    with up_col:
        st.markdown(
            """
<div class="reveal reveal-2">
  <div class="upload-accent"></div>
  <p class="upload-title">Upload an export</p>
  <p class="upload-sub">Use your current Zoho donation export.</p>
</div>
""",
            unsafe_allow_html=True,
        )
        _home_upload = st.file_uploader(
            "Upload your CRM export",
            type=["csv", "xlsx"],
            key="home_uploader",
            label_visibility="collapsed",
        )
        st.markdown(
            """
<p class="upload-hint"><b>Required:</b> Donation amount in USD · Date of donation</p>
""",
            unsafe_allow_html=True,
        )

    # --- divider ---
    st.markdown(
        """
<div class="sec-head reveal reveal-3">
  <span class="lbl">What you get once it's loaded</span>
  <span class="ln"></span>
</div>
""",
        unsafe_allow_html=True,
    )

    cap1, cap2 = st.columns(2, gap="medium")
    with cap1:
        st.markdown(
            """
<div class="cap">
  <div class="cap-top">
    <div class="cap-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 14l3-3 3 3 5-6"/></svg></div>
    <p class="cap-name">General performance</p>
  </div>
  <p class="cap-desc">Revenue and transaction trends, donor acquisition, channel and platform mix, designations, gift-size distribution, and the largest gifts on record.</p>
  <div class="cap-tags"><span class="cap-tag">Revenue</span><span class="cap-tag">Donors</span><span class="cap-tag">Channels</span><span class="cap-tag">Top gifts</span></div>
</div>
""",
            unsafe_allow_html=True,
        )
    with cap2:
        st.markdown(
            """
<div class="cap">
  <div class="cap-top">
    <div class="cap-ico alt"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 2l3 3-3 3"/><path d="M20 5H9a5 5 0 0 0-5 5"/><path d="M7 22l-3-3 3-3"/><path d="M4 19h11a5 5 0 0 0 5-5"/></svg></div>
    <p class="cap-name">Recurring program</p>
  </div>
  <p class="cap-desc">Monthly recurring revenue, subscriber growth, retention and churn, cohort curves, lifetime value, and your strongest recurring donors.</p>
  <div class="cap-tags"><span class="cap-tag">MRR</span><span class="cap-tag">Retention</span><span class="cap-tag">Cohorts</span><span class="cap-tag">LTV</span></div>
</div>
""",
            unsafe_allow_html=True,
        )

    # Persist bytes and rerun cleanly so the analytics page renders on its
    # own — not stacked beneath the still-visible home page HTML.
    if _home_upload is not None:
        st.session_state["file_data"] = _home_upload.read()
        st.session_state["file_name"] = _home_upload.name
        st.rerun()

    st.stop()


# ══════════════════════════════════════════════════════════════════
# LOAD DATA (cached) — reads from session state, not a widget
# ══════════════════════════════════════════════════════════════════

CACHE_VERSION = "v3"

@st.cache_data(show_spinner="Loading data…")
def cached_load(data: bytes, name: str, _version: str = CACHE_VERSION):
    import io
    f = io.BytesIO(data)
    f.name = name
    return load_and_normalise(f)

df_full, msg = cached_load(
    st.session_state["file_data"],
    st.session_state["file_name"],
)
if df_full is None:
    st.error(msg)
    # Clear bad file so the user can try a different upload
    st.session_state.pop("file_data", None)
    st.session_state.pop("file_name", None)
    st.stop()

render_data_strip(df_full, st.session_state["file_name"])


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — MONTHLY REPORT
# ══════════════════════════════════════════════════════════════════════════════

if page == "General Analysis":
    available = sorted(df_full["month_key"].unique())
    labels    = [str(m) for m in available]
    today     = date.today()

    default_idx = len(available) - 1
    if available[-1].year == today.year and available[-1].month == today.month and len(available) > 1:
        default_idx = len(available) - 2

    with st.sidebar:
        st.divider()
        st.markdown('<p class="side-label">Settings</p>', unsafe_allow_html=True)
        sel_label  = st.selectbox("Month to analyse:", labels, index=default_idx)
        plan_target = st.number_input("Revenue target USD (0 = skip)", min_value=0, value=0, step=1000)

        st.markdown('<p class="side-label">Filters</p>', unsafe_allow_html=True)
        if "source" in df_full.columns:
            all_sources = sorted(df_full["source"].fillna("(no source)").unique())
            sel_sources = st.multiselect("Source:", all_sources, default=all_sources)
        else:
            sel_sources = None

        if "platform" in df_full.columns:
            all_platforms = sorted(df_full["platform"].fillna("(no platform)").unique())
            sel_platforms = st.multiselect("Payment Platform:", all_platforms, default=all_platforms)
        else:
            sel_platforms = None

        if "entity_name" in df_full.columns:
            all_dirs = sorted(df_full["entity_name"].replace("", "(no direction)").unique())
            sel_dirs = st.multiselect("Direction:", all_dirs, default=all_dirs)
        else:
            sel_dirs = None

        all_desigs = sorted(df_full["designation_label"].unique())
        sel_desigs = st.multiselect("Designation:", all_desigs, default=all_desigs)

    sel_period  = available[labels.index(sel_label)]
    prev_period = sel_period - 1

    def apply_filters(df):
        d = df.copy()
        if sel_sources is not None:
            d["source_label"] = d["source"].fillna("(no source)")
            d = d[d["source_label"].isin(sel_sources)]
        if sel_platforms is not None:
            d["platform_label"] = d["platform"].fillna("(no platform)")
            d = d[d["platform_label"].isin(sel_platforms)]
        if sel_dirs is not None:
            d["dir_label"] = d["entity_name"].replace("", "(no direction)")
            d = d[d["dir_label"].isin(sel_dirs)]
        d = d[d["designation_label"].isin(sel_desigs)]
        return d

    df_cur    = apply_filters(df_full[df_full["month_key"] == sel_period].copy())
    df_prev   = apply_filters(df_full[df_full["month_key"] == prev_period].copy())
    df_full_f = apply_filters(df_full)

    if df_cur.empty:
        st.warning("No donations found for the selected month and filters."); st.stop()

    def month_metrics(df):
        return dict(
            revenue   = df["amount"].sum(),
            txns      = len(df),
            donors    = df["donor_key"].nunique(),
            avg_gift  = df["amount"].mean() if len(df) else 0,
            new_donors= df[df["is_new_donor"]]["donor_key"].nunique(),
            mrr       = df[df["is_recurring"]]["amount"].sum(),
            rec_donors= df[df["is_recurring"]]["donor_key"].nunique(),
            wire_rev  = df[df["is_wire"]]["amount"].sum(),
        )

    cur  = month_metrics(df_cur)
    prev = month_metrics(df_prev) if not df_prev.empty else None

    ret_pct = None
    if prev:
        prev_keys = set(df_prev["donor_key"])
        curr_keys = set(df_cur["donor_key"])
        ret_pct   = len(prev_keys & curr_keys) / len(prev_keys) * 100 if prev_keys else 0

    render_page_header(
        "General analysis",
        f"Monthly performance — {sel_label}",
        "Revenue, donor movement, recurring activity, designations, channels, and the largest gifts — for the month you select.",
        [
            f"{cur['donors']:,} donors",
            f"{cur['txns']:,} transactions",
            f"{fmt(cur['revenue'])} raised",
            f"{fmt(cur['mrr'])} recurring",
        ],
    )

    t1, t2, t3, t4, t5, t6 = st.tabs([
        "Revenue", "Donors", "Recurring", "Designations", "Channels", "Top Donations"
    ])

    # ── TAB 1 — REVENUE ──────────────────────────────────────────
    with t1:
        st.subheader("Revenue")
        plan_str  = f"{cur['revenue']/plan_target*100:.1f}%" if plan_target else "—"
        delta_rev = mom_delta(cur["revenue"], prev["revenue"]) if prev else "—"

        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Total Raised",  fmt(cur["revenue"]), delta=delta_rev if delta_rev != "—" else None)
        c2.metric("vs Plan",       plan_str)
        c3.metric("MoM Growth",    delta_rev)
        c4.metric("Transactions",  f"{cur['txns']:,}", delta=mom_delta(cur["txns"], prev["txns"]) if prev else None)
        c5.metric("Avg Gift",      fmt(cur["avg_gift"]))

        if plan_target:
            if cur["revenue"] >= plan_target:
                st.success(f"Plan achieved — {fmt(cur['revenue'])} of the {fmt(plan_target)} target.")
            else:
                st.warning(f"{fmt(plan_target - cur['revenue'])} short of the {fmt(plan_target)} target ({cur['revenue']/plan_target*100:.1f}% reached).")

        st.divider()
        trail_start = sel_period - 11
        trail_df    = df_full_f[(df_full_f["month_key"] >= trail_start) & (df_full_f["month_key"] <= sel_period)]
        rev_m = trail_df.groupby("month_key")["amount"].sum().reset_index()
        rev_m["month_str"]   = rev_m["month_key"].astype(str)
        rev_m["is_selected"] = rev_m["month_key"] == sel_period

        bar = alt.Chart(rev_m).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("month_str:O", sort=list(rev_m["month_str"]), title=""),
            y=alt.Y("amount:Q", title="USD", axis=alt.Axis(format="$,.0f")),
            color=alt.condition(alt.datum.is_selected, alt.value(GOLD), alt.value(BLUE_MID)),
            tooltip=["month_str:O", alt.Tooltip("amount:Q", format="$,.0f", title="Revenue")]
        ).properties(height=300, title="Trailing 12 months · selected month in gold")
        txt = bar.mark_text(dy=-8, fontSize=9).encode(text=alt.Text("amount:Q", format="$,.2s"))
        st.altair_chart(bar + txt, use_container_width=True)

        st.divider()
        st.subheader("Overall Revenue — Year-over-Year by Month")
        yoy_all = df_full_f.copy()
        yoy_all["year"]        = yoy_all["date"].dt.year.astype(str)
        yoy_all["month"]       = yoy_all["date"].dt.month
        yoy_all["month_label"] = yoy_all["date"].dt.strftime("%b")
        yoy_all_pivot = yoy_all.groupby(["month","month_label","year"])["amount"].sum().reset_index()
        month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        yoy_line_all = alt.Chart(yoy_all_pivot).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X("month_label:O", sort=month_order, title="", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("amount:Q", title="USD", axis=alt.Axis(format="$,.0f")),
            color=alt.Color("year:N", title="Year", scale=alt.Scale(range=CAT)),
            tooltip=["year:N","month_label:O", alt.Tooltip("amount:Q", format="$,.0f", title="Revenue")]
        ).properties(height=300)
        st.altair_chart(yoy_line_all, use_container_width=True)

        st.divider()
        st.subheader("Revenue by Payment Platform")
        if "platform" in df_cur.columns:
            plat_rev = df_cur.groupby(df_cur["platform"].fillna("(unknown)"))["amount"].sum().reset_index()
            plat_rev.columns = ["Platform", "Amount"]
            plat_rev = plat_rev.sort_values("Amount", ascending=False)
            plat_rev["pct"] = (plat_rev["Amount"] / plat_rev["Amount"].sum() * 100).apply(lambda x: f"{x:.1f}%")
            pc1, pc2 = st.columns([1, 1])
            with pc1:
                donut = alt.Chart(plat_rev).mark_arc(innerRadius=70).encode(
                    theta=alt.Theta("Amount:Q"),
                    color=alt.Color("Platform:N", scale=alt.Scale(range=CAT)),
                    tooltip=["Platform:N", alt.Tooltip("Amount:Q", format="$,.0f"), "pct:N"]
                ).properties(height=280)
                st.altair_chart(donut, use_container_width=True)
            with pc2:
                plat_rev["Amount_fmt"] = plat_rev["Amount"].apply(fmt)
                st.dataframe(
                    plat_rev[["Platform","Amount_fmt","pct"]].rename(columns={"Amount_fmt":"Revenue","pct":"% Rev"}),
                    use_container_width=True, hide_index=True
                )
        else:
            retail_rev = cur["revenue"] - cur["wire_rev"]
            wire_pct   = cur["wire_rev"] / cur["revenue"] * 100 if cur["revenue"] else 0
            wc1, wc2   = st.columns(2)
            wc1.metric("Wire Transfers",  fmt(cur["wire_rev"]), help=f"{wire_pct:.0f}% of total")
            wc2.metric("Retail Channels", fmt(retail_rev),      help=f"{100-wire_pct:.0f}% of total")

    # ── TAB 2 — DONORS ───────────────────────────────────────────
    with t2:
        st.subheader("Donors")
        repeat_donors = cur["donors"] - cur["new_donors"]
        new_pct       = cur["new_donors"] / cur["donors"] * 100 if cur["donors"] else 0

        d1,d2,d3,d4 = st.columns(4)
        d1.metric("Total Donors",  f"{cur['donors']:,}", delta=mom_delta(cur["donors"], prev["donors"]) if prev else None)
        d2.metric("New Donors",    f"{cur['new_donors']:,}", delta=mom_delta(cur["new_donors"], prev["new_donors"]) if prev else None)
        d3.metric("Returning",     f"{repeat_donors:,}")
        d4.metric("% New",         f"{new_pct:.1f}%")
        st.caption("New = a donor's first recorded donation anywhere in the dataset.")

        if ret_pct is not None:
            st.divider()
            st.subheader("This month vs Last month")
            prev_keys = set(df_prev["donor_key"])
            curr_keys = set(df_cur["donor_key"])
            retained  = len(prev_keys & curr_keys)
            lapsed    = len(prev_keys - curr_keys)
            ra,rb,rc = st.columns(3)
            ra.metric("Donors last month",   f"{len(prev_keys):,}")
            rb.metric("Retained this month", f"{retained:,}")
            rc.metric("Lapsed",              f"{lapsed:,}")

        st.divider()
        st.subheader("New vs. Returning — Trailing 12 Months")
        trail_start = sel_period - 11
        trail_df2   = df_full_f[(df_full_f["month_key"] >= trail_start) & (df_full_f["month_key"] <= sel_period)]
        dm = trail_df2.groupby(["month_key","is_new_donor"])["donor_key"].nunique().reset_index()
        dm["month_str"] = dm["month_key"].astype(str)
        dm["Type"] = dm["is_new_donor"].map({True:"New", False:"Returning"})
        bar_d = alt.Chart(dm).mark_bar().encode(
            x=alt.X("month_str:O", sort=list(dm["month_str"].unique()), title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("donor_key:Q", title="Donors", stack="zero"),
            color=alt.Color("Type:N", scale=alt.Scale(domain=["New","Returning"], range=[BRAND, BLUE_SOFT])),
            tooltip=["month_str:O","Type:N", alt.Tooltip("donor_key:Q", title="Donors")]
        ).properties(height=280)
        st.altair_chart(bar_d, use_container_width=True)

        st.divider()
        st.subheader(f"Top Donors — {sel_label}")
        st.caption("Ranked by total given within the selected month. Respects the sidebar filters.")

        if df_cur.empty:
            st.info("No donations in this month for the current filters.")
        else:
            n_top = st.slider("Show top", 5, 25, 10, step=5, key="top_donors_month_n")

            month_donors = df_cur.groupby("donor_key").agg(
                name     = ("donor_name",   "first"),
                total    = ("amount",       "sum"),
                gifts    = ("amount",       "count"),
                largest  = ("amount",       "max"),
                is_new   = ("is_new_donor", "any"),
                recurring= ("is_recurring", "any"),
            ).nlargest(n_top, "total").reset_index()

            month_rev = df_cur["amount"].sum()
            month_donors["share"] = (
                month_donors["total"] / month_rev * 100 if month_rev else 0
            )

            tbl = pd.DataFrame({
                "Donor":     month_donors["name"],
                "Total":     month_donors["total"].apply(fmt),
                "% of month": month_donors["share"].apply(lambda v: f"{v:.1f}%"),
                "Gifts":     month_donors["gifts"],
                "Largest":   month_donors["largest"].apply(fmt),
                "Type":      month_donors["is_new"].map({True: "New", False: "Returning"}),
                "Recurring": month_donors["recurring"].map({True: "Yes", False: "No"}),
            })
            st.dataframe(tbl, use_container_width=True, hide_index=True)

            shown = month_donors["total"].sum()
            st.caption(
                f"These {len(month_donors)} donors gave {fmt(shown)} of "
                f"{fmt(month_rev)} raised this month "
                f"({shown / month_rev * 100:.1f}%)." if month_rev else ""
            )

    # ── TAB 3 — RECURRING ────────────────────────────────────────
    with t3:
        st.subheader("Recurring Program")
        rec_share  = cur["mrr"] / cur["revenue"] * 100 if cur["revenue"] else 0
        avg_mg     = df_cur[df_cur["is_recurring"]]["amount"].mean()   if cur["rec_donors"] else 0
        median_mg  = df_cur[df_cur["is_recurring"]]["amount"].median() if cur["rec_donors"] else 0

        r1,r2,r3,r4,r5 = st.columns(5)
        r1.metric("MRR (this month)",    fmt(cur["mrr"]),          delta=mom_delta(cur["mrr"], prev["mrr"]) if prev else None)
        r2.metric("Active Subscribers",  f"{cur['rec_donors']:,}", delta=mom_delta(cur["rec_donors"], prev["rec_donors"]) if prev else None)
        r3.metric("% of Total Revenue",  f"{rec_share:.1f}%")
        r4.metric("Avg Monthly Gift",    fmt(avg_mg))
        r5.metric("Median Monthly Gift", fmt(median_mg))

        st.divider()
        st.subheader("MRR — Trailing 12 Months")
        trail_start = sel_period - 11
        trail_rec   = df_full_f[(df_full_f["month_key"] >= trail_start) & (df_full_f["month_key"] <= sel_period) & df_full_f["is_recurring"]]
        mrr_m = trail_rec.groupby("month_key")["amount"].sum().reset_index()
        mrr_m["month_str"] = mrr_m["month_key"].astype(str)
        mrr_m["is_selected"] = mrr_m["month_key"] == sel_period
        bar_mrr = alt.Chart(mrr_m).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("month_str:O", sort=list(mrr_m["month_str"]), title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("amount:Q", title="USD", axis=alt.Axis(format="$,.0f")),
            color=alt.condition(alt.datum.is_selected, alt.value(GOLD), alt.value(BLUE_MID)),
            tooltip=["month_str:O", alt.Tooltip("amount:Q", format="$,.0f", title="MRR")]
        ).properties(height=260)
        txt_mrr = bar_mrr.mark_text(dy=-8, fontSize=9).encode(text=alt.Text("amount:Q", format="$,.2s"))
        st.altair_chart(bar_mrr + txt_mrr, use_container_width=True)

        st.divider()
        st.subheader("New Subscriptions vs. Churn — Trailing 12 Months")
        all_rec_m  = sorted(df_full_f["month_key"].unique())
        churn_rows = []
        for m in [p for p in all_rec_m if trail_start <= p <= sel_period]:
            mp = m - 1
            d_cur_r  = set(df_full_f[(df_full_f["month_key"] == m)  & df_full_f["is_recurring"]]["donor_key"])
            d_prev_r = set(df_full_f[(df_full_f["month_key"] == mp) & df_full_f["is_recurring"]]["donor_key"])
            new_s    = len(d_cur_r - d_prev_r)
            churn_n  = len(d_prev_r - d_cur_r)
            ret_r    = len(d_cur_r & d_prev_r) / len(d_prev_r) * 100 if d_prev_r else 0
            churn_rows.append({"month_str": str(m), "New Subscriptions": new_s, "Churned": churn_n, "Retention %": ret_r})
        if churn_rows:
            ch_df = pd.DataFrame(churn_rows)
            melt  = ch_df.melt(id_vars="month_str", value_vars=["New Subscriptions","Churned"], var_name="Type", value_name="Count")
            bar_ch = alt.Chart(melt).mark_bar().encode(
                x=alt.X("month_str:O", sort=list(ch_df["month_str"]), title="", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("Count:Q"),
                color=alt.Color("Type:N", scale=alt.Scale(domain=["New Subscriptions","Churned"], range=[GOOD, NEG])),
                tooltip=["month_str:O","Type:N","Count:Q"]
            ).properties(height=240)
            st.altair_chart(bar_ch, use_container_width=True)

        st.divider()
        st.subheader("Recurring Revenue — Year-over-Year by Month")
        yoy_rec = df_full_f[df_full_f["is_recurring"]].copy()
        yoy_rec["year"]        = yoy_rec["date"].dt.year.astype(str)
        yoy_rec["month"]       = yoy_rec["date"].dt.month
        yoy_rec["month_label"] = yoy_rec["date"].dt.strftime("%b")
        yoy_pivot = yoy_rec.groupby(["month","month_label","year"])["amount"].sum().reset_index()
        month_order_rec = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        yoy_line_rec = alt.Chart(yoy_pivot).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X("month_label:O", sort=month_order_rec, title="", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("amount:Q", title="USD", axis=alt.Axis(format="$,.0f")),
            color=alt.Color("year:N", title="Year", scale=alt.Scale(range=CAT)),
            tooltip=["year:N","month_label:O", alt.Tooltip("amount:Q", format="$,.0f", title="MRR")]
        ).properties(height=300)
        st.altair_chart(yoy_line_rec, use_container_width=True)

        st.divider()
        st.subheader("Gift Size Distribution (recurring donors)")
        BRACKETS = [0,50,100,250,500,1000,float("inf")]
        LABELS   = ["$0–50","$50–100","$100–250","$250–500","$500–1k","$1k+"]
        rec_cur  = df_cur[df_cur["is_recurring"]].copy()
        if not rec_cur.empty:
            rec_cur["bracket"] = pd.cut(rec_cur["amount"], bins=BRACKETS, labels=LABELS, right=False)
            dc = rec_cur.groupby("bracket", observed=True)["donor_key"].nunique().reset_index(name="Donors")
            br = alt.Chart(dc).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X("bracket:O", sort=LABELS, title="", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("Donors:Q")
            )
            st.altair_chart(br + br.mark_text(dy=-8, fontSize=10).encode(text="Donors:Q"), use_container_width=True)

    # ── TAB 4 — DESIGNATIONS ─────────────────────────────────────
    with t4:
        st.subheader("Revenue by Designation")
        desig = df_cur.groupby("designation_label").agg(
            revenue=("amount","sum"),
            donors=("donor_key","nunique"),
            txns=("amount","count"),
        ).sort_values("revenue", ascending=False).reset_index()
        desig["% Rev"] = (desig["revenue"] / desig["revenue"].sum() * 100).apply(lambda x: f"{x:.1f}%")
        if not df_prev.empty:
            prev_desig = df_prev.groupby("designation_label")["amount"].sum().rename("prev_rev")
            desig = desig.join(prev_desig, on="designation_label")
            desig["MoM"] = desig.apply(lambda r: mom_delta(r["revenue"], r.get("prev_rev", 0) or 0), axis=1)
        else:
            desig["MoM"] = "—"
        desig["revenue_fmt"] = desig["revenue"].apply(fmt)
        if len(desig):
            top3 = desig.head(3)["revenue"].sum() / desig["revenue"].sum() * 100
            st.info(f"Top designation: **{desig.iloc[0]['designation_label']}** at {desig.iloc[0]['% Rev']}. The top 3 make up {top3:.0f}% of the month.")
        st.dataframe(
            desig[["designation_label","revenue_fmt","% Rev","MoM","donors","txns"]].rename(columns={
                "designation_label":"Designation","revenue_fmt":"Revenue","donors":"Donors","txns":"Txns"
            }),
            use_container_width=True, hide_index=True
        )
        st.divider()
        st.subheader("Designation — Trailing 12 Months")
        trail_start  = sel_period - 11
        trail_desig  = df_full_f[(df_full_f["month_key"] >= trail_start) & (df_full_f["month_key"] <= sel_period)]
        top5 = desig.head(5)["designation_label"].tolist()
        td = trail_desig[trail_desig["designation_label"].isin(top5)].groupby(["month_key","designation_label"])["amount"].sum().reset_index()
        td["month_str"] = td["month_key"].astype(str)
        line_d = alt.Chart(td).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X("month_str:O", axis=alt.Axis(labelAngle=-45), title=""),
            y=alt.Y("amount:Q", title="USD", axis=alt.Axis(format="$,.0f")),
            color=alt.Color("designation_label:N", title="Designation"),
            tooltip=["month_str:O","designation_label:N", alt.Tooltip("amount:Q", format="$,.0f")]
        ).properties(height=280)
        st.altair_chart(line_d, use_container_width=True)
        st.caption("Top 5 designations shown.")

    # ── TAB 5 — CHANNELS ─────────────────────────────────────────
    with t5:
        st.subheader("Revenue by Channel (Source)")
        if "source" not in df_cur.columns:
            st.info("No 'SOURCE' column found in the export.")
        else:
            df_cur["source_label"] = df_cur["source"].fillna("(no source)")
            ch = df_cur.groupby("source_label").agg(
                revenue=("amount","sum"),
                donors=("donor_key","nunique"),
                new_donors=("is_new_donor","sum"),
                txns=("amount","count"),
            ).sort_values("revenue", ascending=False).reset_index()
            if not df_prev.empty and "source" in df_prev.columns:
                df_prev["source_label"] = df_prev["source"].fillna("(no source)")
                prev_ch = df_prev.groupby("source_label")["amount"].sum().rename("prev_rev")
                ch = ch.join(prev_ch, on="source_label")
                ch["MoM"] = ch.apply(lambda r: mom_delta(r["revenue"], r.get("prev_rev", 0) or 0), axis=1)
            else:
                ch["MoM"] = "—"
            ch["% Rev"]        = (ch["revenue"] / ch["revenue"].sum() * 100).apply(lambda x: f"{x:.1f}%")
            ch["revenue_fmt"]  = ch["revenue"].apply(fmt)
            st.dataframe(
                ch[["source_label","revenue_fmt","% Rev","MoM","donors","new_donors","txns"]].rename(columns={
                    "source_label":"Channel","revenue_fmt":"Revenue",
                    "donors":"Donors","new_donors":"New Donors","txns":"Txns"
                }),
                use_container_width=True, hide_index=True
            )
            st.divider()
            bar_ch = alt.Chart(ch).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X("source_label:O", sort="-y", title=""),
                y=alt.Y("revenue:Q", title="USD", axis=alt.Axis(format="$,.0f")),
                tooltip=["source_label:O", alt.Tooltip("revenue:Q", format="$,.0f"), "donors:Q"]
            ).properties(height=260)
            st.altair_chart(bar_ch, use_container_width=True)
            st.divider()
            st.subheader("Channel Revenue — Trailing 12 Months")
            trail_start = sel_period - 11
            trail_ch = df_full_f[(df_full_f["month_key"] >= trail_start) & (df_full_f["month_key"] <= sel_period)].copy()
            if "source" in trail_ch.columns:
                trail_ch["source_label"] = trail_ch["source"].fillna("(no source)")
                top5_ch = ch.head(5)["source_label"].tolist()
                tc = trail_ch[trail_ch["source_label"].isin(top5_ch)].groupby(["month_key","source_label"])["amount"].sum().reset_index()
                tc["month_str"] = tc["month_key"].astype(str)
                line_ch = alt.Chart(tc).mark_line(point=True, strokeWidth=2).encode(
                    x=alt.X("month_str:O", axis=alt.Axis(labelAngle=-45), title=""),
                    y=alt.Y("amount:Q", title="USD", axis=alt.Axis(format="$,.0f")),
                    color=alt.Color("source_label:N", title="Channel"),
                    tooltip=["month_str:O","source_label:N", alt.Tooltip("amount:Q", format="$,.0f")]
                ).properties(height=260)
                st.altair_chart(line_ch, use_container_width=True)
                st.caption("Top 5 channels shown.")

    # ── TAB 6 — TOP DONATIONS ────────────────────────────────────
    with t6:
        st.subheader("Top 10 Donations of All Time")
        st.caption("Ranked by single transaction amount — from the full dataset (all years, ignoring filters).")

        top10_txns = df_full.nlargest(10, "amount")[
            ["date", "amount", "donor_name", "designation_label", "platform", "is_recurring"]
        ].copy()

        top10_txns["date"]         = top10_txns["date"].dt.strftime("%Y-%m-%d")
        top10_txns["amount_fmt"]   = top10_txns["amount"].apply(fmt)
        top10_txns["is_recurring"] = top10_txns["is_recurring"].map({True: "Recurring", False: "One-time"})

        rename_txns = {
            "date": "Date", "amount_fmt": "Amount", "donor_name": "Donor",
            "designation_label": "Designation", "platform": "Platform", "is_recurring": "Type"
        }
        top10_txns = top10_txns.drop(columns=["amount"]).rename(columns=rename_txns)
        cols_txns  = ["Date", "Amount", "Donor", "Designation", "Platform", "Type"]
        cols_txns  = [c for c in cols_txns if c in top10_txns.columns]
        st.dataframe(top10_txns[cols_txns], use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Top 10 Donors of All Time (by total given)")
        st.caption("Sum of all donations per donor — full dataset.")

        top_donors = df_full.groupby("donor_key").agg(
            total     = ("amount", "sum"),
            txns      = ("amount", "count"),
            avg_gift  = ("amount", "mean"),
            first_txn = ("date",   "min"),
            last_txn  = ("date",   "max"),
            name      = ("donor_name", "first"),
        ).nlargest(10, "total").reset_index()

        top_donors["total"]     = top_donors["total"].apply(fmt)
        top_donors["avg_gift"]  = top_donors["avg_gift"].apply(fmt)
        top_donors["first_txn"] = top_donors["first_txn"].dt.strftime("%Y-%m-%d")
        top_donors["last_txn"]  = top_donors["last_txn"].dt.strftime("%Y-%m-%d")

        st.dataframe(
            top_donors[["name","total","txns","avg_gift","first_txn","last_txn"]].rename(columns={
                "name": "Donor", "total": "Total Given", "txns": "Transactions",
                "avg_gift": "Avg Gift", "first_txn": "First Donation", "last_txn": "Last Donation"
            }),
            use_container_width=True, hide_index=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — RECURRING ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Recurring Analysis":
    df_all = df_full
    df_rec_base = df_all[df_all["is_recurring"]].copy()

    if df_rec_base.empty:
        st.error("No recurring donations found in this file."); st.stop()

    with st.sidebar:
        st.divider()
        st.markdown('<p class="side-label">Filters</p>', unsafe_allow_html=True)
        years_avail = sorted(df_rec_base["year"].unique())
        sel_years   = st.multiselect("Year:", years_avail, default=years_avail)

        if "platform" in df_rec_base.columns:
            all_platforms = sorted(df_rec_base["platform"].fillna("(unknown)").unique())
            sel_platforms = st.multiselect("Payment Platform:", all_platforms, default=all_platforms)
        else:
            sel_platforms = None

        if "source" in df_rec_base.columns:
            all_sources = sorted(df_rec_base["source"].fillna("(no source)").unique())
            sel_sources = st.multiselect("Source:", all_sources, default=all_sources)
        else:
            sel_sources = None

        all_desigs  = sorted(df_rec_base["designation_label"].unique())
        sel_desigs  = st.multiselect("Designation:", all_desigs, default=all_desigs)

    # apply filters
    df = df_rec_base[df_rec_base["year"].isin(sel_years)].copy()
    if sel_platforms:
        df = df[df["platform"].fillna("(unknown)").isin(sel_platforms)]
    if sel_sources:
        df = df[df["source"].fillna("(no source)").isin(sel_sources)]
    df = df[df["designation_label"].isin(sel_desigs)]

    if df.empty:
        st.warning("No data after applying filters."); st.stop()

    all_months  = sorted(df["month_key"].unique())
    all_m_str   = [str(m) for m in all_months]
    render_page_header(
        "Recurring analysis",
        "Recurring donations",
        "MRR growth, active subscribers, retention, churn, cohort behavior, lifetime value, and recurring gift composition.",
        [
            f"{df['donor_key'].nunique():,} recurring donors",
            f"{len(df):,} transactions",
            f"{all_m_str[0]} to {all_m_str[-1]}",
            f"{fmt(df['amount'].sum())} recurring revenue",
        ],
    )

    # monthly snapshots (on full recurring data for accuracy)
    df_rec_full = df_all[df_all["is_recurring"]].copy()
    all_m_full  = sorted(df_rec_full["month_key"].unique())
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    monthly_snap = []
    for i, m in enumerate(all_m_full):
        d_cur  = set(df_rec_full[df_rec_full["month_key"] == m]["donor_key"])
        d_prev = set(df_rec_full[df_rec_full["month_key"] == (m-1)]["donor_key"]) if i > 0 else set()
        mrr_val = df_rec_full[df_rec_full["month_key"] == m]["amount"].sum()
        avg_val = df_rec_full[df_rec_full["month_key"] == m]["amount"].mean() if d_cur else 0
        med_val = df_rec_full[df_rec_full["month_key"] == m]["amount"].median() if d_cur else 0
        ret     = len(d_cur & d_prev) / len(d_prev) * 100 if d_prev else None
        churn_n = len(d_prev - d_cur)
        monthly_snap.append({
            "month_key":   m,
            "month_str":   str(m),
            "year":        m.year,
            "month_num":   m.month,
            "month_label": pd.Period(m, "M").strftime("%b"),
            "active":      len(d_cur),
            "new":         len(d_cur - d_prev),
            "churned":     churn_n,
            "mrr":         mrr_val,
            "avg_gift":    avg_val,
            "median_gift": med_val,
            "retention":   ret,
            "churn_rate":  (churn_n / len(d_prev) * 100) if d_prev else None,
        })

    snap   = pd.DataFrame(monthly_snap)
    snap_f = snap[snap["year"].isin(sel_years)]

    t1,t2,t3,t4,t5,t6,t7,t8 = st.tabs([
        "MRR & Metrics",
        "Retention & Churn",
        "New vs. Churned",
        "Cohort Table",
        "LTV",
        "Gift Distribution",
        "Designations & Channels",
        "Top Donors",
    ])

    # ── TAB 1 — MRR & METRICS ────────────────────────────────────
    with t1:
        st.subheader("MRR & Key Metrics")
        latest_m   = snap_f.iloc[-1]
        prev_m_row = snap_f.iloc[-2] if len(snap_f) > 1 else None

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("Latest MRR",          fmt(latest_m["mrr"]),
                  delta=pct_delta(latest_m["mrr"], prev_m_row["mrr"]) if prev_m_row is not None else None)
        c2.metric("Active Subscribers",  f"{int(latest_m['active']):,}",
                  delta=pct_delta(latest_m["active"], prev_m_row["active"]) if prev_m_row is not None else None)
        c3.metric("Avg Monthly Gift",    fmt(latest_m["avg_gift"]))
        c4.metric("Median Monthly Gift", fmt(latest_m["median_gift"]))
        c5.metric("Cumulative MRR",      fmt(snap_f["mrr"].sum()))
        c6.metric("Avg Active / Month",  f"{snap_f['active'].mean():.0f}")

        st.divider()
        st.subheader("MRR Over Time")
        mrr_bar = alt.Chart(snap_f).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("month_str:O", sort=list(snap_f["month_str"]), title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("mrr:Q", title="USD", axis=alt.Axis(format="$,.0f")),
            color=alt.Color("year:O", scale=alt.Scale(range=CAT), title="Year"),
            tooltip=["month_str:O", alt.Tooltip("mrr:Q", format="$,.0f"), alt.Tooltip("active:Q", title="Active")]
        ).properties(height=300)
        st.altair_chart(mrr_bar, use_container_width=True)

        st.divider()
        st.subheader("MRR — Year-over-Year by Month")
        yoy_mrr = alt.Chart(snap).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X("month_label:O", sort=month_order, title="", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("mrr:Q", title="USD", axis=alt.Axis(format="$,.0f")),
            color=alt.Color("year:O", scale=alt.Scale(range=CAT), title="Year"),
            tooltip=["year:O","month_label:O", alt.Tooltip("mrr:Q", format="$,.0f")]
        ).properties(height=300)
        st.altair_chart(yoy_mrr, use_container_width=True)

        st.divider()
        st.subheader("Active Subscribers Over Time")
        sub_line = alt.Chart(snap_f).mark_line(point=True, strokeWidth=2, color=BRAND).encode(
            x=alt.X("month_str:O", sort=list(snap_f["month_str"]), title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("active:Q", title="Active Subscribers"),
            tooltip=["month_str:O","active:Q"]
        ).properties(height=260)
        st.altair_chart(sub_line, use_container_width=True)

        st.divider()
        st.subheader("Avg & Median Gift Over Time")
        gift_m = snap_f.melt(id_vars="month_str", value_vars=["avg_gift","median_gift"], var_name="Metric", value_name="USD")
        gift_m["Metric"] = gift_m["Metric"].map({"avg_gift":"Average","median_gift":"Median"})
        gift_line = alt.Chart(gift_m).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X("month_str:O", sort=list(snap_f["month_str"]), title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("USD:Q", title="USD", axis=alt.Axis(format="$,.0f")),
            color=alt.Color("Metric:N", scale=alt.Scale(range=[BRAND, GOLD])),
            tooltip=["month_str:O","Metric:N", alt.Tooltip("USD:Q", format="$,.2f")]
        ).properties(height=260)
        st.altair_chart(gift_line, use_container_width=True)

    # ── TAB 2 — RETENTION & CHURN ────────────────────────────────
    with t2:
        st.subheader("Retention & Churn Rate")
        snap_ret = snap_f.dropna(subset=["retention"])
        avg_ret   = snap_ret["retention"].mean()
        avg_churn = snap_ret["churn_rate"].mean()
        best_ret  = snap_ret.loc[snap_ret["retention"].idxmax()]
        worst_ret = snap_ret.loc[snap_ret["retention"].idxmin()]

        r1,r2,r3,r4 = st.columns(4)
        r1.metric("Avg Monthly Retention", f"{avg_ret:.1f}%")
        r2.metric("Avg Monthly Churn",     f"{avg_churn:.1f}%")
        r3.metric("Best Month",  best_ret["month_str"],  help=f"{best_ret['retention']:.1f}% retention")
        r4.metric("Worst Month", worst_ret["month_str"], help=f"{worst_ret['retention']:.1f}% retention")

        st.divider()
        st.subheader("Monthly Retention Rate")
        ret_line = alt.Chart(snap_ret).mark_line(point=True, strokeWidth=2, color=GOOD).encode(
            x=alt.X("month_str:O", sort=list(snap_f["month_str"]), title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("retention:Q", title="Retention %", scale=alt.Scale(domain=[0,100])),
            tooltip=["month_str:O", alt.Tooltip("retention:Q", format=".1f", title="Retention %")]
        ).properties(height=280)
        ref_line = alt.Chart(pd.DataFrame({"y":[80]})).mark_rule(color=NEG, strokeDash=[6,3], strokeWidth=1.5).encode(y="y:Q")
        st.altair_chart(ret_line + ref_line, use_container_width=True)
        st.caption("Red dashed line = 80% retention benchmark.")

        st.divider()
        st.subheader("Monthly Churn Rate")
        churn_bar = alt.Chart(snap_ret).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("month_str:O", sort=list(snap_f["month_str"]), title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("churn_rate:Q", title="Churn %"),
            color=alt.condition(alt.datum.churn_rate > 20, alt.value(NEG), alt.value(GOLD)),
            tooltip=["month_str:O", alt.Tooltip("churn_rate:Q", format=".1f"), alt.Tooltip("churned:Q", title="Donors churned")]
        ).properties(height=260)
        st.altair_chart(churn_bar, use_container_width=True)
        st.caption("Red = churn > 20%.")

        st.divider()
        st.subheader("Retention — Year-over-Year by Month")
        snap_ret2 = snap.dropna(subset=["retention"])
        yoy_ret = alt.Chart(snap_ret2).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X("month_label:O", sort=month_order, title="", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("retention:Q", title="Retention %", scale=alt.Scale(domain=[0,100])),
            color=alt.Color("year:O", scale=alt.Scale(range=CAT), title="Year"),
            tooltip=["year:O","month_label:O", alt.Tooltip("retention:Q", format=".1f")]
        ).properties(height=280)
        st.altair_chart(yoy_ret, use_container_width=True)

        st.divider()
        st.subheader("Monthly Detail Table")
        tbl = snap_ret[["month_str","active","new","churned","retention","churn_rate","mrr"]].copy()
        tbl["retention"]  = tbl["retention"].apply(lambda x: f"{x:.1f}%")
        tbl["churn_rate"] = tbl["churn_rate"].apply(lambda x: f"{x:.1f}%")
        tbl["mrr"]        = tbl["mrr"].apply(fmt)
        tbl.columns       = ["Month","Active","New","Churned","Retention","Churn Rate","MRR"]
        st.dataframe(tbl, use_container_width=True, hide_index=True)

    # ── TAB 3 — NEW VS CHURNED ───────────────────────────────────
    with t3:
        st.subheader("New vs. Churned Subscribers per Month")
        snap_nc = snap_f.copy()
        snap_nc["churned_neg"] = -snap_nc["churned"]
        pos = snap_nc[["month_str","new"]].rename(columns={"new":"count"}); pos["Type"] = "New"
        neg = snap_nc[["month_str","churned_neg"]].rename(columns={"churned_neg":"count"}); neg["Type"] = "Churned"
        nc_long = pd.concat([pos, neg])
        nc_bar = alt.Chart(nc_long).mark_bar().encode(
            x=alt.X("month_str:O", sort=list(snap_f["month_str"]), title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("count:Q", title="Subscribers", axis=alt.Axis(labelExpr="abs(datum.value)")),
            color=alt.Color("Type:N", scale=alt.Scale(domain=["New","Churned"], range=[GOOD, NEG])),
            tooltip=["month_str:O","Type:N","count:Q"]
        ).properties(height=300)
        zero_line = alt.Chart(pd.DataFrame({"y":[0]})).mark_rule(color=MUTED, strokeWidth=1).encode(y="y:Q")
        st.altair_chart(nc_bar + zero_line, use_container_width=True)
        st.caption("Green = new subscribers. Red = churned. Net growth = green − red.")

        st.divider()
        snap_nc["net"] = snap_nc["new"] - snap_nc["churned"]
        st.subheader("Net Subscriber Growth per Month")
        net_bar = alt.Chart(snap_nc).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("month_str:O", sort=list(snap_f["month_str"]), title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("net:Q", title="Net change"),
            color=alt.condition(alt.datum.net >= 0, alt.value(GOOD), alt.value(NEG)),
            tooltip=["month_str:O", alt.Tooltip("net:Q", title="Net growth"), "new:Q","churned:Q"]
        ).properties(height=240)
        st.altair_chart(net_bar, use_container_width=True)

        st.divider()
        st.subheader("New Subscribers — Year-over-Year by Month")
        yoy_new = alt.Chart(snap).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X("month_label:O", sort=month_order, title="", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("new:Q", title="New Subscribers"),
            color=alt.Color("year:O", scale=alt.Scale(range=CAT), title="Year"),
            tooltip=["year:O","month_label:O","new:Q"]
        ).properties(height=260)
        st.altair_chart(yoy_new, use_container_width=True)

        st.divider()
        n1,n2,n3 = st.columns(3)
        n1.metric("Total New Subscribers", f"{int(snap_f['new'].sum()):,}")
        n2.metric("Total Churned",         f"{int(snap_f['churned'].sum()):,}")
        n3.metric("Net Growth",            f"{int(snap_f['new'].sum() - snap_f['churned'].sum()):+,}")

    # ── TAB 4 — COHORT TABLE ─────────────────────────────────────
    with t4:
        st.subheader("Cohort Retention Table")
        st.caption("Each row = cohort month of first subscription. Each column = months since start. Value = % of cohort still active.")

        df_cohort = df_all[df_all["is_recurring"]].copy()
        df_cohort["cohort_month"] = df_cohort.groupby("donor_key")["month_key"].transform("min")
        cohort_sizes = df_cohort.groupby("cohort_month")["donor_key"].nunique().rename("cohort_size")
        df_cohort = df_cohort.join(cohort_sizes, on="cohort_month")
        df_cohort["period_num"] = (
            df_cohort["month_key"].apply(lambda x: x.ordinal) -
            df_cohort["cohort_month"].apply(lambda x: x.ordinal)
        )
        cohort_pivot = df_cohort.groupby(["cohort_month","period_num"])["donor_key"].nunique().reset_index()
        cohort_pivot = cohort_pivot.join(cohort_sizes, on="cohort_month")
        cohort_pivot["pct"] = cohort_pivot["donor_key"] / cohort_pivot["cohort_size"] * 100
        cohort_table = cohort_pivot.pivot(index="cohort_month", columns="period_num", values="pct")
        cohort_table.index = cohort_table.index.astype(str)
        max_cols = min(24, cohort_table.shape[1])
        cohort_table = cohort_table.iloc[:, :max_cols]
        cohort_table.columns = [f"M+{c}" for c in cohort_table.columns]
        cohort_table = cohort_table[cohort_table.index.str[:4].astype(int).isin(sel_years)]

        def style_cohort(val):
            if pd.isna(val): return "background-color: #F3F6FB; color: #C2C9D6;"
            if val >= 90:    return "background-color: #0F2A52; color: #EAF0FB;"
            if val >= 75:    return "background-color: #1B4DB1; color: #FFFFFF;"
            if val >= 60:    return "background-color: #5B8BE0; color: #FFFFFF;"
            if val >= 40:    return "background-color: #AFC9EE; color: #0F2A52;"
            return                  "background-color: #F6E2DC; color: #B23A36;"

        styled = cohort_table.style.map(style_cohort).format(
            lambda v: f"{v:.0f}%" if not pd.isna(v) else ""
        )
        st.dataframe(styled, use_container_width=True)
        st.caption("Deeper blue = stronger retention · warm = below 40% · blank = no data.")

        st.divider()
        st.subheader("Cohort Size at Start")
        cs = cohort_sizes.reset_index()
        cs["cohort_str"] = cs["cohort_month"].astype(str)
        cs = cs[cs["cohort_str"].str[:4].astype(int).isin(sel_years)]
        cs_bar = alt.Chart(cs).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("cohort_str:O", title="Cohort Month", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("cohort_size:Q", title="Donors in Cohort"),
            tooltip=["cohort_str:O","cohort_size:Q"]
        ).properties(height=240)
        st.altair_chart(cs_bar, use_container_width=True)

    # ── TAB 5 — LTV ──────────────────────────────────────────────
    with t5:
        st.subheader("Lifetime Value (LTV) Estimates")
        ltv_df = df.groupby(["donor_key","donor_name","cohort_month","cohort_year"]).agg(
            total_paid    = ("amount","sum"),
            months_active = ("month_key","nunique"),
            avg_gift      = ("amount","mean"),
        ).reset_index()

        l1,l2,l3,l4 = st.columns(4)
        l1.metric("Avg LTV per Donor",    fmt(ltv_df["total_paid"].mean()))
        l2.metric("Median LTV per Donor", fmt(ltv_df["total_paid"].median()))
        l3.metric("Avg Active Lifespan",  f"{ltv_df['months_active'].mean():.1f} months")
        l4.metric("Total Unique Donors",  f"{len(ltv_df):,}")

        st.divider()
        BRACKETS = [0,100,250,500,1000,2500,5000,float("inf")]
        LABELS   = ["$0–100","$100–250","$250–500","$500–1k","$1k–2.5k","$2.5k–5k","$5k+"]
        ltv_df["ltv_bracket"] = pd.cut(ltv_df["total_paid"], bins=BRACKETS, labels=LABELS, right=False)
        ltv_dist = ltv_df.groupby("ltv_bracket", observed=True).size().reset_index(name="Donors")
        ltv_bar = alt.Chart(ltv_dist).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("ltv_bracket:O", sort=LABELS, title="LTV Bracket", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Donors:Q"),
            tooltip=["ltv_bracket:O","Donors:Q"]
        ).properties(height=260)
        st.altair_chart(ltv_bar + ltv_bar.mark_text(dy=-8, fontSize=10).encode(text="Donors:Q"), use_container_width=True)

        st.divider()
        st.subheader("Avg LTV by Cohort Year")
        ltv_by_year = ltv_df.groupby("cohort_year").agg(
            avg_ltv    = ("total_paid","mean"),
            median_ltv = ("total_paid","median"),
            donors     = ("donor_key","nunique"),
        ).reset_index().sort_values("cohort_year")
        ly_bar = alt.Chart(ltv_by_year).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("cohort_year:O", title="Cohort Year"),
            y=alt.Y("avg_ltv:Q", title="Avg LTV (USD)", axis=alt.Axis(format="$,.0f")),
            color=alt.Color("cohort_year:O", scale=alt.Scale(range=CAT), legend=None),
            tooltip=["cohort_year:O",
                     alt.Tooltip("avg_ltv:Q", format="$,.0f", title="Avg LTV"),
                     alt.Tooltip("median_ltv:Q", format="$,.0f", title="Median LTV"),
                     "donors:Q"]
        ).properties(height=260)
        st.altair_chart(
            ly_bar + ly_bar.mark_text(dy=-8, fontSize=10).encode(text=alt.Text("avg_ltv:Q", format="$,.0f")),
            use_container_width=True
        )

        st.divider()
        st.subheader("Top 10 Donors by LTV")
        top10 = ltv_df.nlargest(10, "total_paid")[["donor_name","cohort_year","total_paid","months_active","avg_gift"]].copy()
        top10["total_paid"] = top10["total_paid"].apply(fmt)
        top10["avg_gift"]   = top10["avg_gift"].apply(fmt)
        top10.columns = ["Donor","Cohort Year","Total Paid","Months Active","Avg Gift"]
        st.dataframe(top10, use_container_width=True, hide_index=True)

    # ── TAB 6 — GIFT DISTRIBUTION ────────────────────────────────
    with t6:
        st.subheader("Gift Size Distribution")
        BRACKETS = [0,25,50,100,250,500,1000,float("inf")]
        LABELS   = ["$0–25","$25–50","$50–100","$100–250","$250–500","$500–1k","$1k+"]
        df["bracket"] = pd.cut(df["amount"], bins=BRACKETS, labels=LABELS, right=False)

        g1,g2 = st.columns(2)
        with g1:
            st.caption("By number of transactions")
            dist_txn = df.groupby("bracket", observed=True).size().reset_index(name="Transactions")
            b_txn = alt.Chart(dist_txn).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X("bracket:O", sort=LABELS, title="", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("Transactions:Q"),
                tooltip=["bracket:O","Transactions:Q"]
            ).properties(height=280)
            st.altair_chart(b_txn + b_txn.mark_text(dy=-8, fontSize=9).encode(text="Transactions:Q"), use_container_width=True)
        with g2:
            st.caption("By unique donors")
            dist_don = df.groupby("bracket", observed=True)["donor_key"].nunique().reset_index(name="Donors")
            b_don = alt.Chart(dist_don).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X("bracket:O", sort=LABELS, title="", axis=alt.Axis(labelAngle=-45)),
                y=alt.Y("Donors:Q"),
                tooltip=["bracket:O","Donors:Q"]
            ).properties(height=280)
            st.altair_chart(b_don + b_don.mark_text(dy=-8, fontSize=9).encode(text="Donors:Q"), use_container_width=True)

        st.divider()
        st.subheader("Gift Size — Year-over-Year Distribution")
        dist_yoy = df.groupby(["year","bracket"], observed=True).size().reset_index(name="Transactions")
        dist_yoy["year"] = dist_yoy["year"].astype(str)
        dist_yoy_bar = alt.Chart(dist_yoy).mark_bar().encode(
            x=alt.X("bracket:O", sort=LABELS, title="", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("Transactions:Q"),
            color=alt.Color("year:N", scale=alt.Scale(range=CAT), title="Year"),
            xOffset="year:N",
            tooltip=["year:N","bracket:O","Transactions:Q"]
        ).properties(height=280)
        st.altair_chart(dist_yoy_bar, use_container_width=True)

    # ── TAB 7 — DESIGNATIONS & CHANNELS ─────────────────────────
    with t7:
        st.subheader("Revenue by Designation")
        desig = df.groupby("designation_label").agg(
            revenue  = ("amount","sum"),
            donors   = ("donor_key","nunique"),
            txns     = ("amount","count"),
            avg_gift = ("amount","mean"),
        ).sort_values("revenue", ascending=False).reset_index()
        total_rev = desig["revenue"].sum()
        desig["% Rev"] = (desig["revenue"] / total_rev * 100).apply(lambda x: f"{x:.1f}%")
        if len(desig):
            top3_pct = desig.head(3)["revenue"].sum() / total_rev * 100
            st.info(f"Top designation: **{desig.iloc[0]['designation_label']}** at {desig.iloc[0]['% Rev']}. The top 3 make up {top3_pct:.0f}% of recurring revenue.")
        desig_display = desig.copy()
        desig_display["revenue"]  = desig_display["revenue"].apply(fmt)
        desig_display["avg_gift"] = desig_display["avg_gift"].apply(fmt)
        st.dataframe(
            desig_display[["designation_label","revenue","% Rev","donors","txns","avg_gift"]].rename(columns={
                "designation_label":"Designation","revenue":"Revenue","donors":"Donors","txns":"Txns","avg_gift":"Avg Gift"
            }),
            use_container_width=True, hide_index=True
        )

        st.divider()
        st.subheader("Revenue by Payment Platform")
        if "platform" in df.columns:
            plat = df.groupby(df["platform"].fillna("(unknown)")).agg(
                revenue=("amount","sum"), donors=("donor_key","nunique"), txns=("amount","count"),
            ).sort_values("revenue", ascending=False).reset_index()
            plat["% Rev"]   = (plat["revenue"] / plat["revenue"].sum() * 100).apply(lambda x: f"{x:.1f}%")
            plat["revenue"] = plat["revenue"].apply(fmt)
            st.dataframe(
                plat[["platform","revenue","% Rev","donors","txns"]].rename(columns={
                    "platform":"Platform","revenue":"Revenue","donors":"Donors","txns":"Txns"
                }),
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No payment platform column found.")

        st.divider()
        st.subheader("Revenue by Source / Channel")
        if "source" in df.columns:
            ch = df.groupby(df["source"].fillna("(no source)")).agg(
                revenue=("amount","sum"), donors=("donor_key","nunique"), txns=("amount","count"),
            ).sort_values("revenue", ascending=False).reset_index()
            ch["% Rev"]   = (ch["revenue"] / ch["revenue"].sum() * 100).apply(lambda x: f"{x:.1f}%")
            ch["revenue"] = ch["revenue"].apply(fmt)
            st.dataframe(
                ch[["source","revenue","% Rev","donors","txns"]].rename(columns={
                    "source":"Channel","revenue":"Revenue","donors":"Donors","txns":"Txns"
                }),
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No source column found.")

    # ── TAB 8 — TOP DONORS BY COHORT ────────────────────────────
    with t8:
        st.subheader("Top Donors by Cohort")
        cohort_months_avail = sorted(df["cohort_month"].dropna().unique())
        cohort_labels = [str(c) for c in cohort_months_avail]

        col_a, col_b = st.columns([2,1])
        with col_a:
            sel_cohort_label = st.selectbox("Select cohort:", cohort_labels, index=len(cohort_labels)-1)
        with col_b:
            top_n = st.number_input("Show top N donors:", min_value=5, max_value=50, value=10, step=5)

        sel_cohort = cohort_months_avail[cohort_labels.index(sel_cohort_label)]

        agg_dict = {
            "total_paid":    ("amount","sum"),
            "months_active": ("month_key","nunique"),
            "avg_gift":      ("amount","mean"),
            "first_txn":     ("date","min"),
            "last_txn":      ("date","max"),
            "designation":   ("designation_label", lambda x: x.mode()[0] if len(x) else "—"),
        }
        if "platform" in df.columns:
            agg_dict["platform"] = ("platform", lambda x: x.mode()[0] if len(x) else "—")

        cohort_donors = df[df["cohort_month"] == sel_cohort].groupby(
            ["donor_key","donor_name"]
        ).agg(**agg_dict).reset_index().sort_values("total_paid", ascending=False).head(top_n)

        cohort_size    = df[df["cohort_month"] == sel_cohort]["donor_key"].nunique()
        cohort_rev     = df[df["cohort_month"] == sel_cohort]["amount"].sum()
        cohort_avg_ltv = cohort_donors["total_paid"].mean() if len(cohort_donors) else 0

        ca,cb,cc = st.columns(3)
        ca.metric("Cohort Size",       f"{cohort_size:,} donors")
        cb.metric("Total Revenue",     fmt(cohort_rev))
        cc.metric("Avg LTV in Cohort", fmt(cohort_avg_ltv))

        bar_top = alt.Chart(cohort_donors).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("total_paid:Q", title="Total Paid (USD)", axis=alt.Axis(format="$,.0f")),
            y=alt.Y("donor_name:O", sort="-x", title=""),
            color=alt.Color("designation:N", scale=alt.Scale(range=CAT), title="Designation"),
            tooltip=["donor_name:O", alt.Tooltip("total_paid:Q", format="$,.0f"),
                     "months_active:Q", alt.Tooltip("avg_gift:Q", format="$,.0f")]
        ).properties(height=max(250, top_n * 28))
        st.altair_chart(bar_top, use_container_width=True)

        cohort_display = cohort_donors.copy()
        cohort_display["total_paid"] = cohort_display["total_paid"].apply(fmt)
        cohort_display["avg_gift"]   = cohort_display["avg_gift"].apply(fmt)
        cohort_display["first_txn"]  = cohort_display["first_txn"].dt.strftime("%Y-%m-%d")
        cohort_display["last_txn"]   = cohort_display["last_txn"].dt.strftime("%Y-%m-%d")
        display_cols = ["donor_name","total_paid","months_active","avg_gift","first_txn","last_txn","designation"]
        if "platform" in cohort_display.columns:
            display_cols.append("platform")
        col_rename = {
            "donor_name":"Donor","total_paid":"Total Paid","months_active":"Months Active",
            "avg_gift":"Avg Gift","first_txn":"First Txn","last_txn":"Last Txn",
            "designation":"Top Designation","platform":"Platform"
        }
        st.dataframe(cohort_display[display_cols].rename(columns=col_rename), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("All Cohorts — Top Donor Summary")
        top_per_cohort = df.groupby(["cohort_month","donor_key","donor_name"]).agg(
            total_paid=("amount","sum"), months_active=("month_key","nunique"),
        ).reset_index()
        top_per_cohort = top_per_cohort.sort_values("total_paid", ascending=False)\
                                       .groupby("cohort_month").first().reset_index()
        top_per_cohort["cohort_str"]      = top_per_cohort["cohort_month"].astype(str)
        top_per_cohort["total_paid_fmt"]  = top_per_cohort["total_paid"].apply(fmt)
        top_per_cohort = top_per_cohort.sort_values("cohort_month")
        st.dataframe(
            top_per_cohort[["cohort_str","donor_name","total_paid_fmt","months_active"]].rename(columns={
                "cohort_str":"Cohort","donor_name":"Top Donor",
                "total_paid_fmt":"Total Paid","months_active":"Months Active"
            }),
            use_container_width=True, hide_index=True
        )
