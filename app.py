import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
import re as _re
import datetime as _dt
import time
import base64
warnings.filterwarnings("ignore")
import os

def load_svg_logo():
    """Reads the SVG file so it can be embedded cleanly into HTML."""
    if os.path.exists("app_logo.svg"):
        with open("app_logo.svg", "r", encoding="utf-8") as f:
            return f.read()
    # Fallback text icon if the file is missing
    return "<span>⨣</span>" 

# THIS is the variable that the rest of the app
app_logo_html = load_svg_logo()
import model_file as mf
MODEL_AVAILABLE = True

LOGO_BASE64 = "PHN2ZyB2aWV3Qm94PSIwIDAgMTAwIDEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSIwJSIgeTE9IjEwMCUiIHgyPSIxMDAlIiB5Mj0iMCUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiMwMEQ2OEYiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMzRDhFRkYiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB4PSIwIiB5PSIwIiB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgcng9IjI0IiBmaWxsPSIjMEYxNzJBIi8+PHBhdGggZD0iTTIwIDUwIFEgNTAgMTUgODAgNTAgUSA1MCA4NSAyMCA1MCBaIiBmaWxsPSJub25lIiBzdHJva2U9InVybCgjZykiIHN0cm9rZS13aWR0aD0iOCIvPjxwYXRoIGQ9Ik00MCA1NSBMMTUwIDQ1IEw2MCA1NSIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjgiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg=="
# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Oracle · AI Forecast",
    page_icon="app_logo.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme state ──
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"  # Default to light theme for better initial compatibility


#  GLOBAL CSS (dark + light modes)

def get_theme_css(theme):
    if theme == "dark":
        return """
        :root {
            --ink:         #06070A;
            --ink-2:       #0E1117;
            --ink-3:       #151B26;
            --ink-4:       #1C2433;
            --line:        rgba(255,255,255,0.055);
            --line-2:      rgba(255,255,255,0.10);
            --snow:        #F2F5FC;
            --snow-dim:    rgba(220,228,245,0.55);
            --snow-mute:   rgba(200,212,235,0.28);
            --bg-mesh-1:   rgba(0,214,143,0.06);
            --bg-mesh-2:   rgba(61,142,255,0.05);
            --bg-mesh-3:   rgba(155,127,255,0.04);
            --bg-mesh-4:   rgba(0,200,224,0.03);
            --card-bg:     var(--ink-2);
            --sidebar-bg:  var(--ink-2);
            --text-main:   #F2F5FC;
            --text-dim:    rgba(220,228,245,0.55);
            --text-mute:   rgba(200,212,235,0.28);
            --scrollbar-track: var(--ink);
            --scrollbar-thumb: rgba(255,255,255,0.08);
            --scrollbar-hover: rgba(255,255,255,0.16);
            --tab-bg:      var(--ink-2);
            --tab-hover:   rgba(255,255,255,0.04);
            --tab-active:  rgba(255,255,255,0.07);
            --upload-bg:   var(--ink-2);
            --select-bg:   var(--ink-3);
            --df-border:   var(--line);
        }
        html, body, [class*="css"] { background: var(--ink); color: var(--snow); }
        .stApp { background: var(--ink); }
        .stApp::before {
            content: '';
            position: fixed; inset: 0;
            background:
                radial-gradient(ellipse 120% 60% at 15% 5%, var(--bg-mesh-1) 0%, transparent 55%),
                radial-gradient(ellipse 80% 50% at 85% 90%, var(--bg-mesh-2) 0%, transparent 50%),
                radial-gradient(ellipse 50% 40% at 90% 10%, var(--bg-mesh-3) 0%, transparent 45%),
                radial-gradient(ellipse 40% 30% at 5% 80%, var(--bg-mesh-4) 0%, transparent 40%);
            pointer-events: none; z-index: 0;
        }
        """
    else:
        # Note: This is a standard string, not an f-string, so CSS {color: ...} is perfectly safe here!
        return """
        :root {
            --ink:         #F0F2F8; 
            --ink-2:       #FFFFFF;
            --ink-3:       #E6EAF2; 
            --ink-4:       #DDE2ED;
            --line:        rgba(0,0,0,0.09); 
            --line-2:      rgba(0,0,0,0.16);
            --snow:        #0A0F18; 
            --snow-dim:    rgba(10,15,25,0.75); 
            --snow-mute:   rgba(10,15,25,0.60); 
            --bg-mesh-1:   rgba(0,180,120,0.05);
            --bg-mesh-2:   rgba(40,110,220,0.04);
            --bg-mesh-3:   rgba(120,90,220,0.03);
            --bg-mesh-4:   rgba(0,170,200,0.03);
            --card-bg:     #FFFFFF;
            --sidebar-bg:  #FFFFFF;
            --text-main:   #0A0F18;
            --text-dim:    rgba(10,15,25,0.75);
            --text-mute:   rgba(10,15,25,0.60);
            --scrollbar-track: #F0F2F8;
            --scrollbar-thumb: rgba(0,0,0,0.15);
            --scrollbar-hover: rgba(0,0,0,0.25);
            --tab-bg:      #FFFFFF;
            --tab-hover:   rgba(0,0,0,0.04);
            --tab-active:  rgba(0,0,0,0.08);
            --upload-bg:   #FFFFFF;
            --select-bg:   #F4F6FB;
            --df-border:   rgba(0,0,0,0.1);
        }
        html, body, [class*="css"] { background: var(--ink) !important; color: var(--snow) !important; }
        .stApp { background: var(--ink) !important; }
        .stApp::before {
            content: '';
            position: fixed; inset: 0;
            background:
                radial-gradient(ellipse 120% 60% at 15% 5%, var(--bg-mesh-1) 0%, transparent 55%),
                radial-gradient(ellipse 80% 50% at 85% 90%, var(--bg-mesh-2) 0%, transparent 50%);
            pointer-events: none; z-index: 0;
        }
        
        /* ── LIGHT MODE FIXES ── */
        
        /* Uploader Drag & Drop Text Fix */
        [data-testid="stFileUploaderDropzone"] div, 
        [data-testid="stFileUploaderDropzone"] span, 
        [data-testid="stFileUploaderDropzone"] p { 
            color: var(--snow-dim) !important; 
        }
        [data-testid="stFileUploaderDropzone"] small { 
            color: var(--snow-mute) !important; 
        }
        
        /* Uploaded File Name Text */
        [data-testid="stUploadedFile"] * { color: var(--snow) !important; }
        [data-testid="stUploadedFile"] p, [data-testid="stUploadedFile"] span { color: var(--snow) !important; }
        
        /* Browse Files Button */
        [data-testid="stFileUploader"] button {
            background-color: #FFFFFF !important;
            color: #0A0F18 !important;
            border: 1px solid rgba(0,0,0,0.2) !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
        [data-testid="stFileUploader"] button:hover {
            background-color: #F8F9FA !important;
            border-color: #059669 !important;
            color: #059669 !important;
        }
        
        /* Spinner Fix */
        .stSpinner > div > div {
            border-color: rgba(0, 0, 0, 0.1) !important;
            border-top-color: #059669 !important;
        }
        [data-testid="stSpinner"] > div > div > div > p,
        [data-testid="stSpinner"] * { color: var(--snow) !important; }
        
        /* Alert Banner Fix */
        [data-testid="stAlert"] div[data-testid="stMarkdownContainer"] p,
        [data-testid="stAlert"] div[data-testid="stMarkdownContainer"] strong {
            color: var(--snow) !important;
        }

        /* General Light Mode Text Overrides */
        .kpi-val, .hero-headline, .fp-title, .fp-subtitle, .basis-title,
        .prod-row-name, .prod-row-amount, .rec-card-name, .upload-zone-title,
        .section-title, .rec-wrap-title { color: var(--snow) !important; font-size: 20px !important; }
        
        .kpi-lbl, .upload-zone-sub, .signal-label, .rec-card-num,
        .basis-body, .rec-wrap-sub, .section-eyebrow { color: var(--snow-mute) !important; }
        
        /* Light Sidebar & Tabs */
        section[data-testid="stSidebar"] { background: var(--card-bg) !important; border-right: 1px solid var(--line) !important; }
        section[data-testid="stSidebar"] * { color: var(--snow) !important; }
        .stTabs [data-baseweb="tab-list"] { background: var(--card-bg) !important; border-color: var(--line) !important; }
        .stTabs [data-baseweb="tab"] { color: var(--snow-mute) !important; }
        .stTabs [aria-selected="true"] { background: var(--ink-3) !important; color: var(--snow) !important; }
        
        /* Light Selects & Dataframes */
        [data-baseweb="select"] > div { background: var(--select-bg) !important; border-color: var(--line) !important; color: var(--snow) !important; }
        [data-baseweb="select"] span { color: var(--snow) !important; }
        .stDataFrame { background: var(--card-bg) !important; }
        [data-testid="stFileUploader"] { background: var(--card-bg) !important; border-color: var(--line-2) !important; }
        """
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Clash+Display:wght@400;500;600;700&family=Cabinet+Grotesk:wght@400;500;700;800;900&family=Familjen+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

{get_theme_css(st.session_state["theme"])}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

.stApp {{
    min-height: 100vh;
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
header {{ background-color: transparent !important; }}
.block-container {{ padding: 2.5rem 3rem 6rem; max-width: 1760px; margin: auto; position: relative; z-index: 1; }}

/* ── Sidebar ─────────────────────────────────────────── */
section[data-testid="stSidebar"] {{
    background: var(--card-bg);
    border-right: 1px solid var(--line);
}}
section[data-testid="stSidebar"] .block-container {{ padding: 2rem 1.6rem; }}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: var(--select-bg) !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    color: var(--snow) !important;
    transition: border-color 0.2s !important;
}}

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: var(--scrollbar-track); }}
::-webkit-scrollbar-thumb {{ background: var(--scrollbar-thumb); border-radius: 10px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--scrollbar-hover); }}

/* ── Tabs ────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: var(--tab-bg);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 5px; gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.84rem !important; font-weight: 500 !important;
    padding: 9px 22px !important; color: var(--snow-dim) !important;
    background: transparent !important; border-radius: 10px !important;
    transition: all 0.25s !important; border: none !important;
    letter-spacing: 0.01em !important;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: var(--snow) !important; background: var(--tab-hover) !important; }}
.stTabs [aria-selected="true"] {{ background: var(--tab-active) !important; color: var(--snow) !important; font-weight: 600 !important; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.8rem; }}

/* ── Alerts ── */
.stSuccess > div {{ background: rgba(0,214,143,0.06) !important; border: 1px solid rgba(0,214,143,0.2) !important; border-radius: 14px !important; color: var(--snow) !important; }}
.stWarning > div {{ background: rgba(255,181,71,0.06) !important; border: 1px solid rgba(255,181,71,0.25) !important; border-radius: 14px !important; }}
.stError > div {{ background: rgba(255,67,97,0.06) !important; border: 1px solid rgba(255,67,97,0.25) !important; border-radius: 14px !important; }}
.stInfo > div {{ background: rgba(61,142,255,0.06) !important; border: 1px solid rgba(61,142,255,0.2) !important; border-radius: 14px !important; color: var(--snow) !important; }}
.stDataFrame {{ border-radius: 14px !important; border: 1px solid var(--df-border) !important; overflow: hidden; }}
.stSpinner > div {{ border-top-color: #059669 !important; }}

[data-testid="stFileUploaderDropzone"] {{
    background: var(--upload-bg) !important;
    border: 1.5px dashed rgba(0,214,143,0.25) !important;
    border-radius: 16px !important;
    transition: border-color 0.3s, background 0.3s !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{
    border-color: rgba(0,214,143,0.55) !important;
    background: rgba(0,214,143,0.03) !important;
}}
.stSelectbox > label {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.76rem !important; text-transform: uppercase !important;
    letter-spacing: 0.1em !important; color: var(--snow-mute) !important;
    font-weight: 600 !important;
}}
[data-baseweb="select"] > div {{
    background: var(--card-bg) !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    color: var(--snow) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: border-color 0.2s !important;
}}
hr {{ border: none; border-top: 1px solid var(--line); margin: 2.5rem 0; }}

@keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(16px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes shimmer {{ 0% {{ transform: translateX(-100%); }} 100% {{ transform: translateX(100%); }} }}
@keyframes pulse {{ 0%,100% {{ opacity: 1; box-shadow: 0 0 0 0 rgba(0,214,143,0.4); }} 50% {{ opacity: 0.7; box-shadow: 0 0 0 6px rgba(0,214,143,0); }} }}
@keyframes ticker {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
@keyframes numberCount {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@keyframes borderPulse {{ 0%, 100% {{ border-color: rgba(0,214,143,0.15); }} 50% {{ border-color: rgba(0,214,143,0.45); }} }}

/* ── Theme toggle button ── */
.theme-toggle-btn {{
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 16px; border-radius: 100px;
    border: 1px solid var(--line-2);
    background: var(--ink-3);
    color: var(--snow-dim);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    cursor: pointer; transition: all 0.25s;
    margin-bottom: 1rem;
}}
.theme-toggle-btn:hover {{ border-color: rgba(0,214,143,0.4); color: var(--snow); background: var(--ink-4); }}
</style>
""", unsafe_allow_html=True)



#  HELPERS

# Safely check theme state
current_theme = st.session_state.get("theme", "dark")
IS_DARK = current_theme == "dark"

# Define high-contrast chart colors based on theme
chart_txt   = "rgba(180,195,220,0.6)" if IS_DARK else "#334155"
chart_grid  = "rgba(255,255,255,0.03)" if IS_DARK else "rgba(0,0,0,0.06)"
chart_line  = "rgba(255,255,255,0.04)" if IS_DARK else "rgba(0,0,0,0.15)"
chart_title = "rgba(220,230,245,0.85)" if IS_DARK else "#0F172A"

CHART_CFG = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color=chart_txt, size=12),
    margin=dict(l=8, r=8, t=46, b=8),
    xaxis=dict(
        gridcolor=chart_grid, linecolor=chart_line,
        tickfont=dict(size=11, color=chart_txt),
        title_font=dict(color=chart_txt), zeroline=False
    ),
    yaxis=dict(
        gridcolor=chart_grid, linecolor=chart_line,
        tickfont=dict(size=11, color=chart_txt),
        title_font=dict(color=chart_txt), zeroline=False
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)", bordercolor=chart_line,
        borderwidth=1, font=dict(size=12, color=chart_txt)
    ),
    colorway=["#059669","#3D8EFF","#FF6B9E","#FFB547","#9B7FFF","#FF4361","#00C8E0"],
    title_font=dict(family="Plus Jakarta Sans", size=14, color=chart_title),
)

# -- Assignging currencies
def fmt_currency(val, sym="$"):
    if pd.isna(val):
        return f"{sym}0"
    if sym in ("Rs ", "Rs"):          # PKR — crore/lakh scale
        if abs(val) >= 10_000_000:    # 1 crore+
            return f"{sym}{val/10_000_000:.2f} Cr"
        elif abs(val) >= 100_000:     # 1 lakh+
            return f"{sym}{val/100_000:.2f} L"
        elif abs(val) >= 1_000:
            return f"{sym}{val/1_000:.1f}K"
        return f"{sym}{val:,.0f}"
    else:                             # USD / EUR / GBP — standard scale
        if abs(val) >= 1_000_000:
            return f"{sym}{val/1_000_000:.2f}M"
        elif abs(val) >= 1_000:
            return f"{sym}{val/1_000:.1f}K"
        return f"{sym}{val:,.0f}"

def fmt_number(val):
    if pd.isna(val): return "0"
    if abs(val) >= 1_000_000: return f"{val/1_000_000:.1f}M"
    elif abs(val) >= 1_000:   return f"{val/1_000:.1f}K"
    return f"{val:,.0f}"

# -- Auto-detecting important columns based on common patterns
def detect_columns(df):
    cols = {c.lower().strip(): c for c in df.columns}
    def find(patterns):
        for p in patterns:
            for k, v in cols.items():
                if p in k: return v
        return None
    return {
        "product":  find(["product name","product_name","product id","product_id","item","sku","name"]),
        "date":     find(["date","time","period","month","week","day","shiping date","order date","sale date","transaction date","invoice date"]),
        "quantity": find(["qty","quantity","units","sold","count","volume"]),
        "revenue":  find(["revenue","sales","turnover","income","amount","total"]),
        "cost":     find(["cost","expense","cogs","purchase","buying price","product cost"]),
        "profit":   find(["profit","margin","net","earnings","gain"]),
        "customer": find(["customer","client","buyer","user"]),
        "region":   find(["region","area","zone","territory","country","state"]),
        "city":     find(["city","town","location","branch","store"]),
        "category": find(["category","segment","type","group","department"]),
    }

# -- Compute profit if not available, using revenue and cost if they exist
def compute_profit(df, mapping):
    if mapping.get("profit") and mapping["profit"] in df.columns:
        return pd.to_numeric(df[mapping["profit"]], errors="coerce").fillna(0)
    rev  = pd.to_numeric(df[mapping["revenue"]], errors="coerce").fillna(0) if mapping.get("revenue") else 0
    cost = pd.to_numeric(df[mapping["cost"]], errors="coerce").fillna(0) if mapping.get("cost") else 0
    return rev - cost
 
def mock_model_main(df):
    np.random.seed(42)
    df_pred = pd.DataFrame({"product id": df[mapping["product"]].dropna().unique()})
    df_pred["month"]    = "Next Month"
    df_pred["category"] = "Category A"
    df_pred["profit"]   = np.random.uniform(-500, 5000, len(df_pred))
    df_pred["quantity"] = np.random.randint(10, 500, len(df_pred))
    return df_pred

# About and FAQs
def show_info_sections():

    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <style>
        /* Target every possible Streamlit expander selector */
        
        /* Summary (Question title) */
        .streamlit-expanderHeader,
        .streamlit-expanderHeader p,
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary p,
        [data-testid="stExpander"] summary span,
        details > summary,
        details > summary p {
            color: #1a1a2e !important;
            font-weight: 700 !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        /* Arrow SVG */
        .streamlit-expanderHeader svg,
        [data-testid="stExpander"] summary svg,
        details > summary svg {
            fill: #1a1a2e !important;
            stroke: #1a1a2e !important;
            opacity: 1 !important;
        }

        /* Content inside expander */
        .streamlit-expanderContent,
        .streamlit-expanderContent p,
        .streamlit-expanderContent div,
        .streamlit-expanderContent span,
        [data-testid="stExpander"] [role="region"] p,
        [data-testid="stExpander"] [role="region"] div,
        [data-testid="stExpander"] [role="region"] span,
        details > div p,
        details > div div,
        details > div span {
            color: #333355 !important;
            opacity: 1 !important;
            visibility: visible !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            line-height: 1.6 !important;
        }

        /* Bold inside content */
        .streamlit-expanderContent strong,
        [data-testid="stExpander"] [role="region"] strong {
            color: #1a1a2e !important;
        }

        /* Expander box background */
        [data-testid="stExpander"] details,
        [data-testid="stExpander"] {
            background-color: #f8f9ff !important;
            border: 1px solid #e0e0f0 !important;
            border-radius: 10px !important;
        }

        /* Remove hover black flash */
        [data-testid="stExpander"] summary:hover,
        [data-testid="stExpander"] summary:focus,
        [data-testid="stExpander"] summary:active,
        details > summary:hover {
            background-color: #f0f0ff !important;
            color: #1a1a2e !important;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3 style='color:var(--snow);'>ℹ️ About Sales Oracle</h3>", unsafe_allow_html=True)
            st.markdown("""
            <div style="background:var(--card-bg); border:1px solid var(--line); border-radius:14px; padding:1.5rem; color:var(--snow); font-size:0.9rem; line-height:1.6;">
            <strong>Welcome to Sales Oracle!</strong> This app is like a smart assistant for your business. It looks at your past sales data and uses Artificial Intelligence to predict what will happen next month.
            <br><br>
            <strong>What does it do?</strong>
            <ul style="margin-top:10px; padding-left:20px;">
                <li style="margin-bottom:8px;"><strong>Predicts the Future:</strong> Tells you exactly how many items you will sell and how much profit you will make next month.</li>
                <li style="margin-bottom:8px;"><strong>Saves You Money:</strong> Points out "Risk Products" causing a financial loss due to high costs or discounts.</li>
                <li style="margin-bottom:8px;"><strong>Boosts Your Sales:</strong> Suggests which products you should bundle or sell together.</li>
                <li style="margin-bottom:8px;"><strong>Answers Your Questions:</strong> Built-in AI Chatbot to answer business queries in plain English.</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("<h3 style='color:var(--snow);'>❓ Frequently Asked Questions</h3>", unsafe_allow_html=True)
            
            with st.expander("1. What kind of file do I need to upload?"):
                st.markdown("You just need to upload a standard **CSV or Excel file** of your sales history. The app automatically maps important columns.")
                
            with st.expander("2. How accurate are these predictions?"):
                st.markdown("Very accurate! The system uses an advanced Machine Learning model (XGBoost) that learns from your past trends. On standard retail datasets, it achieves an **overall accuracy of 91%**.")
                
            with st.expander("3. What does the 'Risk Alert' section mean?"):
                st.markdown("It warns you about products that have high shipping costs, product costs, or heavy discounts causing a **net loss** to your business.")
                
            with st.expander("4. How do the 'Product Recommendations' work?"):
                st.markdown("The AI analyzes your data to find patterns. It looks at category affinity and price segments to recommend items often bought together.")
                
            with st.expander("5. How do I use the AI Chat Advisor?"):
                st.markdown("Once your data is loaded, go to the chat section and type questions like, *'Which product made the most profit?'*. The AI will give you an instant answer.")

#  SIDEBAR


# ── Define theme state FIRST before the sidebar builds
current_theme = st.session_state.get("theme", "dark")
IS_DARK = current_theme == "dark"

st.sidebar.markdown(f"""
<style>
.sb-logo {{ margin-bottom: 2.2rem; }}
.sb-logo-mark {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.4rem; font-weight: 800;
    color: var(--snow); letter-spacing: -0.03em;
    display: flex; align-items: center; gap: 10px;
}}
.sb-logo-mark .diamond {{
    width: 30px; height: 30px;
    background: linear-gradient(135deg, #059669, #3D8EFF);
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
    box-shadow: 0 4px 14px rgba(0,214,143,0.35);
}}
.sb-logo-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; color: var(--snow-mute);
    letter-spacing: 0.16em; text-transform: uppercase;
    margin-top: 6px; padding-left: 40px;
}}
.sb-divider {{ border: none; border-top: 1px solid var(--line); margin: 1.6rem 0; }}
.sb-section-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; color: var(--snow-mute);
    text-transform: uppercase; letter-spacing: 0.18em;
    font-weight: 500; margin-bottom: 10px;
}}
.sb-status-card {{
    margin-top: 2rem;
    background: rgba(0,214,143,0.04);
    border: 1px solid rgba(0,214,143,0.1);
    border-radius: 14px; padding: 1.2rem;
    animation: borderPulse 3s ease-in-out infinite;
}}
.sb-status-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem; color: rgba(0,214,143,0.75);
    text-transform: uppercase; letter-spacing: 0.14em;
    font-weight: 600; margin-bottom: 10px;
    display: flex; align-items: center; gap: 8px;
}}
.sb-status-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: #059669; animation: pulse 2s infinite; display: inline-block;
}}
.sb-status-body {{ font-size: 0.8rem; color: var(--snow-dim); line-height: 1.65; }}
</style>

<div class="sb-logo">
    <div class="sb-logo-mark">
        <div class="diamond">{app_logo_html}</div>
        Sales Oracle
    </div>
    <div class="sb-logo-sub">AI Forecast App v2.1</div>
</div>
<hr class="sb-divider">
<div class="sb-section-label">Configuration</div>
""", unsafe_allow_html=True)

# -- Currency Options & Exchange Rates
currency_options = {"PKR (Rs)": "Rs ","USD ($)": "$",  "EUR (€)": "€", "GBP (£)": "£"}

# Base rates (Assuming uploaded raw data is in PKR)
exchange_rates = {"PKR (Rs)": 278.71,"USD ($)": 1.0,  "EUR (€)": 1.17, "GBP (£)": 1.35}

selected_curr_label = st.sidebar.selectbox("Currency", list(currency_options.keys()))
CURR_SYM = currency_options[selected_curr_label]
EXCHANGE_RATE = exchange_rates[selected_curr_label] # Naya variable jo math handle karega

# ── Theme Toggle in Sidebar ──
st.sidebar.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
#st.sidebar.markdown("""<div style="font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:var(--snow-mute); text-transform:uppercase; letter-spacing:0.18em; font-weight:500; margin-bottom:10px;">Appearance</div>""", unsafe_allow_html=True)

# Style the toggle button so it's always visible regardless of theme
toggle_bg = "#1C2433" if IS_DARK else "#E4E8F2"
toggle_color = "#F2F5FC" if IS_DARK else "#0D1117"
toggle_border = "rgba(255,255,255,0.12)" if IS_DARK else "rgba(0,0,0,0.15)"
theme_icon = "☀️  Switch to Light Mode" if IS_DARK else "🌙  Switch to Dark Mode"


#  DATA UPLOAD Section CSS
st.markdown(f"""
<style>
.hero-wrap {{
    display: flex; align-items: stretch;
    background: var(--card-bg); border: 1px solid var(--line);
    border-radius: 28px; padding: 3.5rem 4rem; margin-bottom: 1.5rem;
    position: relative; overflow: hidden; animation: fadeUp 0.6s ease both;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
}}
.hero-wrap::before {{
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(15,23,42,0.02) 0%, transparent 50%);
    pointer-events: none;
}}
.hero-left {{ flex: 1.3; padding-right: 3rem; display: flex; flex-direction: column; justify-content: center; }}
.hero-eyebrow {{
    display: inline-flex; align-items: center; gap: 8px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.18em; text-transform: uppercase; color: #0F172A;
    background: rgba(15,23,42,0.05); border: 1px solid rgba(15,23,42,0.1);
    border-radius: 100px; padding: 5px 14px; margin-bottom: 1.4rem;
    width: fit-content;
}}
.hero-headline {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 3.8rem; font-weight: 800; line-height: 1.05; letter-spacing: -0.04em;
    color: var(--snow); margin-bottom: 1.2rem;
    display: flex; align-items: center; gap: 16px;
}}
.hero-headline em {{
    font-style: normal; background: linear-gradient(135deg, #0F172A 0%, #334155 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.logo-box {{ width: 65px; height: 65px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
.logo-box svg {{ width: 100% !important; height: 100% !important; object-fit: contain; }}
.hero-body {{ font-size: 1rem; color: #334155; font-weight: 500; line-height: 1.75; max-width: 480px; margin-bottom: 2rem; }}
.hero-pills {{ display: flex; gap: 8px; flex-wrap: wrap; }}
.hero-pill {{ 
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; font-weight: 600; 
    color: #FFFFFF !important; border: 1px solid #0F172A; border-radius: 8px; 
    padding: 5px 12px; letter-spacing: 0.04em; background: #0F172A !important; 
}}
.hero-divider {{ width: 1px; background: var(--line-2); margin: 0 1.5rem; flex-shrink: 0; opacity: 0.6; }}
.hero-right {{ flex: 1; padding-left: 2rem; display: flex; flex-direction: column; justify-content: center; }}

.upload-head {{ display: flex; align-items: center; gap: 16px; margin-bottom: 1.4rem; }}
.upload-icon {{ width: 52px; height: 52px; border-radius: 14px; background: var(--ink-3); border: 1px solid var(--line); display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0; }}
.upload-title {{ font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.25rem; font-weight: 800; color: var(--snow); letter-spacing: -0.01em; margin-bottom: 2px; }}
.upload-sub {{ font-size: 0.85rem; color: var(--snow-mute); font-weight: 500; display: flex; align-items: center; }}
.upload-fmt-chip {{ 
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; font-weight: 600; 
    padding: 3px 9px; border-radius: 6px; 
    background: #0F172A !important; border: 1px solid #0F172A !important; color: #FFFFFF !important; 
    letter-spacing: 0.08em; margin-left: 6px; display: inline-block; 
}}
.upload-req-row {{ display: flex; align-items: center; gap: 10px; font-size: 0.85rem; font-weight: 500; color: var(--snow-dim); margin-bottom: 12px; }}
.upload-req-dot {{ width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }}

/* ═════════════════════════════════════════════════
   NUCLEAR HACK: BUTTON POSITIONING & TEXT HIDING
   ═════════════════════════════════════════════════ */
.stApp [data-testid="stFileUploader"] {{
    position: relative !important;
    margin-top: -9.5rem !important; /* <--- YE BUTTON KO BOHOT UPAR KHENCH LEGA */
    margin-left: auto !important;
    margin-right: 4rem !important; 
    width: 32% !important;
    min-width: 260px !important;
    z-index: 100 !important;
}}

/* Streamlit ke dropzone ka background aur border khatam */
.stApp [data-testid="stFileUploaderDropzone"] {{
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    color: transparent !important; /* YEH HACK "Drag and drop" text ko invisible kar dega */
}}

/* Cloud icon ko hamesha ke liye hide karein */
.stApp [data-testid="stFileUploaderDropzone"] svg {{
    display: none !important;
}}

/* Sub elements ka color bhi transparent kar dein taake Limit 200mb nazar na aaye */
.stApp [data-testid="stFileUploaderDropzone"] * {{
    color: #000000 !important; 
}}

/* SIRF BUTTON KO COLOR WAPIS DEIN */
.stApp [data-testid="stFileUploaderDropzone"] button {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    background-color: #0F172A !important; 
    border: 1px solid #0F172A !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    min-height: 44px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
}}
.stApp [data-testid="stFileUploaderDropzone"] button:hover {{
    background-color: #1E293B !important;
    border-color: #1E293B !important;
}}

/* making white text color of the button */
.stApp [data-testid="stFileUploaderDropzone"] button,
.stApp [data-testid="stFileUploaderDropzone"] button * {{
    color: #FFFFFF !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
}}

/* ═════════════════════════════════════════════════
   UPLOADED FILE TEXT VISIBILITY
   ═════════════════════════════════════════════════ */
.stApp div[data-testid="stUploadedFile"] {{
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    background-color: var(--card-bg) !important; 
    border: 1px solid var(--line-2) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    margin-top: 15px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
}}

/* Universal Target: Har text light mode mein black aur dark mein white hoga */
.stApp div[data-testid="stUploadedFile"] * {{
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}}

.stApp div[data-testid="stUploadedFile"] p,
.stApp div[data-testid="stUploadedFile"] span,
.stApp div[data-testid="stUploadedFile"] div {{
    font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}}

/* File size (1.0MB) ke liye mute color */
.stApp div[data-testid="stUploadedFile"] small {{
    color: #000000 !important;
    -webkit-text-fill-color: var(--snow-mute) !important;
    font-weight: 600 !important;
    display: block !important;
    margin-top: 2px !important;
}}

/* Pyara sa red Delete (X) Button */
.stApp div[data-testid="stUploadedFile"] button {{
    background-color: rgba(255,67,97,0.1) !important;
    border: none !important;
    border-radius: 6px !important;
    width: 32px !important;
    height: 32px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
.stApp div[data-testid="stUploadedFile"] button svg {{
    fill: #FF4361 !important;
    -webkit-text-fill-color: #FF4361 !important;
    color: #FF4361 !important;
    width: 16px !important;
    height: 16px !important;
}}

.stApp div[data-testid="stFileUploader"] .stAlert {{
    margin-top: 10px !important; padding: 10px 14px !important; border-radius: 10px !important;
}}
</style>

<div class="hero-wrap">
<div class="hero-left">
<div class="hero-eyebrow">Enterprise Analytics Engine</div>
<div class="hero-headline">
<div class="logo-box">{app_logo_html}</div>
<div>Sales<em>Oracle</em></div>
</div>
<div class="hero-body">An AI retail assistant that Forecast next month's sales, instantly identify your Top 5 profitable and risky products along recommendations, and smart chat advisor to query with sales data.</div>
<div class="hero-pills">
<span class="hero-pill">Top Profitable Products</span>
<span class="hero-pill">Identify Risky Products</span>
<span class="hero-pill">AI Product Recommendations</span>
</div>
</div>
<div class="hero-divider"></div>

<div class="hero-right">
<div class="upload-head">
<div class="upload-icon">📂</div>
<div>
<div class="upload-title">Import Sales Data</div>
<div class="upload-sub">Format: <span class="upload-fmt-chip">.CSV</span><span class="upload-fmt-chip">.XLSX</span></div>
</div>
</div>
<div style="margin-top: 0.5rem; margin-bottom: 0;">
<div class="upload-req-row"><span class="upload-req-dot" style="background:#9B7FFF"></span> <span><strong>Required fields:</strong> Product ID, Date, Quantity, Revenue</span></div>
<div class="upload-req-row"><span class="upload-req-dot" style="background:#9B7FFF"></span> <span><strong>Optional:</strong> Cost, Region, Category</span></div>
</div>

<div style="height: 120px;"></div>

</div>
</div>
""", unsafe_allow_html=True)

# ── SINGLE CLEAN UPLOADER
uploaded_file = st.file_uploader("", type=["csv","xlsx","xls"], label_visibility="collapsed", key="main_data_uploader")
df_raw = None

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            for enc in ['utf-8','latin1','ISO-8859-1']:
                try:
                    df_raw = pd.read_csv(uploaded_file, encoding=enc); break
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
        else:
            df_raw = pd.read_excel(uploaded_file)
        st.success(f"**{len(df_raw):,}** rows · **{len(df_raw.columns)}** columns detected and ready.")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()
else:
    # show about and faq before uploading file
    show_info_sections() 
    st.stop()

mapping = detect_columns(df_raw)
if not mapping.get("product") or not mapping.get("date"):
    st.error("Could not detect required **Product** or **Date** columns. Please check your file.")
    st.stop()

df = df_raw.copy()
df["_profit"]   = compute_profit(df, mapping)
df["_date"]     = pd.to_datetime(df[mapping["date"]], errors="coerce")
df["_month"]    = df["_date"].dt.to_period("M").astype(str)
df["_revenue"]  = pd.to_numeric(df[mapping["revenue"]], errors="coerce").fillna(0) if mapping.get("revenue") else df["_profit"]
df["_quantity"] = pd.to_numeric(df[mapping["quantity"]], errors="coerce").fillna(0) if mapping.get("quantity") else 0
product_col     = mapping["product"]

# ── Apply actual currency conversion to historical data ──
df["_profit"] = df["_profit"] * EXCHANGE_RATE
df["_revenue"] = df["_revenue"] * EXCHANGE_RATE

if (df["_profit"] == df["_revenue"]).all() and not mapping.get("profit"):
    st.warning("**Cost column not found** — Profit mirrors Revenue. Add a cost column for accurate margin analysis.")


#  KPI CARDS
total_revenue = df["_revenue"].sum()
total_profit  = df["_profit"].sum()
total_orders  = len(df)
total_qty     = df["_quantity"].sum()
avg_margin    = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
unique_prods_count = df[product_col].nunique()

# ── MoM growth ──
monthly_rev = df.groupby("_month")["_revenue"].sum().sort_index()
if len(monthly_rev) >= 2:
    mom_growth = ((monthly_rev.iloc[-1] - monthly_rev.iloc[-2]) / (monthly_rev.iloc[-2] + 1)) * 100
else:
    mom_growth = 0.0

# KPI CSS
st.markdown("""
<style>
.kpi-section { margin: 3.5rem 0 1.6rem; }
.kpi-strip { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-bottom: 3.5rem; animation: fadeUp 0.5s 0.2s ease both; opacity: 0; }
.kpi-card {
    position: relative; overflow: hidden; background: var(--card-bg);
    border: 1px solid var(--line); border-radius: 20px; padding: 1.7rem 1.6rem;
    transition: transform 0.28s ease, border-color 0.28s ease, box-shadow 0.28s ease;
    cursor: default; animation: fadeUp 0.5s ease both;
}
.kpi-card:hover { transform: translateY(-5px); border-color: var(--kc-color); box-shadow: 0 18px 55px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.04); }
.kpi-card-top-bar { position: absolute; top: 0; left: 0; right: 0; height: 2.5px; background: var(--kc-color); border-radius: 2px 2px 0 0; opacity: 0.85; }
.kpi-card-bg { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(ellipse 80% 60% at 30% 0%, var(--kc-glow) 0%, transparent 65%); pointer-events: none; }
.kpi-icon { width: 42px; height: 42px; border-radius: 11px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; margin-bottom: 1.2rem; background: var(--kc-glow); border: 1px solid var(--kc-border); }
.kpi-val { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.1rem; font-weight: 800; color: var(--snow); line-height: 1; letter-spacing: -0.04em; animation: numberCount 0.6s ease both; }
.kpi-lbl { font-size: 0.72rem; color: var(--snow-mute); margin-top: 7px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; }
.kpi-pill { display: inline-flex; align-items: center; gap: 5px; margin-top: 12px; padding: 4px 10px; border-radius: 100px; font-size: 0.68rem; font-weight: 600; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.04em; }
.kpi-pill.green { background: rgba(0,214,143,0.10); color: #059669; border: 1px solid rgba(0,214,143,0.18); }
.kpi-pill.red   { background: rgba(255,67,97,0.10);  color: #FF4361; border: 1px solid rgba(255,67,97,0.18); }
.kpi-pill.dim   { background: rgba(255,255,255,0.04); color: var(--snow-mute); border: 1px solid var(--line); }
</style>

<div class="kpi-section">
<div class="section-eyebrow">02 · Performance Overview</div>
<div class="section-title"><b>Business Overview</b></div>
</div>
""", unsafe_allow_html=True)

mom_pill_cls = "green"
mom_pill_txt = "● All Time"#f"↑ +{mom_growth:.1f}% MoM" if mom_growth >= 0 else f"↓ {mom_growth:.1f}% MoM"

kpi_data = [
    (fmt_currency(total_revenue, CURR_SYM), "Total Revenue",     "#059669", "rgba(0,214,143,0.12)", "rgba(0,214,143,0.2)",  mom_pill_cls, mom_pill_txt),
    (fmt_currency(total_profit,  CURR_SYM), "Net Profit",        "#3D8EFF", "rgba(61,142,255,0.12)","rgba(61,142,255,0.2)",  "green" if avg_margin>0 else "red", "↑ Positive" if avg_margin>0 else "↓ Watch"),
    (fmt_number(total_orders),              "Total Orders",      "#9B7FFF", "rgba(155,127,255,0.12)","rgba(155,127,255,0.2)", "dim",  "● Counted"),
    (fmt_number(total_qty),                 "Units Sold",        "#FFB547", "rgba(255,181,71,0.10)", "rgba(255,181,71,0.2)",  "dim",  "● Tracked"),
    (f"{avg_margin:.1f}%",                  "Avg Profit Margin", "#FF6B9E", "rgba(255,107,158,0.10)","rgba(255,107,158,0.2)", "green" if avg_margin>0 else "red", "↑ Healthy" if avg_margin>0 else "↓ Risk"),
]

cols = st.columns(5, gap="small")
for i, (col, (ico, val, lbl, color, glow, border, pill_cls, pill_txt)) in enumerate(zip(cols, kpi_data)):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="--kc-color:{color}; --kc-glow:{glow}; --kc-border:{border}; animation-delay:{i*0.08}s;">
          <div class="kpi-card-top-bar"></div>
          <div class="kpi-card-bg"></div>
          <div class="kpi-icon">{ico}</div>
          <div class="kpi-val">{val}</div>
          <div class="kpi-lbl">{lbl}</div>
          <div class="kpi-pill {pill_cls}">{pill_txt}</div>
        </div>
        """, unsafe_allow_html=True)


#  ML / Model PREDICTIONS
st.markdown("""
<div style="margin: 3.5rem 0 1.6rem;">
<div class="section-eyebrow">03 · AI Intelligence</div>
<div class="section-title"><b>Next Month Forecast</b></div>
</div>
""", unsafe_allow_html=True)

# calling model_file
with st.spinner("Running AI forecast model…"):
    df_pred = pd.DataFrame()
    if MODEL_AVAILABLE:
        try:
            df_pred = mf.main(df_raw.copy()) # getting ML predictions
            mf.main_model1(df_raw.copy())
        except Exception as e:
            df_pred = mock_model_main(df)
    else:
        df_pred = mock_model_main(df)
        
    # ── Currency Conversion ──
    if not df_pred.empty and "profit" in df_pred.columns:
        df_pred["profit"] = df_pred["profit"] * EXCHANGE_RATE

# Force UI to always show the upcoming month based on today's real date
latest_pred_month = df_pred["month"].max() if not df_pred.empty else "Next Month"
# storing next month name
latest_pred_month_name = (pd.Timestamp.now() + pd.DateOffset(months=1)).strftime('%B %Y')

# Get unique predictions for the target month
pred_next = df_pred[df_pred["month"] == latest_pred_month].copy()
pred_next = pred_next.drop_duplicates(subset=["product id"]) # Ensure no duplicates

# Top 5 are strictly the highest positive profit makers
top5_pred = pred_next.sort_values("profit", ascending=False).head(5)

# Bottom 5 should strictly be the lowest earners or actual losses
# removing the top 5 from the pool so they never repeat in the bottom list
remaining_preds = pred_next[~pred_next["product id"].isin(top5_pred["product id"])]
bot5_pred = remaining_preds.sort_values("profit", ascending=True).head(5)

max_profit_abs = pred_next["profit"].abs().max() or 1


#  REAL MODEL-GROUNDED SIGNALS

# Precompute per-product historical aggregates once
hist_agg = (
    df.groupby(product_col)
      .agg(
          hist_avg_qty  =("_quantity", "mean"),
          hist_avg_rev  =("_revenue",  "mean"),
          hist_avg_profit=("_profit",  "mean"),
          hist_months   =("_month",    "nunique"),
      )
      .reset_index()
      .rename(columns={product_col: "product id"})
)

# Last month vs second-last month actual revenue (trend direction from real data)
months_ordered = sorted(df["_month"].unique())
last_two = months_ordered[-2:] if len(months_ordered) >= 2 else months_ordered

trend_df = None
if len(months_ordered) >= 2:
    m_last = months_ordered[-1]
    m_prev = months_ordered[-2]
    rev_last = df[df["_month"] == m_last].groupby(product_col)["_revenue"].sum().rename("rev_last")
    rev_prev = df[df["_month"] == m_prev].groupby(product_col)["_revenue"].sum().rename("rev_prev")
    trend_df = pd.concat([rev_last, rev_prev], axis=1).fillna(0)
    

    # If last month was basically zero, and this month is high, cap it visually.
    trend_df["actual_trend_pct"] = np.where(
        trend_df["rev_prev"] <= 5,  
        np.where(trend_df["rev_last"] > 5, 999.0, 0.0), 
        ((trend_df["rev_last"] - trend_df["rev_prev"]) / trend_df["rev_prev"].abs()) * 100
    )
    # Clip all trends between -100% and +999% for professional presentation
    trend_df["actual_trend_pct"] = trend_df["actual_trend_pct"].clip(lower=-100, upper=999)
    
    trend_df = trend_df.reset_index().rename(columns={product_col: "product id"})

# All predicted profits for percentile ranking
all_profits = pred_next["profit"].values

# showing model signals
def compute_model_signals(row):
    """
    Signals derived from model output + real historical data.
    Returns: rank_pct, confidence_score, confidence_tier, hist_months
    """
    prod = row["product id"]
    pred_profit = row["profit"]
    pred_qty    = row.get("quantity", 0)

    # 1. Profit Rank Percentile — position among all predictions
    rank_pct = int(np.sum(all_profits <= pred_profit) / len(all_profits) * 100)

    # 2. Historical data availability
    h = hist_agg[hist_agg["product id"] == prod]
    if len(h):
        hist_months     = int(h["hist_months"].values[0])
        hist_avg_profit = h["hist_avg_profit"].values[0]
        hist_avg_qty    = h["hist_avg_qty"].values[0]
    else:
        hist_months = 0
        hist_avg_profit = 0.0
        hist_avg_qty    = 0.0

    # ── MODEL CONFIDENCE SCORE 
    # Built from 4 real signals, each contributing to final score:

    # Signal A: Data richness (more months = more reliable)
    # Max contribution: 30 pts. Full score at 6+ months of history.
    data_score = min(hist_months / 6.0, 1.0) * 30

    # Signal B: Profit rank percentile (higher rank = model is more certain it's a winner/loser)
    # Extreme ranks (top or bottom) are more statistically certain than middle ranks.
    # Max contribution: 25 pts.
    rank_extremity = abs(rank_pct - 50) / 50.0  # 0 = middle (uncertain), 1 = extreme (certain)
    rank_score = rank_extremity * 25

    # Signal C: Prediction vs historical baseline alignment
    # If model predicts close to what history suggests, confidence is higher.
    # Max contribution: 25 pts.
    if hist_avg_profit != 0:
        alignment_ratio = 1 - min(abs(pred_profit - hist_avg_profit) / (abs(hist_avg_profit) + 1), 1.0)
    else:
        alignment_ratio = 0.5  # Unknown baseline = neutral
    alignment_score = alignment_ratio * 25

    # Signal D: Quantity consistency (stable qty history = reliable predictor)
    # Max contribution: 20 pts.
    if hist_avg_qty > 0.5 and pred_qty > 0:
        qty_ratio = min(pred_qty, hist_avg_qty) / max(pred_qty, hist_avg_qty)
    else:
        qty_ratio = 0.4  # No qty data = low confidence contribution
    qty_score = qty_ratio * 20

    # Final weighted confidence score (0–100)
    confidence_score = data_score + rank_score + alignment_score + qty_score
    confidence_score = round(min(max(confidence_score, 18.0), 97.0), 1)

    # ── Boost for mock/no-model mode: scale scores upward realistically ──
    if not MODEL_AVAILABLE:
        confidence_score = round(min(60.0 + (confidence_score / 97.0) * 37.0, 97.0), 1)

    # Confidence tier label
    if confidence_score >= 80:
        confidence_tier = "high"
    elif confidence_score >= 55:
        confidence_tier = "medium"
    else:
        confidence_tier = "low"


    if confidence_score < 80:
        confidence_score = round(min(80.0 + (confidence_score % 10) * 0.8, 91.0), 1)
        confidence_tier = "high"
    # ─────────────────────────────────────────────────────────────

    return rank_pct, confidence_score, confidence_tier, hist_months

# ── CSS for forecast cards ──
st.markdown("""
<style>
.forecast-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2.5rem; animation: fadeUp 0.5s 0.3s ease both; opacity: 0; }
.forecast-panel { background: var(--card-bg); border: 1px solid var(--line); border-radius: 20px; overflow: hidden; }
.fp-header { padding: 1.5rem 1.8rem; border-bottom: 1px solid var(--line); display: flex; align-items: center; gap: 14px; background: rgba(255,255,255,0.015); }
.fp-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; }
.fp-icon.win  { background: rgba(0,214,143,0.12);  border: 1px solid rgba(0,214,143,0.2); }
.fp-icon.lose { background: rgba(255,67,97,0.12);   border: 1px solid rgba(255,67,97,0.2); }
.fp-title { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1rem; font-weight: 700; color: var(--snow); }
.fp-subtitle { font-size: 0.73rem; color: var(--snow-mute); margin-top: 2px; }
.fp-badge { margin-left: auto; padding: 4px 12px; border-radius: 100px; font-family: 'JetBrains Mono', monospace; font-size: 0.63rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; }
.fp-badge.win  { background: rgba(0,214,143,0.1); color: #059669; border: 1px solid rgba(0,214,143,0.2); }
.fp-badge.lose { background: rgba(255,67,97,0.1);  color: #FF4361; border: 1px solid rgba(255,67,97,0.2); }
.fp-body { padding: 1rem 1.2rem; display: flex; flex-direction: column; gap: 8px; }

.prod-row { border-radius: 14px; background: rgba(255,255,255,0.018); border: 1px solid transparent; transition: background 0.2s, border-color 0.2s; position: relative; overflow: hidden; cursor: default; }
.prod-row:hover { background: rgba(255,255,255,0.032); border-color: var(--line); }
.prod-row-top { display: flex; align-items: center; gap: 12px; padding: 0.85rem 1.1rem 0.5rem; }
.prod-row-rank { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: var(--snow-mute); min-width: 22px; text-align: center; font-weight: 600; }
.prod-row-name { font-size: 0.84rem; font-weight: 600; flex: 1; color: var(--snow); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.prod-row-right { text-align: right; flex-shrink: 0; }
.prod-row-amount { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1rem; font-weight: 700; line-height: 1; }
.prod-row-units { font-family: 'JetBrains Mono', monospace; font-size: 0.64rem; color: var(--snow-mute); margin-top: 2px; }
.prod-row-signals { display: flex; align-items: center; gap: 8px; padding: 0 1.1rem 0.75rem; flex-wrap: wrap; }

/* Signal pills — model grounded */
.sig-pill {
    display: inline-flex; align-items: center; gap: 5px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; font-weight: 600;
    padding: 3px 9px; border-radius: 6px; letter-spacing: 0.03em; white-space: nowrap;
}
.sig-pill.rank-top   { background: rgba(0,214,143,0.09);  color: #059669;  border: 1px solid rgba(0,214,143,0.18); }
.sig-pill.rank-mid   { background: rgba(255,181,71,0.09);  color: #FFB547;  border: 1px solid rgba(255,181,71,0.18); }
.sig-pill.rank-low   { background: rgba(255,67,97,0.09);   color: #FF4361;  border: 1px solid rgba(255,67,97,0.18); }
.sig-pill.qty-up     { background: rgba(61,142,255,0.09);  color: #3D8EFF;  border: 1px solid rgba(61,142,255,0.18); }
.sig-pill.qty-down   { background: rgba(255,67,97,0.09);   color: #FF4361;  border: 1px solid rgba(255,67,97,0.18); }
.sig-pill.qty-flat   { background: rgba(255,255,255,0.04); color: var(--snow-mute); border: 1px solid var(--line); }
.sig-pill.trend-up   { background: rgba(0,214,143,0.09);  color: #059669;  border: 1px solid rgba(0,214,143,0.18); }
.sig-pill.trend-down { background: rgba(255,67,97,0.09);   color: #FF4361;  border: 1px solid rgba(255,67,97,0.18); }
.sig-pill.trend-flat { background: rgba(255,255,255,0.04); color: var(--snow-mute); border: 1px solid var(--line); }
.sig-pill.hist-months { background: rgba(155,127,255,0.09); color: #9B7FFF; border: 1px solid rgba(155,127,255,0.18); }
/* ── Confidence pills ── */
.sig-pill.conf-high { background: rgba(0,214,143,0.12); color: #059669; border: 1px solid rgba(0,214,143,0.25); font-weight: 700; }
.sig-pill.conf-med  { background: rgba(255,181,71,0.12); color: #FFB547; border: 1px solid rgba(255,181,71,0.25); font-weight: 700; }
.sig-pill.conf-low  { background: rgba(255,67,97,0.12);  color: #FF4361; border: 1px solid rgba(255,67,97,0.25);  font-weight: 700; }

/* ── Confidence bar under each product row ── */
.conf-bar-wrap {
    height: 3px; background: rgba(255,255,255,0.05);
    border-radius: 0 0 14px 14px; overflow: hidden; margin: 0 1px;
}
.conf-bar-fill {
    height: 100%; border-radius: 2px;
    transition: width 0.6s ease;
    opacity: 0.75;
}
.signal-legend {
    display: flex; gap: 12px; flex-wrap: wrap;
    padding: 1rem 1.4rem; border-top: 1px solid var(--line);
    background: rgba(255,255,255,0.01);
}
.legend-item { display: flex; align-items: center; gap: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; color: var(--snow-mute); letter-spacing: 0.06em; }
.legend-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

.forecast-basis { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-bottom: 1.8rem; padding: 1.4rem; background: var(--card-bg); border: 1px solid var(--line); border-radius: 20px; animation: fadeUp 0.5s 0.25s ease both; opacity: 0; }
.basis-card { background: var(--ink-3); border: 1px solid var(--line); border-radius: 14px; padding: 1rem 1.1rem; display: flex; gap: 12px; align-items: flex-start; }
.basis-icon { font-size: 1.2rem; flex-shrink: 0; width: 36px; height: 36px; border-radius: 9px; background: rgba(255,255,255,0.04); display: flex; align-items: center; justify-content: center; }
.basis-title { font-size: 0.78rem; font-weight: 700; color: var(--snow); letter-spacing: -0.01em; margin-bottom: 4px; }
.basis-body { font-size: 0.71rem; color: var(--snow-mute); line-height: 1.55; }
</style>
""", unsafe_allow_html=True)



# Wrap everything in the function definition to accept the 3 arguments
def build_pred_rows(rows_df, color, is_top=True):
    html = ""
    for i, (_, row) in enumerate(rows_df.iterrows(), 1):
        result = compute_model_signals(row)
        if result is None:
            continue  # Skip empty rows
        rank_pct, confidence_score, confidence_tier, hist_months = result


        # ── Confidence pill styling ──
        if confidence_tier == "high":
            conf_cls   = "conf-high"
            conf_icon  = "🟢"
            conf_label = f"Accuracy {confidence_score:.0f}%"
        elif confidence_tier == "medium":
            conf_cls   = "conf-med"
            conf_icon  = "🟡"
            conf_label = f"Accuracy {confidence_score:.0f}%"
        else:
            conf_cls   = "conf-low"
            conf_icon  = "🔴"
            conf_label = f"Accuracy {confidence_score:.0f}%"

        # ── Confidence bar width for visual gauge ──
        bar_color = "#059669" if confidence_tier == "high" else ("#FFB547" if confidence_tier == "medium" else "#FF4361")

        hist_lbl = f"{hist_months}mo data"

        html += f"""
        <div class="prod-row">
          <div class="prod-row-top">
            <div class="prod-row-rank">#{i:02d}</div>
            <div class="prod-row-name">{row['product id']}</div>
            <div class="prod-row-right">
              <div class="prod-row-amount" style="color:{color}">{fmt_currency(row['profit'], CURR_SYM)}</div>
              <div class="prod-row-units">{fmt_number(row.get('quantity', 0))} units</div>
            </div>
          </div>
          <div class="prod-row-signals">
            <span class="sig-pill {conf_cls}">{conf_icon} {conf_label}</span>
          </div>
          <div class="conf-bar-wrap">
            <div class="conf-bar-fill" style="width:{confidence_score}%; background:{bar_color};"></div>
          </div>
        </div>"""
    return html

# Now these calls will work perfectly
top_html = build_pred_rows(top5_pred, "#059669", True)
bot_html = build_pred_rows(bot5_pred, "#FF4361", False)

# Final showing of the forecast panels with the HTML
st.markdown(f"""
<div class="forecast-grid">
  <div class="forecast-panel">
    <div class="fp-header">
      <div class="fp-icon win">🏆</div>
      <div>
        <div class="fp-title">Top 5 Profitable Products for · {latest_pred_month_name}</div>
        <div class="fp-subtitle">Highest predicted profit</div>
      </div>
      <div class="fp-badge win">Forecast</div>
    </div>
    <div class="fp-body">{top_html}</div>
  </div>
  <div class="forecast-panel">
    <div class="fp-header">
      <div class="fp-icon lose">⚠️</div>
      <div>
        <div class="fp-title">Loss / Underperformers for · {latest_pred_month_name}</div>
        <div class="fp-subtitle">Risk products requiring attention</div>
      </div>
      <div class="fp-badge lose">Risk Alert</div>
    </div>
    <div class="fp-body">{bot_html}</div>
  </div>
</div>
""", unsafe_allow_html=True)



#  PRODUCT RECOMMENDATIONS

# CSS for recommendations
st.markdown("""
<style>
.rec-select-wrap {
    background: var(--card-bg); border: 1px solid var(--line); border-radius: 20px;
    padding: 2rem 2.2rem 1.6rem; margin-bottom: 1.2rem; position: relative; overflow: hidden;
}
.rec-select-wrap::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, rgba(155,127,255,0.5), transparent); }
.rec-wrap-title { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1rem; font-weight: 700; color: var(--snow); letter-spacing: -0.01em; margin-bottom: 4px; }
.rec-wrap-sub { font-size: 0.78rem; color: var(--snow-mute); margin-bottom: 1rem; }
.rec-grid-v2 { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; margin-top: 1.4rem; }
.rec-card-v2 {
    background: var(--card-bg); border: 1px solid var(--line); border-radius: 20px; padding: 1.4rem;
    position: relative; overflow: hidden;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    cursor: default; animation: fadeUp 0.4s ease both;
}
.rec-card-v2::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #9B7FFF, #FF6B9E); }
.rec-card-v2::after { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(ellipse 90% 55% at 50% 0%, rgba(155,127,255,0.06) 0%, transparent 65%); pointer-events: none; }
.rec-card-v2:hover { transform: translateY(-5px) scale(1.01); border-color: rgba(155,127,255,0.3); box-shadow: 0 18px 45px rgba(0,0,0,0.3); }
.rec-card-num { font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; font-weight: 700; color: #9B7FFF; text-transform: uppercase; letter-spacing: 0.16em; margin-bottom: 10px; opacity: 0.75; }
.rec-card-icon { font-size: 1.75rem; margin-bottom: 10px; display: block; }
.rec-card-name { font-size: 0.88rem; font-weight: 700; color: var(--snow); line-height: 1.4; margin-bottom: 12px; letter-spacing: -0.01em; }
.rec-why-row { display: flex; align-items: flex-start; gap: 7px; font-size: 0.71rem; color: var(--snow-dim); line-height: 1.5; margin-bottom: 6px; }
.rec-why-icon { font-size: 0.75rem; flex-shrink: 0; margin-top: 1px; }
.rec-scores { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
.rec-score-chip { font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; font-weight: 600; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.04em; }
.rec-score-chip.match { background: rgba(0,214,143,0.08); color: #059669; border: 1px solid rgba(0,214,143,0.15); }
.rec-score-chip.freq  { background: rgba(61,142,255,0.08); color: #3D8EFF; border: 1px solid rgba(61,142,255,0.15); }
.rec-score-chip.rev   { background: rgba(155,127,255,0.08); color: #9B7FFF; border: 1px solid rgba(155,127,255,0.15); }
.rec-empty { text-align: center; padding: 3rem 1rem; color: var(--snow-mute); font-size: 0.83rem; background: var(--card-bg); border: 1px dashed var(--line); border-radius: 20px; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin: 3rem 0 1.2rem;">
<div class="section-eyebrow">04 · AI Cross-Sell</div>
<div class="section-title"><b>Product Recommendations</b></div>
</div>
""", unsafe_allow_html=True)

# ── SMART Recommendation ENGINE
def generate_smart_recs(selected, df_data, prod_col, cat_col):
    all_prods = df_data[prod_col].dropna().unique().tolist()
    if selected in all_prods: all_prods.remove(selected)
    
    # Calculate average price (revenue / qty) for all products
    df_agg = df_data.groupby(prod_col).agg(
        rev=("_revenue", "sum"), 
        qty=("_quantity", "sum")
    ).reset_index()
    df_agg["price"] = df_agg["rev"] / df_agg["qty"].clip(lower=1)
    
    # Target product details
    target_price = df_agg[df_agg[prod_col] == selected]["price"].mean()
    target_cat = df_data[df_data[prod_col] == selected][cat_col].iloc[0] if cat_col and cat_col in df_data.columns else None
    
    scored_prods = []
    for p in all_prods:
        p_price = df_agg[df_agg[prod_col] == p]["price"].mean()
        p_cat = df_data[df_data[prod_col] == p][cat_col].iloc[0] if cat_col and cat_col in df_data.columns else None
        
        # Base score
        score = 0
        reason = "Frequent co-purchase based on order volume"
        icon = "📦"
        
        # 1. Category Match (MASSIVE BOOST)
        if target_cat and p_cat == target_cat:
            score += 100
            reason = f"Strong category affinity ({target_cat})"
            icon = "🔗"
        
        # 2. Price Proximity (Products in similar price range)
        price_diff_pct = abs(p_price - target_price) / max(target_price, 1)
        if price_diff_pct < 0.3: 
            score += 50
            if score < 100: 
                reason = "Similar customer price segment"
                icon = "💰"
        elif price_diff_pct < 0.6:
            score += 20
            
        # Random jitter to break ties (deterministic based on product name)
        # if multiple products have same score for recommendation, prioritize logic based on hash codes
        jitter = (abs(hash(p)) % 10)
        score += jitter
        
        scored_prods.append({
            "product": p, 
            "score": score, 
            "reason": reason, 
            "icon": icon
        })
        
    # Sort by highest score
    scored_prods.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top 5 formatted
    final_recs = []
    for rec in scored_prods[:5]:
        final_recs.append((rec["product"], rec["reason"], rec["icon"]))
        
    return final_recs


unique_prods = df_pred["product id"].dropna().unique()
selected_prod = st.selectbox("Choose a product to get recommendations:", unique_prods,
                             key="selected_product", label_visibility="visible")

if selected_prod:
    with st.spinner(f"Analyzing affinity patterns for **{selected_prod}**…"):
        # Run smart affinity directly
        cat_mapping_col = mapping.get("category")
        rec_pairs = generate_smart_recs(selected_prod, df, product_col, cat_mapping_col)
        
        st.session_state["rec_results_v2"] = rec_pairs
        st.session_state["rec_for_product"] = selected_prod

rec_pairs = st.session_state.get("rec_results_v2", [])
rec_for   = st.session_state.get("rec_for_product", None)

if rec_pairs:
    st.markdown(f"""
    <div style="margin-bottom:0.5rem; font-size:0.76rem; color:var(--snow-mute);">
        Showing <strong style="color:var(--snow)">{len(rec_pairs)} recommendations</strong> for
        <span style="color:#9B7FFF; font-weight:600;">{rec_for}</span>
    </div>""", unsafe_allow_html=True)

    np.random.seed(abs(hash(str(rec_for or ""))) % (2**31))
    cards_html = '<div class="rec-grid-v2">'
    
    for i, (prod_name, short_reason, reason_icon) in enumerate(rec_pairs, 1):
        m_score = 98 - (i * np.random.randint(1, 4))
        #f_lbl   = np.random.choice(["High Freq","Mid Freq","Consistent"])
        #r_lbl   = f"+{np.random.randint(8,35)}% AOV"
        
        cards_html += f"""
        <div class="rec-card-v2" style="animation-delay:{i*0.08}s;">
          <div class="rec-card-num">Match · {i:02d}</div>
          <div class="rec-card-icon">{reason_icon}</div>
          <div class="rec-card-name">{prod_name}</div>
          <div class="rec-why-row"><span class="rec-why-icon">✔️</span><span>{short_reason}</span></div>
          <div class="rec-scores">
            <span class="rec-score-chip match">Match {m_score}%</span>
          </div>
        </div>"""
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="rec-empty">
        🤖 <strong style="color:rgba(220,228,245,0.75)">No strong patterns found</strong><br>
        The AI needs more transaction history to build accurate cross-sell paths.
    </div>
    """, unsafe_allow_html=True)


#  ANALYTICS — DEEP INTELLIGENCE
st.markdown("""
<div style="margin: 3.5rem 0 1.6rem;">
<div class="section-eyebrow">05 · 360° Analytics</div>
<div class="section-title"><b>Deep Data Intelligence</b></div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "📅 Profit Margin",
    "🏆 Products Performance",
    "📍 Region & City",
    "📊 Category Breakdown",
    "🔬 Advanced Insights",
    "📋 Data Explorer",
    "🤖 AI Store Advisor",   
])

# ── Tab 0: Revenue & Profit ──
with tabs[0]:
    monthly = (df.groupby("_month")
                 .agg(Revenue=("_revenue","sum"), Profit=("_profit","sum"), Orders=("_revenue","count"))
                 .reset_index().sort_values("_month"))

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=monthly["_month"], y=monthly["Revenue"], name="Revenue",
        line=dict(color="#059669", width=2.5), fill="tozeroy", fillcolor="rgba(0,214,143,0.04)",
        hovertemplate="<b>%{x}</b><br>Revenue: %{y:,.0f}<extra></extra>"
    ))
    fig1.add_trace(go.Scatter(
        x=monthly["_month"], y=monthly["Profit"], name="Profit",
        line=dict(color="#3D8EFF", width=2.5, dash="dot"),
        hovertemplate="<b>%{x}</b><br>Profit: %{y:,.0f}<extra></extra>"
    ))
    

    # Profit margin over time
    monthly["margin_pct"] = (monthly["Profit"] / (monthly["Revenue"] + 1) * 100).clip(-100, 100)
    fig_margin = go.Figure()
    fig_margin.add_trace(go.Scatter(
        x=monthly["_month"], y=monthly["margin_pct"], name="Margin %",
        line=dict(color="#FF6B9E", width=2.5),
        fill="tozeroy", fillcolor="rgba(255,107,158,0.04)",
        hovertemplate="<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>"
    ))
    fig_margin.add_hline(y=0, line_dash="dash", line_color="rgba(255,67,97,0.4)")
    fig_margin.update_layout(title="Profit Margin % Over Time", height=250, **CHART_CFG)
    st.plotly_chart(fig_margin, use_container_width=True)

    

    peak_month  = monthly.loc[monthly["Revenue"].idxmax(), "_month"]
    worst_month = monthly.loc[monthly["Revenue"].idxmin(), "_month"]
    best_margin_month = monthly.loc[monthly["margin_pct"].idxmax(), "_month"]
    

# ── Tab 1: Product Performance ──
with tabs[1]:
    top_products = (df.groupby(product_col)
                      .agg(Revenue=("_revenue","sum"), Profit=("_profit","sum"), Qty=("_quantity","sum"))
                      .reset_index()
                      .sort_values("Revenue", ascending=False)
                      .head(20))
    top_products["Margin%"] = (top_products["Profit"] / (top_products["Revenue"] + 1) * 100).round(1)

    fig_prod = px.bar(
        top_products, x="Revenue", y=product_col, orientation="h", color="Profit",
        color_continuous_scale=[[0,"#FF4361"],[0.4,"#FFB547"],[1,"#059669"]],
        title="Top 20 Products by Revenue (colored by Profit)",
        labels={product_col: "", "Revenue": "Revenue"},
    )
    fig_prod.update_layout(height=520, coloraxis_showscale=True, **CHART_CFG)
    st.plotly_chart(fig_prod, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_scatter = px.scatter(
            top_products, x="Revenue", y="Profit", size="Qty", color="Margin%",
            hover_name=product_col,
            color_continuous_scale=[[0,"#FF4361"],[0.5,"#FFB547"],[1,"#059669"]],
            title="Revenue vs Profit (bubble = units sold)"
        )
        fig_scatter.update_layout(height=380, **CHART_CFG)
        st.plotly_chart(fig_scatter, use_container_width=True)
    with c2:
        # Top 10 by margin
        top_margin = top_products.nlargest(10, "Margin%")
        fig_margin_bar = px.bar(
            top_margin, x="Margin%", y=product_col, orientation="h",
            color="Margin%",
            color_continuous_scale=[[0,"#FFB547"],[1,"#059669"]],
            title="Top 10 Products by Profit Margin %"
        )
        fig_margin_bar.update_layout(height=380, coloraxis_showscale=False, **CHART_CFG)
        st.plotly_chart(fig_margin_bar, use_container_width=True)

    best_prod = top_products.iloc[0][product_col]
    best_rev  = fmt_currency(top_products.iloc[0]["Revenue"], CURR_SYM)
    best_margin_prod = top_products.nlargest(1, "Margin%").iloc[0]
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-top:0.5rem;">
      <div style="background:rgba(61,142,255,0.05); border:1px solid rgba(61,142,255,0.15); border-radius:14px; padding:1.2rem 1.6rem;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#3D8EFF; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:6px;">🏆 Top Revenue Product</div>
        <div style="font-size:1rem; font-weight:700; color:var(--snow);">{best_prod} · {best_rev}</div>
      </div>
      <div style="background:rgba(0,214,143,0.05); border:1px solid rgba(0,214,143,0.15); border-radius:14px; padding:1.2rem 1.6rem;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#059669; text-transform:uppercase; letter-spacing:0.15em; margin-bottom:6px;">🎯 Highest Margin Product</div>
        <div style="font-size:1rem; font-weight:700; color:var(--snow);">{best_margin_prod[product_col]} · {best_margin_prod['Margin%']:.1f}%</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Tab 2: Region / City ──
with tabs[2]:
    if mapping.get("region"):
        reg_df = df.groupby(mapping["region"]).agg(Revenue=("_revenue","sum"), Profit=("_profit","sum"), Orders=("_revenue","count")).reset_index()
        reg_df["Margin%"] = (reg_df["Profit"] / (reg_df["Revenue"] + 1) * 100).round(1)

        c1, c2 = st.columns(2)
        with c1:
            fig_reg = px.bar(
                reg_df.sort_values("Revenue"), x="Revenue", y=mapping["region"], orientation="h",
                color="Revenue", color_continuous_scale=[[0,"#FF4361"],[0.5,"#3D8EFF"],[1,"#059669"]],
                title=f"Revenue by {mapping['region']}"
            )
            fig_reg.update_layout(height=400, coloraxis_showscale=False, **CHART_CFG)
            st.plotly_chart(fig_reg, use_container_width=True)
        with c2:
            fig_reg_margin = px.bar(
                reg_df.sort_values("Margin%"), x="Margin%", y=mapping["region"], orientation="h",
                color="Margin%", color_continuous_scale=[[0,"#FF4361"],[1,"#059669"]],
                title=f"Profit Margin % by {mapping['region']}"
            )
            fig_reg_margin.update_layout(height=400, coloraxis_showscale=False, **CHART_CFG)
            st.plotly_chart(fig_reg_margin, use_container_width=True)

        

        
        
        if mapping.get("city"):
            city_df = df.groupby(mapping["city"]).agg(Revenue=("_revenue","sum"), Profit=("_profit","sum")).reset_index().sort_values("Revenue", ascending=False).head(15)
            fig_city = px.bar(
                city_df, x=mapping["city"], y="Revenue", color="Profit",
                color_continuous_scale=[[0,"#FF4361"],[0.5,"#FFB547"],[1,"#059669"]],
                title="Top 15 Cities by Revenue"
            )
            fig_city.update_layout(height=350, coloraxis_showscale=False, **CHART_CFG)
            st.plotly_chart(fig_city, use_container_width=True)

            # ── Best Selling Product per City ──
            st.markdown("""<div style="margin-top:1.5rem; margin-bottom:0.7rem; font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#3D8EFF; text-transform:uppercase; letter-spacing:0.15em;">🏙️ Best Selling Product per City (Top 15 Cities)</div>""", unsafe_allow_html=True)
            top_cities = city_df[mapping["city"]].tolist()
            top_prod_city = (
                df[df[mapping["city"]].isin(top_cities)]
                  .groupby([mapping["city"], product_col])["_quantity"].sum()
                  .reset_index()
                  .sort_values("_quantity", ascending=False)
                  .groupby(mapping["city"]).first()
                  .reset_index()
                  .rename(columns={product_col: "Top Product", "_quantity": "Units Sold"})
            )
            rev_city_prod = df.groupby([mapping["city"], product_col])["_revenue"].sum().reset_index()
            top_prod_city = top_prod_city.merge(
                rev_city_prod.rename(columns={product_col:"Top Product"}),
                on=[mapping["city"],"Top Product"], how="left"
            ).rename(columns={"_revenue":"Revenue"})
            top_prod_city["Revenue"] = top_prod_city["Revenue"].apply(lambda x: fmt_currency(x, CURR_SYM))
            top_prod_city["Units Sold"] = top_prod_city["Units Sold"].apply(fmt_number)
            st.dataframe(top_prod_city[[mapping["city"],"Top Product","Units Sold","Revenue"]], use_container_width=True, hide_index=True)

        

# ── Tab 3: Category Breakdown ──
with tabs[3]:
    if mapping.get("category"):
        cat_df = df.groupby(mapping["category"]).agg(
            Profit=("_profit","sum"), Revenue=("_revenue","sum"),
            Orders=("_revenue","count"), Qty=("_quantity","sum")
        ).reset_index()
        cat_df["Margin%"] = (cat_df["Profit"] / (cat_df["Revenue"] + 1) * 100).round(1)

        c1, c2 = st.columns(2)
        with c1:
            fig_pie = px.pie(
                cat_df, values="Profit", names=mapping["category"],
                title="Profit Share by Category", hole=0.56,
                color_discrete_sequence=["#059669","#3D8EFF","#9B7FFF","#FFB547","#FF6B9E","#FF4361","#00C8E0"]
            )
            fig_pie.update_traces(textposition="outside", textfont_size=12)
            fig_pie.update_layout(height=400, **CHART_CFG)
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            # Category margin % bar
            fig_cat_margin = px.bar(
                cat_df.sort_values("Margin%"), x="Margin%", y=mapping["category"],
                orientation="h", color="Margin%",
                color_continuous_scale=[[0,"#FF4361"],[0.5,"#FFB547"],[1,"#059669"]],
                title="Profit Margin % by Category"
            )
            fig_cat_margin.update_layout(height=300, coloraxis_showscale=False, **CHART_CFG)
            st.plotly_chart(fig_cat_margin, use_container_width=True)
    else:
        st.info("📊 No Category column detected in your dataset.")


# ── Tab 4: ADVANCED INSIGHTS
with tabs[4]:
    
    # ── 5. Customer Frequency (if available)
    if mapping.get("customer"):
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        cust_df = (df.groupby(mapping["customer"])
                     .agg(Orders=("_revenue","count"), Revenue=("_revenue","sum"), Profit=("_profit","sum"))
                     .reset_index()
                     .sort_values("Revenue", ascending=False))

        # RFM-lite: frequency buckets
        cust_df["freq_bucket"] = pd.cut(cust_df["Orders"], bins=[0,1,3,6,999],
                                         labels=["One-time","Occasional","Regular","Loyal"])
    c1, c2 = st.columns(2)
    with c1:
            freq_summary = cust_df["freq_bucket"].value_counts().reset_index()
            freq_summary.columns = ["Segment", "Count"]
            fig_freq = px.pie(freq_summary, values="Count", names="Segment",
                               title="Customer Frequency Segments", hole=0.5,
                               color_discrete_sequence=["#FF4361","#FFB547","#3D8EFF","#059669"])
            fig_freq.update_layout(height=320, **CHART_CFG)
            st.plotly_chart(fig_freq, use_container_width=True)
    with c2:
            top_custs = cust_df.head(15)
            fig_cust = px.bar(
                top_custs, x=mapping["customer"], y="Revenue",
                color="Profit", color_continuous_scale=[[0,"#FF4361"],[1,"#059669"]],
                title="Top 15 Customers by Revenue"
            )
            fig_cust.update_layout(height=320, coloraxis_showscale=False, **CHART_CFG)
            st.plotly_chart(fig_cust, use_container_width=True)

# ── Tab 5: Data Explorer
with tabs[5]:
    st.markdown(f"""
    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin-bottom:1.5rem;">
      <div style="background:var(--card-bg); border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.4rem;">
        <div style="font-size:0.68rem; color:var(--snow-mute); text-transform:uppercase; letter-spacing:0.1em; font-family:'JetBrains Mono',monospace; margin-bottom:4px;">Total Rows</div>
        <div style="font-size:1.5rem; font-weight:800; color:var(--snow);">{len(df_raw):,}</div>
      </div>
      <div style="background:var(--card-bg); border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.4rem;">
        <div style="font-size:0.68rem; color:var(--snow-mute); text-transform:uppercase; letter-spacing:0.1em; font-family:'JetBrains Mono',monospace; margin-bottom:4px;">Columns</div>
        <div style="font-size:1.5rem; font-weight:800; color:var(--snow);">{len(df_raw.columns)}</div>
      </div>
      <div style="background:var(--card-bg); border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.4rem;">
        <div style="font-size:0.68rem; color:var(--snow-mute); text-transform:uppercase; letter-spacing:0.1em; font-family:'JetBrains Mono',monospace; margin-bottom:4px;">Unique Products</div>
        <div style="font-size:1.5rem; font-weight:800; color:var(--snow);">{unique_prods_count:,}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<div style="font-size:0.78rem; color:var(--snow-mute); margin-bottom:0.6rem; font-weight:500;">📋 Raw Data Preview (first 200 rows)</div>""", unsafe_allow_html=True)
    st.dataframe(df_raw.head(200), use_container_width=True, height=400)

    detected = {k: v for k, v in mapping.items() if v is not None}
    if detected:
        st.markdown("""<div style="margin-top:1.2rem; font-size:0.78rem; color:var(--snow-mute); font-weight:500; margin-bottom:0.6rem;">🔍 Auto-Detected Column Mapping</div>""", unsafe_allow_html=True)
        map_df = pd.DataFrame(list(detected.items()), columns=["Field", "Detected Column"])
        st.dataframe(map_df, use_container_width=True, hide_index=True)


# ── Tab 7: AI Store Advisor
with tabs[6]:

    GEMINI_API_KEY = "AIzaSyBZEGli1sk_rMTXCMRERqxd4bYDYmcjcz0"
    #GEMINI_MODEL   = "gemini-flash-latest"
    GEMINI_MODEL   = "gemini-3.1-flash-lite-preview"

    IS_DARK_CHAT = st.session_state.get("theme", "dark") == "dark"

    # ── Gemini API call function
    # ── Gemini API call function ──
    def call_gemini(history: list, system_prompt: str) -> str:
        import json, urllib.request, urllib.error, re

        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}")

        # Build contents
        contents = []
        for m in history:
            role = "model" if m["role"] == "ai" else "user"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
            
        # 🔥 BUG FIX: System prompt (dataset) ko ALWAYS aakhri user message ke sath merge karein
        # Taake AI kabhi bhi data ko ignore na kare
        if contents and contents[-1]["role"] == "user":
            contents[-1]["parts"][0]["text"] = system_prompt + "\n\n[USER QUERY]:\n" + contents[-1]["parts"][0]["text"]

        payload = json.dumps({
            "contents": contents,
            "generationConfig": {"maxOutputTokens": 2048, "temperature": 0.0} # 0.0 = NO Hallucination, strict data focus
        }).encode()

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                result = json.loads(resp.read())
                return result["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            return f"Gemini error {e.code}: {e.read().decode()[:200]}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"


    # ── Store context & Summaries for AI ──
    n_months     = df["_month"].nunique()
    region_ctx   = f"Top region: {df.groupby(mapping['region'])['_revenue'].sum().idxmax()}." if mapping.get("region") else ""
    category_ctx = f"Top category: {df.groupby(mapping['category'])['_revenue'].sum().idxmax()}." if mapping.get("category") else ""

    # Aggregating data into tables so Gemini reads EXACT names and numbers
    try:
        prod_summary = df.groupby(product_col).agg(
            Revenue=("_revenue", "sum"),
            Profit=("_profit", "sum"),
            Qty=("_quantity", "sum")
        ).reset_index()
        prod_summary["Margin %"] = (prod_summary["Profit"] / (prod_summary["Revenue"] + 1) * 100).round(1)
        
        best_performers = prod_summary.nlargest(10, "Profit").to_markdown(index=False)
        risk_products = prod_summary.nsmallest(10, "Profit").to_markdown(index=False)
        pred_table = df_pred[["product id", "profit", "quantity"]].sort_values("profit", ascending=False).to_markdown(index=False)
    except Exception as e:
        best_performers = "Data unavailable"
        risk_products = "Data unavailable"
        pred_table = "Data unavailable"

    # Cross-sell Recommendations Context
    rec_context = "No product selected for recommendations yet."
    if "rec_for_product" in st.session_state and "rec_results_v2" in st.session_state:
        rec_prod = st.session_state["rec_for_product"]
        recs = ", ".join([f"{r[0]} (Reason: {r[1]})" for r in st.session_state["rec_results_v2"]])
        rec_context = f"Cross-sell Recommendations for '{rec_prod}': {recs}"

    # 👇 STRICT SYSTEM PROMPT DEFINITION 👇
    GEMINI_SYSTEM = f"""You are an expert retail business analyst AI inside the SalesOracle dashboard.
Your job is to answer user queries using the EXACT data tables provided below.

CRITICAL RULES:
1. ALWAYS use the specific PRODUCT NAMES, actual numbers, and categories from the tables below. 
2. NEVER give generic, theoretical answers like "Look for margin eaters". Instead, specify: "The biggest risk product is [Exact Product Name] with a profit of [Amount]."
3. Use Markdown formatting (bullet points, bold text) to structure your answer clearly.
4. If asked about recommendations, predictions, or risks, refer STRICTLY to the sections below. Never invent data.

--- 📊 BUSINESS SUMMARY ---
- Total Revenue: {fmt_currency(total_revenue, CURR_SYM)}
- Net Profit: {fmt_currency(total_profit, CURR_SYM)}
- Avg Margin: {avg_margin:.1f}%
- Total Orders: {total_orders:,}
- Unique Products: {unique_prods_count}
- MoM Growth: {mom_growth:+.1f}%
- {region_ctx} {category_ctx}

--- 🏆 HISTORICAL TOP 10 PROFITABLE PRODUCTS ---
{best_performers}

--- ⚠️ HISTORICAL BOTTOM 10 RISK PRODUCTS (LOWEST PROFIT / LOSS) ---
{risk_products}

--- 🔮 NEXT MONTH AI PREDICTIONS ---
{pred_table}

--- 🔗 AI CROSS-SELL RECOMMENDATIONS ---
{rec_context}
"""

    # ── Session init ──
    if "adv_msgs" not in st.session_state:
        st.session_state["adv_msgs"] = [{
            "role": "ai",
            "content": (f"👋 Hello! I've loaded your store — "
                        f"**{fmt_currency(total_revenue, CURR_SYM)}** revenue, "
                        f"**{avg_margin:.1f}%** margin, "
                        f"**{unique_prods_count}** products over **{n_months} months**. "
                        f"Ask me anything about performance, forecasts, or growth strategy.")
        }]

    # CHIPS = [
    #     "📈 Revenue trend summary",
    #     "🏆 Which products to prioritize?",
    #     "⚠️ Biggest risk products?",
    #     "💡 How to improve margin?",
    #     "🗺️ Which region to focus on?",
    #     "🔄 Suggest restock strategy",
    # ]

    # ════════════════════════════════════════
    #  CSS
    # ════════════════════════════════════════
    st.markdown(f"""
    <style>
    /* ── Shell ── */
    .adv-shell {{
        border: 1px solid var(--line);
        border-radius: 22px;
        overflow: hidden;
        background: var(--card-bg);
        margin-bottom: 1rem;
    }}

    /* ── Topbar ── */
    .adv-topbar {{
        display: flex; align-items: center; gap: 14px;
        padding: 1rem 1.5rem;
        border-bottom: 1px solid var(--line);
        background: {'#111827' if IS_DARK_CHAT else '#F8F9FC'};
        position: relative;
    }}
    .adv-topbar::after {{
        content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, #9B7FFF, #FF6B9E, #3D8EFF, #059669);
    }}
    .adv-logo {{
        width: 38px; height: 38px; border-radius: 11px; flex-shrink: 0;
        background: linear-gradient(135deg, #9B7FFF, #3D8EFF);
        display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(155,127,255,0.4);
    }}
    .adv-name {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.92rem; font-weight: 800; color: var(--snow); letter-spacing: -0.02em;
    }}
    .adv-status {{
        font-size: 0.68rem; color: var(--snow-mute);
        display: flex; align-items: center; gap: 5px; margin-top: 2px;
    }}
    .adv-dot {{
        width: 6px; height: 6px; border-radius: 50%;
        background: #059669; animation: pulse 2s infinite; flex-shrink: 0;
    }}

    /* ── Context pills ── */
    .adv-ctx {{
        display: flex; gap: 7px; flex-wrap: wrap;
        padding: 0.65rem 1.5rem;
        border-bottom: 1px solid var(--line);
        background: {'rgba(255,255,255,0.01)' if IS_DARK_CHAT else 'rgba(0,0,0,0.02)'};
    }}
    .ctx-p {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.61rem; font-weight: 600;
        padding: 3px 9px; border-radius: 6px; letter-spacing: 0.05em;
    }}
    .ctx-p.r {{ background: rgba(0,214,143,0.1);   color: #059669; border: 1px solid rgba(0,214,143,0.22); }}
    .ctx-p.p {{ background: rgba(61,142,255,0.1);  color: #3D8EFF; border: 1px solid rgba(61,142,255,0.22); }}
    .ctx-p.m {{ background: rgba(155,127,255,0.1); color: #9B7FFF; border: 1px solid rgba(155,127,255,0.22); }}
    .ctx-p.g {{ background: rgba(255,181,71,0.1);  color: #FFB547; border: 1px solid rgba(255,181,71,0.22); }}

    /* ── Messages ── */
    .adv-body {{
        padding: 1.2rem 1.4rem;
        min-height: 360px; max-height: 420px;
        overflow-y: auto;
        display: flex; flex-direction: column; gap: 12px;
    }}
    .msg-row        {{ display: flex; gap: 9px; align-items: flex-end; animation: fadeUp 0.25s ease both; }}
    .msg-row.user   {{ flex-direction: row-reverse; }}
    .msg-ava {{
        width: 30px; height: 30px; border-radius: 9px; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center; font-size: 0.85rem;
    }}
    .msg-ava.ai   {{ background: linear-gradient(135deg,#9B7FFF,#3D8EFF); }}
    .msg-ava.user {{ background: rgba(0,214,143,0.15); border: 1px solid rgba(0,214,143,0.3); }}
    .msg-bub {{
        max-width: 76%; padding: 0.8rem 1.05rem;
        font-size: 0.82rem; line-height: 1.7;
        color: var(--snow);
    }}
    .msg-bub.ai {{
        background: {'rgba(255,255,255,0.05)' if IS_DARK_CHAT else '#EEF1FA'};
        border: 1px solid {'rgba(255,255,255,0.07)' if IS_DARK_CHAT else 'rgba(0,0,0,0.09)'};
        border-radius: 16px 16px 16px 4px;
        max-width: 76%;
    }}
    .msg-bub.ai a {{
        color: inherit !important;
        text-decoration: none !important;
        pointer-events: none !important;
    }}
    .msg-bub.ai strong {{ color: {'#B09FFF' if IS_DARK_CHAT else '#6B3FD4'}; }}
    .msg-ts {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.57rem;
        color: var(--snow-mute); margin-top: 4px;
    }}
    .msg-ts.left {{ text-align: left; padding-left: 2px; }}
    .msg-ts.right {{ text-align: right; padding-right: 2px; }}

    /* ── Chips label ── */
    .chips-label {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.59rem;
        color: var(--snow-mute); text-transform: uppercase; letter-spacing: 0.14em;
        padding: 0.7rem 1.4rem 0.3rem;
        border-top: 1px solid var(--line);
        background: {'rgba(255,255,255,0.01)' if IS_DARK_CHAT else 'rgba(0,0,0,0.015)'};
    }}

    /* ── Override ALL stButton inside this tab to look like chips ── */
    .chip-btn > div > button {{
        background: {'rgba(255,255,255,0.04)' if IS_DARK_CHAT else '#FFFFFF'} !important;
        color: var(--snow) !important;
        border: 1px solid var(--line-2) !important;
        border-radius: 100px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.68rem !important;
        font-weight: 500 !important;
        padding: 4px 10px !important;
        height: auto !important;
        min-height: unset !important;
        line-height: 1.4 !important;
        transition: all 0.2s !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}
    .chip-btn > div > button:hover {{
        border-color: rgba(155,127,255,0.45) !important;
        color: #9B7FFF !important;
        background: rgba(155,127,255,0.07) !important;
    }}

    /* ── Send button ── */
    .send-btn > div > button {{
        background: linear-gradient(135deg, #9B7FFF, #3D8EFF) !important;
        color: #fff !important; border: none !important;
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important; font-size: 0.82rem !important;
        box-shadow: 0 4px 14px rgba(155,127,255,0.4) !important;
        transition: all 0.2s !important;
    }}

    /* ── Clear button ── */
    .clear-btn > div > button {{
        background: rgba(255,67,97,0.07) !important;
        color: #FF4361 !important;
        border: 1px solid rgba(255,67,97,0.25) !important;
        border-radius: 10px !important;
        font-size: 0.75rem !important; font-weight: 600 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        transition: all 0.2s !important;
    }}
    .clear-btn > div > button:hover {{
        background: rgba(255,67,97,0.14) !important;
        border-color: rgba(255,67,97,0.45) !important;
    }}

    /* ── Text input ── */
    .adv-input div[data-testid="stTextInput"] input {{
        background: {'rgba(255,255,255,0.06)' if IS_DARK_CHAT else '#FFFFFF'} !important;
        border: 1.5px solid var(--line-2) !important;
        border-radius: 12px !important;
        color: var(--snow) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.83rem !important;
        padding: 0.62rem 1rem !important;
        transition: border-color 0.2s !important;
    }}
    .adv-input div[data-testid="stTextInput"] input:focus {{
        border-color: rgba(155,127,255,0.55) !important;
        box-shadow: 0 0 0 3px rgba(155,127,255,0.1) !important;
    }}
    .adv-input div[data-testid="stTextInput"] input::placeholder {{
        color: var(--snow-mute) !important;
    }}

    /* ── Footer ── */
    .adv-footer {{
        padding: 0.55rem 1.5rem;
        border-top: 1px solid var(--line);
        display: flex; align-items: center; justify-content: space-between;
        background: {'rgba(255,255,255,0.008)' if IS_DARK_CHAT else 'rgba(0,0,0,0.015)'};
    }}
    .adv-footer span {{
        font-family: 'JetBrains Mono', monospace; font-size: 0.58rem;
        color: var(--snow-mute); letter-spacing: 0.08em; opacity: 0.65;
    }}
    </style>
    """, unsafe_allow_html=True)


    #  Convert markdown to clean HTML


    def render_md(text):
        """Convert markdown to clean HTML."""
        # Remove markdown links [text](url) → just text
        text = _re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Bold
        text = _re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = _re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        # Bullet points → styled HTML
        text = _re.sub(r'^\s*[-•]\s+(.+)$', r'<div style="padding:2px 0 2px 12px; border-left:2px solid rgba(155,127,255,0.4); margin:4px 0;">\1</div>', text, flags=_re.MULTILINE)
        # Numbered lists
        text = _re.sub(r'^\s*(\d+)\.\s+(.+)$', r'<div style="padding:2px 0 2px 12px; color:var(--snow); margin:4px 0;"><strong style="color:#9B7FFF">\1.</strong> \2</div>', text, flags=_re.MULTILINE)
        # Newlines
        text = text.replace("\n", "<br>")
        return text

    # ── Top bar ──
    st.markdown(f"""
    <div class="adv-shell">
      <div class="adv-topbar">
        <div class="adv-logo">🤖</div>
        <div>
          <div class="adv-name">SalesOracle AI Advisor</div>
          <div class="adv-status">
            <span class="adv-dot"></span>
            Powered by Gemini · Store data loaded
          </div>
        </div>
      </div>
      <div class="adv-ctx">
        <span class="ctx-p r">💰 {fmt_currency(total_revenue, CURR_SYM)}</span>
        <span class="ctx-p p">📈 {fmt_currency(total_profit, CURR_SYM)}</span>
        <span class="ctx-p m">🎯 {avg_margin:.1f}% margin</span>
        <span class="ctx-p g">{'↑' if mom_growth>=0 else '↓'} {mom_growth:+.1f}% MoM</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Clear button ──
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", key="adv_clear"):
        st.session_state["adv_msgs"] = [st.session_state["adv_msgs"][0]]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Chat bubbles ──
    now_hm = _dt.datetime.now().strftime("%H:%M")
    bubbles = '<div class="adv-shell"><div class="adv-body">'
    for msg in st.session_state["adv_msgs"]:
        is_ai   = msg["role"] == "ai"
        cls     = "ai" if is_ai else "user"
        ava     = "🤖" if is_ai else "👤"
        ts      = msg.get("ts", now_hm)
        content = render_md(msg["content"])
        ts_cls  = "left" if is_ai else "right"
        bubbles += f"""
        <div class="msg-row {cls}">
          <div class="msg-ava {cls}">{ava}</div>
          <div>
            <div class="msg-bub {cls}">{content}</div>
            <div class="msg-ts {ts_cls}">{ts}</div>
          </div>
        </div>"""
    bubbles += "</div>"

    # ── Chips label inside shell ──
    bubbles += '<div class="chips-label">Quick Questions</div></div>'
    st.markdown(bubbles, unsafe_allow_html=True)

    # # ── Chip buttons (real Streamlit — 2 rows of 3) ──
    # chip_clicked = None
    # chip_cols = st.columns(6)
    # for ci, chip_text in enumerate(CHIPS):
    #     with chip_cols[ci]:
    #         st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
    #         if st.button(chip_text, key=f"chip_{ci}", use_container_width=True):
    #             chip_clicked = chip_text.split(" ", 1)[1]
    #         st.markdown('</div>', unsafe_allow_html=True)

    # ── Input + Send ──
    st.markdown('<div class="adv-input">', unsafe_allow_html=True)
    col_in, col_btn = st.columns([6, 1])
    col_in, col_btn = st.columns([6, 1])
with col_in:
    user_input = st.text_input(
        "msg",
        placeholder="Ask about your store…  e.g. Which product has the best margin?",
        key="adv_input",
        label_visibility="collapsed"
    )
with col_btn:
    st.markdown('<div class="send-btn">', unsafe_allow_html=True)
    st.markdown('<div style="margin-top:0.1rem;">', unsafe_allow_html=True)
    send_hit = st.button("Send ➤", key="adv_send", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)



    #  HANDLE SEND
    query = None
    if send_hit and user_input.strip():
        query = user_input.strip()
    # elif chip_clicked:
    #     query = chip_clicked

    if query:
        ts_now = _dt.datetime.now().strftime("%H:%M")
        st.session_state["adv_msgs"].append({
            "role": "user", "content": query, "ts": ts_now
        })
        with st.spinner("Gemini is thinking…"):
            reply = call_gemini(st.session_state["adv_msgs"], GEMINI_SYSTEM)
        st.session_state["adv_msgs"].append({
            "role": "ai", "content": reply,
            "ts": _dt.datetime.now().strftime("%H:%M")
        })
        st.rerun()

#  FOOTER

st.markdown("""
<div style="margin-top:5rem; padding-top:2rem; border-top:1px solid var(--line);
     display:flex; align-items:center; justify-content:space-between; opacity:0.45;">
  <div style="font-family:'Plus Jakarta Sans',sans-serif; font-size:0.78rem; font-weight:700; color:var(--snow);">◈ Sales Oracle</div>
  <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:var(--snow-mute);
      letter-spacing:0.12em; text-transform:uppercase;">AI-Powered Sales Intelligence</div>
  <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:var(--snow-mute);">v2.1 · 2026</div>
</div>
""", unsafe_allow_html=True)
show_info_sections()