import streamlit as st
import joblib
import numpy as np
import time
import os
from datetime import datetime

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FraudShield · Detection System",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Session state init ─────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# ── Theme variables ────────────────────────────────────────────────────────────
if st.session_state.dark_mode:
    theme = {
        "bg":        "#0a0c10",
        "surface":   "#111318",
        "border":    "#1e2230",
        "text":      "#e8eaf0",
        "muted":     "#5a6075",
        "input_bg":  "#111318",
        "card_bg":   "#111318",
        "hero_bg1":  "#0d1117",
        "hero_bg2":  "#111827",
        "toggle_bg": "#1e2230",
        "toggle_text": "#e8eaf0",
        "hero_glow": "rgba(0,229,255,.12)",
        "stat_fill_opacity": "rgba(255,255,255,.03)",
    }
else:
    theme = {
        "bg":        "#f0f4f8",
        "surface":   "#ffffff",
        "border":    "#d1dbe8",
        "text":      "#1a202c",
        "muted":     "#718096",
        "input_bg":  "#ffffff",
        "card_bg":   "#ffffff",
        "hero_bg1":  "#e8f0fe",
        "hero_bg2":  "#f0f4ff",
        "toggle_bg": "#e2e8f0",
        "toggle_text": "#1a202c",
        "hero_glow": "rgba(0,100,255,.08)",
        "stat_fill_opacity": "rgba(0,0,0,.03)",
    }

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {{
    --bg:        {theme["bg"]};
    --surface:   {theme["surface"]};
    --border:    {theme["border"]};
    --accent:    #00e5ff;
    --accent2:   #7b61ff;
    --danger:    #ff4c6a;
    --success:   #00e096;
    --warn:      #ffb830;
    --text:      {theme["text"]};
    --muted:     {theme["muted"]};
    --input-bg:  {theme["input_bg"]};
    --card-glow: 0 0 40px rgba(0,229,255,.06);
}}

html, body, [data-testid="stAppViewContainer"] {{
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}}
[data-testid="stHeader"] {{ background: transparent !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
footer {{ display: none !important; }}
.block-container {{ padding: 2rem 1.5rem 4rem !important; max-width: 860px !important; }}

/* ── Top bar ── */
.top-bar {{
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: .75rem;
    margin-bottom: 1.5rem;
}}
.theme-toggle {{
    background: {theme["toggle_bg"]};
    border: 1px solid var(--border);
    border-radius: 100px;
    padding: .45rem 1.1rem;
    font-family: 'Space Mono', monospace;
    font-size: .72rem;
    letter-spacing: .08em;
    color: {theme["toggle_text"]};
    cursor: pointer;
    transition: all .2s;
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    text-decoration: none;
}}
.theme-toggle:hover {{ border-color: var(--accent); color: var(--accent); }}

/* ── Hero ── */
.hero {{
    position: relative;
    text-align: center;
    padding: 3.5rem 2rem 2.5rem;
    margin-bottom: 2rem;
    border-radius: 20px;
    background: linear-gradient(135deg, {theme["hero_bg1"]} 0%, {theme["hero_bg2"]} 100%);
    border: 1px solid var(--border);
    overflow: hidden;
}}
.hero::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 50% 0%, {theme["hero_glow"]} 0%, transparent 70%);
}}
.hero-badge {{
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: .68rem;
    letter-spacing: .18em;
    color: var(--accent);
    border: 1px solid rgba(0,229,255,.35);
    border-radius: 100px;
    padding: .3rem 1rem;
    margin-bottom: 1.2rem;
    background: rgba(0,229,255,.05);
}}
.hero h1 {{
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -.02em;
    margin: 0 0 .5rem;
    background: linear-gradient(135deg, {'#ffffff' if st.session_state.dark_mode else '#1a202c'} 30%, var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.hero p {{ color: var(--muted); font-size: .95rem; font-weight: 400; margin: 0; }}

/* ── Stats row ── */
.stats-row {{ display: flex; gap: 1rem; margin-bottom: 2rem; }}
.stat-card {{
    flex: 1;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: var(--card-glow);
    transition: border-color .2s;
}}
.stat-card:hover {{ border-color: rgba(0,229,255,.3); }}
.stat-card::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent2), var(--accent));
    border-radius: 0 0 16px 16px;
}}
.stat-label {{
    font-family: 'Space Mono', monospace;
    font-size: .62rem;
    letter-spacing: .14em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: .5rem;
}}
.stat-value {{ font-size: 2rem; font-weight: 800; color: var(--accent); line-height: 1; }}

/* ── Input ── */
.input-label {{
    font-family: 'Space Mono', monospace;
    font-size: .72rem;
    letter-spacing: .12em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: .5rem;
}}
[data-testid="stTextInput"] input {{
    background: var(--input-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: .85rem !important;
    padding: .85rem 1.1rem !important;
    transition: border-color .2s !important;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,.1) !important;
}}
[data-testid="stTextInput"] label {{ display: none !important; }}

/* ── Buttons ── */
[data-testid="stButton"] > button {{
    width: 100%;
    background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
    color: #000 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: .04em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: .85rem 2rem !important;
    cursor: pointer !important;
    transition: opacity .2s, transform .1s !important;
    margin-top: .4rem !important;
}}
[data-testid="stButton"] > button:hover {{ opacity: .88 !important; transform: translateY(-1px) !important; }}
[data-testid="stButton"] > button:active {{ transform: translateY(0) !important; }}

/* Clear button override */
.clear-btn [data-testid="stButton"] > button {{
    background: {theme["toggle_bg"]} !important;
    color: var(--danger) !important;
    border: 1px solid rgba(255,76,106,.3) !important;
}}
.clear-btn [data-testid="stButton"] > button:hover {{
    background: rgba(255,76,106,.08) !important;
    border-color: rgba(255,76,106,.6) !important;
}}

/* Clear history button */
.clear-history-btn [data-testid="stButton"] > button {{
    background: transparent !important;
    color: var(--danger) !important;
    border: 1px solid rgba(255,76,106,.3) !important;
    font-size: .68rem !important;
    font-family: 'Space Mono', monospace !important;
    letter-spacing: .08em !important;
    padding: .25rem .8rem !important;
    border-radius: 8px !important;
    margin-top: 0 !important;
    width: auto !important;
    line-height: 1.4 !important;
}}
.clear-history-btn [data-testid="stButton"] > button:hover {{
    background: rgba(255,76,106,.08) !important;
    border-color: rgba(255,76,106,.65) !important;
    transform: none !important;
}}

/* Theme toggle button override */
.theme-btn [data-testid="stButton"] > button {{
    background: {theme["toggle_bg"]} !important;
    color: {theme["toggle_text"]} !important;
    border: 1px solid var(--border) !important;
    font-size: .8rem !important;
    padding: .55rem 1.2rem !important;
    margin-top: 0 !important;
    width: auto !important;
}}
.theme-btn [data-testid="stButton"] > button:hover {{
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}}

/* ── Result cards ── */
.result-card {{
    border-radius: 16px;
    padding: 1.8rem 2rem;
    margin-top: 1.5rem;
    border: 1px solid;
    position: relative;
    overflow: hidden;
    animation: slideUp .35s ease;
}}
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(14px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.result-fraud {{ background: rgba(255,76,106,.06); border-color: rgba(255,76,106,.4); }}
.result-safe  {{ background: rgba(0,224,150,.06);  border-color: rgba(0,224,150,.4); }}
.result-warn  {{ background: rgba(255,184,48,.06); border-color: rgba(255,184,48,.4); }}
.result-icon  {{ font-size: 2.2rem; margin-bottom: .6rem; }}
.result-title {{ font-size: 1.35rem; font-weight: 800; margin-bottom: .3rem; }}
.result-fraud .result-title {{ color: var(--danger); }}
.result-safe  .result-title {{ color: var(--success); }}
.result-warn  .result-title {{ color: var(--warn); }}
.result-sub {{
    font-family: 'Space Mono', monospace;
    font-size: .8rem;
    color: var(--muted);
    margin-bottom: 1.2rem;
}}

.risk-bar-wrap {{
    background: rgba({'255,255,255' if st.session_state.dark_mode else '0,0,0'},.06);
    border-radius: 100px;
    height: 8px;
    overflow: hidden;
    margin-bottom: .4rem;
}}
.risk-bar-fill {{ height: 100%; border-radius: 100px; }}
.fill-fraud {{ background: linear-gradient(90deg, var(--warn), var(--danger)); }}
.fill-safe  {{ background: linear-gradient(90deg, var(--accent), var(--success)); }}
.fill-warn  {{ background: linear-gradient(90deg, var(--accent2), var(--warn)); }}
.risk-pct {{
    font-family: 'Space Mono', monospace;
    font-size: .75rem;
    color: var(--muted);
    text-align: right;
}}

.detail-grid {{ display: flex; gap: 1rem; margin-top: 1.2rem; }}
.detail-item {{
    flex: 1;
    background: {theme["stat_fill_opacity"]};
    border-radius: 10px;
    padding: .9rem 1rem;
}}
.detail-item-label {{
    font-family: 'Space Mono', monospace;
    font-size: .6rem;
    letter-spacing: .12em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: .3rem;
}}
.detail-item-val {{ font-size: 1.1rem; font-weight: 700; }}

/* ── History ── */
.history-section {{
    margin-top: 2rem;
    border-radius: 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    overflow: hidden;
}}
.history-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.4rem;
    border-bottom: 1px solid var(--border);
    background: {theme["stat_fill_opacity"]};
}}
.history-title {{
    font-family: 'Space Mono', monospace;
    font-size: .72rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
}}
.history-count {{
    font-family: 'Space Mono', monospace;
    font-size: .65rem;
    color: var(--accent);
    background: rgba(0,229,255,.08);
    border: 1px solid rgba(0,229,255,.2);
    border-radius: 100px;
    padding: .2rem .7rem;
}}
.history-item {{
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: .9rem 1.4rem;
    border-bottom: 1px solid var(--border);
    transition: background .15s;
    cursor: default;
}}
.history-item:last-child {{ border-bottom: none; }}
.history-item:hover {{ background: {theme["stat_fill_opacity"]}; }}
.h-badge {{
    font-size: .75rem;
    border-radius: 6px;
    padding: .2rem .6rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    flex-shrink: 0;
    min-width: 58px;
    text-align: center;
}}
.h-fraud {{ background: rgba(255,76,106,.15); color: #ff4c6a; }}
.h-safe  {{ background: rgba(0,224,150,.15); color: #00e096; }}
.h-warn  {{ background: rgba(255,184,48,.15); color: #ffb830; }}
.h-meta {{
    flex: 1;
    font-family: 'Space Mono', monospace;
    font-size: .72rem;
    color: var(--muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.h-time {{
    font-family: 'Space Mono', monospace;
    font-size: .65rem;
    color: var(--muted);
    flex-shrink: 0;
}}
.h-score {{
    font-family: 'Space Mono', monospace;
    font-size: .8rem;
    font-weight: 700;
    flex-shrink: 0;
    min-width: 48px;
    text-align: right;
}}
.history-empty {{
    padding: 2rem;
    text-align: center;
    font-family: 'Space Mono', monospace;
    font-size: .78rem;
    color: var(--muted);
}}

/* ── Error ── */
.err-box {{
    background: rgba(255,76,106,.06);
    border: 1px solid rgba(255,76,106,.3);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    font-family: 'Space Mono', monospace;
    font-size: .8rem;
    color: var(--danger);
    margin-top: 1rem;
    animation: slideUp .3s ease;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    margin-top: 1.5rem !important;
}}
[data-testid="stExpander"] summary {{
    font-family: 'Space Mono', monospace !important;
    font-size: .78rem !important;
    color: var(--muted) !important;
    letter-spacing: .08em !important;
}}
[data-testid="stExpander"] p, [data-testid="stExpander"] li,
[data-testid="stExpander"] td, [data-testid="stExpander"] th {{
    color: var(--text) !important;
}}
</style>
""", unsafe_allow_html=True)


# ── Model loader ───────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_model():
    model_path = "logistic_regression_model.sav"
    if not os.path.exists(model_path):
        return None
    return joblib.load(model_path)

model = load_model()

# ── Top controls (theme + clear) ───────────────────────────────────────────────
col_space, col_theme, col_clear = st.columns([6, 1.2, 1.2])

with col_theme:
    st.markdown('<div class="theme-btn">', unsafe_allow_html=True)
    toggle_label = "☀️ Light" if st.session_state.dark_mode else "🌙 Dark"
    if st.button(toggle_label, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_clear:
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🗑️ Clear", key="clear_btn"):
        st.session_state.result = None
        st.session_state.user_input = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">🛡️ &nbsp;AI-POWERED · REAL-TIME</div>
    <h1>FraudShield</h1>
    <p>Credit Card Fraud Detection &mdash; Logistic Regression Engine</p>
</div>
""", unsafe_allow_html=True)

# ── Stats row ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="stats-row">
    <div class="stat-card">
        <div class="stat-label">Overall Accuracy</div>
        <div class="stat-value">99%</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Training Accuracy</div>
        <div class="stat-value">99%</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Test Accuracy</div>
        <div class="stat-value">99%</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Features</div>
        <div class="stat-value">30</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="input-label">Transaction Features Vector</div>', unsafe_allow_html=True)
user_input = st.text_input(
    label="features",
    value=st.session_state.user_input,
    placeholder="e.g.  -1.36, 0.21, 2.53, 1.37, -0.34, …  (30 comma-separated values)",
    label_visibility="collapsed",
    key="feature_input",
)

analyze = st.button("⚡  Analyze Transaction")

# ── Analysis logic ─────────────────────────────────────────────────────────────
if analyze:
    if not user_input.strip():
        st.markdown(
            '<div class="err-box">❌ &nbsp;Please enter the 30 feature values before analyzing.</div>',
            unsafe_allow_html=True,
        )
    else:
        try:
            values = list(map(float, user_input.split(",")))
            if len(values) != 30:
                st.markdown(
                    f'<div class="err-box">❌ &nbsp;Expected <strong>30</strong> features — got <strong>{len(values)}</strong>. '
                    f'Please check your input.</div>',
                    unsafe_allow_html=True,
                )
            elif model is None:
                st.markdown(
                    '<div class="err-box">⚠️ &nbsp;Model file not found at the specified path.<br>'
                    'Running in <strong>demo mode</strong> — replace the model path to enable live predictions.</div>',
                    unsafe_allow_html=True,
                )
            else:
                with st.spinner("Running inference…"):
                    time.sleep(0.4)
                    features = np.array([values])
                    proba = model.predict_proba(features)
                    fraud_prob = proba[0][1]
                    legit_prob = proba[0][0]
                    pct        = round(fraud_prob * 100, 1)
                    bar_w      = int(fraud_prob * 100)

                if fraud_prob > 0.50:
                    card_cls, fill_cls = "result-fraud", "fill-fraud"
                    icon          = "🚨"
                    title         = "High Fraud Risk Detected"
                    sub           = "This transaction pattern matches known fraudulent activity."
                    verdict       = "BLOCK"
                    verdict_color = "#ff4c6a"
                    h_cls         = "h-fraud"
                elif fraud_prob > 0.20:
                    card_cls, fill_cls = "result-warn", "fill-warn"
                    icon          = "⚠️"
                    title         = "Suspicious Activity"
                    sub           = "Elevated risk — further verification recommended."
                    verdict       = "REVIEW"
                    verdict_color = "#ffb830"
                    h_cls         = "h-warn"
                else:
                    card_cls, fill_cls = "result-safe", "fill-safe"
                    icon          = "✅"
                    title         = "Legitimate Transaction"
                    sub           = "Low fraud probability — transaction appears normal."
                    verdict       = "APPROVE"
                    verdict_color = "#00e096"
                    h_cls         = "h-safe"

                # Save to session state
                st.session_state.result = {
                    "card_cls": card_cls, "fill_cls": fill_cls,
                    "icon": icon, "title": title, "sub": sub,
                    "verdict": verdict, "verdict_color": verdict_color,
                    "pct": pct, "bar_w": bar_w, "legit_prob": legit_prob,
                }
                st.session_state.user_input = user_input

                # Add to history
                preview = user_input[:40] + "…" if len(user_input) > 40 else user_input
                st.session_state.history.insert(0, {
                    "verdict": verdict,
                    "h_cls":   h_cls,
                    "pct":     pct,
                    "preview": preview,
                    "time":    datetime.now().strftime("%H:%M:%S"),
                })
                # Keep last 10 entries
                st.session_state.history = st.session_state.history[:10]

        except ValueError:
            st.markdown(
                '<div class="err-box">❌ &nbsp;Invalid input — ensure all 30 values are numbers separated by commas.</div>',
                unsafe_allow_html=True,
            )

# ── Render current result ──────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result
    result_html = (
        f'<div class="result-card {r["card_cls"]}">'
        f'<div class="result-icon">{r["icon"]}</div>'
        f'<div class="result-title">{r["title"]}</div>'
        f'<div class="result-sub">{r["sub"]}</div>'
        f'<div class="risk-bar-wrap">'
        f'<div class="risk-bar-fill {r["fill_cls"]}" style="width:{r["bar_w"]}%"></div>'
        f'</div>'
        f'<div class="risk-pct">Fraud probability: {r["pct"]}%</div>'
        f'<div class="detail-grid">'
        f'<div class="detail-item">'
        f'<div class="detail-item-label">Fraud Score</div>'
        f'<div class="detail-item-val" style="color:{r["verdict_color"]}">{r["pct"]}%</div>'
        f'</div>'
        f'<div class="detail-item">'
        f'<div class="detail-item-label">Legit Score</div>'
        f'<div class="detail-item-val" style="color:#00e5ff">{round(r["legit_prob"] * 100, 1)}%</div>'
        f'</div>'
        f'<div class="detail-item">'
        f'<div class="detail-item-label">Verdict</div>'
        f'<div class="detail-item-val" style="color:{r["verdict_color"]}">{r["verdict"]}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(result_html, unsafe_allow_html=True)

# ── History panel ──────────────────────────────────────────────────────────────
if st.session_state.history:
    items_html = ""
    for entry in st.session_state.history:
        score_color = (
            "#ff4c6a" if entry["verdict"] == "BLOCK"
            else "#ffb830" if entry["verdict"] == "REVIEW"
            else "#00e096"
        )
        items_html += (
            f'<div class="history-item">'
            f'<span class="h-badge {entry["h_cls"]}">{entry["verdict"]}</span>'
            f'<span class="h-meta">{entry["preview"]}</span>'
            f'<span class="h-score" style="color:{score_color}">{entry["pct"]}%</span>'
            f'<span class="h-time">{entry["time"]}</span>'
            f'</div>'
        )

    # Header row: title + count badge on left, Clear History button on right
    h_col_title, h_col_btn = st.columns([5, 1.6])
    with h_col_title:
        st.markdown(
            f'<div style="padding:.85rem 1.4rem .4rem; display:flex; align-items:center; gap:.75rem;">'
            f'<span class="history-title">📋 &nbsp;Analysis History</span>'
            f'<span class="history-count">{len(st.session_state.history)} entries</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with h_col_btn:
        st.markdown('<div class="clear-history-btn" style="padding:.65rem 1.4rem .4rem;">', unsafe_allow_html=True)
        if st.button("🗑️ Clear History", key="clear_history_btn"):
            st.session_state.history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Separator line + items
    st.markdown(
        f'<div class="history-section" style="margin-top:0; border-top-left-radius:0; border-top-right-radius:0;">'
        f'{items_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Help expander ──────────────────────────────────────────────────────────────
with st.expander("ℹ️  How to use this tool"):
    st.markdown("""
**Input format**

Paste the 30 PCA-transformed features from a credit card transaction record as a
comma-separated list:

```
-1.3598, -0.0727, 2.5363, 1.3782, -0.3383, 0.4624, 0.2396, 0.0987,
 0.3638, 0.0908, -0.5516, -0.6178, -0.9913, -0.3111, 1.4681, -0.4704,
 0.2079, 0.0258, 0.4039, 0.2514, -0.0183, 0.2778, -0.1105, 0.0669,
 0.1285, -0.1891, 0.1335, -0.0211, 149.62, 0.00
```

**Risk thresholds**

| Score | Verdict | Action |
|-------|---------|--------|
| < 20% | ✅ Legitimate | Approve |
| 20–50% | ⚠️ Suspicious | Manual review |
| > 50% | 🚨 Fraud | Block |

**Buttons**
- **⚡ Analyze Transaction** — run the model on the input values
- **🗑️ Clear** — wipe the current result from the screen (result is saved to History)
- **🗑️ Clear History** — permanently erase all entries from the Analysis History panel
- **☀️ Light / 🌙 Dark** — toggle between light and dark UI themes

**Model**: Logistic Regression trained on the public Kaggle Credit Card Fraud dataset (284,807 transactions, 0.172% fraud rate).
""")
