"""Design tokens + component CSS for the Airbnb-dark world.

One theme-agnostic set of component rules that read CSS variables; a small
`:root` block per theme supplies those variables. Toggling themes only swaps the
` :root` block, so both themes stay in lockstep by construction.
"""

import streamlit as st

# ---------------------------------------------------------------- palettes --
# Restrained strategy: near-black neutral canvas + exactly one accent.
# The accent (Airbnb "Rausch" pink-red) only ever means "this is the action /
# this is the value" -- never decoration.

DARK = {
    "bg": "#0A0A0B",
    "surface": "#141416",
    "raised": "#1E1E21",
    "border": "#2A2A2E",
    "text": "#F5F5F7",
    "text2": "#A1A1A6",
    "accent": "#FF385C",
    "accentHover": "#E11D48",
    "onAccent": "#FFFFFF",
}

# Light accent is darkened to hold contrast against white.
LIGHT = {
    "bg": "#FFFFFF",
    "surface": "#FFFFFF",
    "raised": "#F4F4F5",
    "border": "#E6E6E9",
    "text": "#141416",
    "text2": "#6B6B73",
    "accent": "#E11D48",
    "accentHover": "#BE123C",
    "onAccent": "#FFFFFF",
}

_THEMES = {"dark": DARK, "light": LIGHT}


def _root(theme: str) -> str:
    p = _THEMES[theme]
    # Light theme earns one soft, offset shadow; dark stays flat (border only).
    if theme == "light":
        card_shadow = "0 1px 2px rgba(0,0,0,.04), 0 8px 24px rgba(0,0,0,.04)"
    else:
        card_shadow = "none"
    return (
        ":root{"
        f"--bg:{p['bg']};--surface:{p['surface']};--raised:{p['raised']};"
        f"--border:{p['border']};--text:{p['text']};--text2:{p['text2']};"
        f"--accent:{p['accent']};--accentHover:{p['accentHover']};"
        f"--onAccent:{p['onAccent']};--cardShadow:{card_shadow};"
        "--font:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;"
        "}"
    )


# Component rules are written once against var() so both themes share them.
_COMPONENTS = r"""
/* ---- foundation: canvas, type, browser surfaces ---- */
.stApp, .main { background: var(--bg); }
.stApp {
  font-family: var(--font);
  color: var(--text);
  font-feature-settings: "tnum" 1, "cv05" 1;
}
section.main > div { padding-top: 2.2rem; padding-bottom: 4rem; }
.block-container {
  max-width: 760px;
  padding-top: 2.2rem;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}
/* caret + selection carry the design, not browser defaults */
::selection { background: var(--accent); color: var(--onAccent); }
html { caret-color: var(--accent); }
*::-webkit-scrollbar { width: 10px; height: 10px; }
*::-webkit-scrollbar-thumb { background: var(--border); border-radius: 999px; }
*::-webkit-scrollbar-track { background: transparent; }

/* headings */
h1, h2, h3 { color: var(--text); font-family: var(--font); }
h1 {
  font-size: 2rem; font-weight: 800; letter-spacing: -0.03em;
  line-height: 1.1; margin: 0;
}
h2 { font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; margin: 0; }
p, li { color: var(--text); }
.stMarkdown p { color: var(--text); }
div[data-testid="stMarkdownContainer"] { color: var(--text); }

/* captions / help text */
small, .stCaption, div[data-testid="stCaptionContainer"] {
  color: var(--text2); font-size: 0.8125rem; font-weight: 400; line-height: 1.5;
}

/* ---- top bar: title left, theme pill right ---- */
.topbar { display: flex; align-items: center; justify-content: space-between; }
.topbar h1 { padding: 0; }

/* ---- segmented pill group (model switcher + theme) ---- */
div[data-testid="stRadio"] > label[data-testid="stWidgetLabel"],
div[data-testid="stRadio"] p {
  color: var(--text2) !important;
  font-size: 0.8125rem; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; margin-bottom: 0.4rem;
}
div[data-testid="stRadio"] div[role="radiogroup"] {
  gap: 0; background: var(--raised); border: 1px solid var(--border);
  border-radius: 999px; padding: 4px;
}
div[data-testid="stRadio"] div[role="radiogroup"] label {
  flex: 1 1 0; justify-content: center; cursor: pointer;
}
div[data-testid="stRadio"] div[role="radiogroup"] label > div {
  width: 100%; text-align: center; padding: 9px 14px; border-radius: 999px;
  color: var(--text2); font-weight: 600; font-size: 0.9rem;
  transition: color .16s ease, background .16s ease; white-space: nowrap;
}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover > div {
  color: var(--text); background: color-mix(in srgb, var(--text) 6%, transparent);
}
div[data-testid="stRadio"] div[role="radiogroup"]
  label > div[data-checked="true"] {
  background: var(--accent); color: var(--onAccent);
}
/* the real input is invisible; keep it focusable + show a ring on its label */
div[data-testid="stRadio"] input { position: absolute; opacity: 0; pointer-events: none; }
div[data-testid="stRadio"] input:focus-visible + div,
div[data-testid="stRadio"] label:focus-within > div {
  outline: 2px solid var(--accent); outline-offset: 2px;
}

/* compact theme toggle in the top bar */
.theme-switch div[role="radiogroup"] label > div { padding: 7px 14px; font-size: 0.8125rem; }
.theme-switch p { display: none; }

/* ---- cards: the one container for a group of inputs ---- */
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 20px; padding: 28px 28px 24px; box-shadow: var(--cardShadow);
}
.card + .card { margin-top: 20px; }
.card-title {
  color: var(--text); font-size: 1.05rem; font-weight: 700; letter-spacing: -0.01em;
  margin: 0 0 18px;
}

/* ---- inputs ---- */
div[data-testid="stWidgetLabel"] p, label {
  color: var(--text) !important; font-size: 0.9rem; font-weight: 500;
}
div[data-testid="stTextInput"], div[data-testid="stNumberInput"],
div[data-testid="stDateInput"] { }
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input {
  background: var(--raised); color: var(--text);
  border: 1px solid var(--border); border-radius: 12px;
  font-family: var(--font); font-size: 0.95rem; font-weight: 500;
  transition: border-color .16s ease, box-shadow .16s ease;
}
div[data-testid="stTextInput"] input::placeholder { color: var(--text2); }
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stDateInput"] input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 22%, transparent);
  outline: none;
}
/* number-input stepper buttons */
div[data-testid="stNumberInput"] button { color: var(--text2); }
div[data-testid="stNumberInput"] button:hover { color: var(--accent); }

/* slider */
div[data-testid="stSlider"] label { color: var(--text); }
div[data-testid="stSlider"] [role="slider"] {
  background: var(--accent); border-color: var(--accent);
}
div[data-testid="stSlider"] div[data-baseweb="slider"] {
  --thumb-width: 16px;
}
div[data-testid="stSlider"] div[role="presentation"] { background: var(--text2); }
div[data-testid="stSlider"] div[role="presentation"] > div { background: var(--accent); }
/* slider value readout */
div[data-testid="stSlider"] [data-testid="stMarkdownContainer"] { color: var(--text); }

/* ---- primary action: the only filled button on screen ---- */
div[data-testid="stButton"] > button {
  background: var(--accent); color: var(--onAccent);
  border: none; border-radius: 999px; padding: 14px 24px;
  font-family: var(--font); font-size: 1rem; font-weight: 700;
  letter-spacing: -0.01em; width: 100%;
  transition: background .16s ease, transform .16s ease, box-shadow .16s ease;
}
div[data-testid="stButton"] > button:hover {
  background: var(--accentHover); transform: translateY(-1px);
  box-shadow: 0 6px 20px color-mix(in srgb, var(--accent) 30%, transparent);
}
div[data-testid="stButton"] > button:active { transform: translateY(0) scale(.99); }
div[data-testid="stButton"] > button:focus-visible {
  outline: 2px solid var(--accent); outline-offset: 3px;
}

/* ghost buttons (secondary / small) */
div[data-testid="stButton"] > button[kind="secondary"],
.ghost button {
  background: transparent; color: var(--text); border: 1px solid var(--border);
}
.ghost button { width: auto; border-radius: 999px; padding: 8px 16px; font-size: .875rem; }
.ghost button:hover { background: var(--raised); color: var(--text); transform: none; box-shadow: none; }

/* ---- result band ---- */
.result-grid { display: flex; gap: 16px; }
.result-cell {
  flex: 1; background: var(--surface); border: 1px solid var(--border);
  border-radius: 20px; padding: 26px 28px; box-shadow: var(--cardShadow);
}
.result-kind {
  color: var(--text2); font-size: 0.78rem; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;
}
.result-figure {
  color: var(--text); font-size: 3rem; font-weight: 800; letter-spacing: -0.03em;
  line-height: 1; font-variant-numeric: tabular-nums;
}
.result-cell.accent .result-figure { color: var(--accent); }
.result-note { color: var(--text2); font-size: 0.8125rem; margin-top: 10px; }

/* one authored entrance for a freshly computed price */
@keyframes riseIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.result-cell { animation: riseIn .28s cubic-bezier(.16,.84,.44,1) both; }
.result-cell:nth-child(2) { animation-delay: .05s; }

/* ---- misc states ---- */
div[data-testid="stAlert"] { border-radius: 14px; font-size: .9rem; }
div[data-testid="stAlert"] p { font-size: .9rem; }
[data-testid="stSpinner"] { color: var(--text); }
.hr { height: 1px; background: var(--border); border: 0; margin: 26px 0; }

/* charts sit on the surface, no default padding box */
div[data-testid="stImage"] img, div[data-testid="stImage"] { background: transparent; }
"""


def css(theme: str) -> str:
    return _root(theme) + _COMPONENTS


def inject() -> None:
    """Push the active theme's stylesheet into the page."""
    theme = st.session_state.get("theme", "dark")
    st.markdown(f"<style>{css(theme)}</style>", unsafe_allow_html=True)


def current() -> str:
    return st.session_state.get("theme", "dark")
