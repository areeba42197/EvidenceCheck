"""Centralised CSS (light, developer-oriented)."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: Inter, system-ui, sans-serif; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1050px; }
.ec-header h1 { font-size: 1.6rem; font-weight: 600; margin: 0; letter-spacing: -0.01em; }
.ec-header p { color: #57606a; margin: .25rem 0 .75rem; }
.ec-chips span { display:inline-block; margin-right:.4rem; padding:.1rem .5rem; border:1px solid #d0d7de;
  border-radius:6px; font: 500 .72rem 'JetBrains Mono', monospace; color:#57606a; background:#f6f8fa; }
.ec-card { background:#fff; border:1px solid #d0d7de; border-radius:8px; padding:.9rem 1rem; margin-bottom:.7rem; }
.ec-label { font: 500 .68rem 'JetBrains Mono', monospace; color:#6e7781; letter-spacing:.06em; text-transform:uppercase; }
.ec-value { font: 500 1.7rem 'JetBrains Mono', monospace; color:#1f2328; }
.ec-mono { font-family:'JetBrains Mono', monospace; font-size:.78rem; color:#57606a; }
.ec-badge { padding:.1rem .5rem; border-radius:5px; font: 500 .7rem 'JetBrains Mono', monospace; }
.ec-SUPPORTED { background:#dafbe1; color:#116329; border:1px solid #aceebb; }
.ec-PARTIALLY_SUPPORTED { background:#fff8c5; color:#7d4e00; border:1px solid #eac54f; }
.ec-UNSUPPORTED { background:#ffebe9; color:#a40e26; border:1px solid #ffcecb; }
.ec-evidence { border-left:3px solid #4f46e5; padding-left:.75rem; color:#24292f; font-size:.9rem; }
.ec-step { font: 600 .75rem 'JetBrains Mono', monospace; color:#4f46e5; }
.ec-hero { padding:2.4rem 2.2rem; border:1px solid #d0d7de; border-radius:14px;
  background: linear-gradient(135deg,#f5f3ff 0%,#eef6ff 100%); margin-bottom:1.2rem; }
.ec-hero .tag { display:inline-block; font:500 .72rem 'JetBrains Mono',monospace; color:#4f46e5; background:#fff;
  border:1px solid #c7d2fe; border-radius:999px; padding:.15rem .7rem; margin-bottom:.9rem; }
.ec-hero h1 { font-size:2.5rem; line-height:1.15; font-weight:600; letter-spacing:-0.02em; margin:0 0 .6rem; }
.ec-hero p { font-size:1.05rem; color:#424a53; max-width:46rem; margin:0 0 1.1rem; }
.ec-flow { display:flex; flex-wrap:wrap; gap:.4rem; align-items:center; font:500 .78rem 'JetBrains Mono',monospace; }
.ec-flow b { background:#fff; border:1px solid #d0d7de; border-radius:6px; padding:.2rem .55rem; font-weight:500; }
.ec-flow i { color:#8c959f; font-style:normal; }
.ec-ok { color:#116329; } .ec-todo { color:#a40e26; }
</style>
"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
