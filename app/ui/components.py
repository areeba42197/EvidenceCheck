"""Reusable UI components."""
import html
import streamlit as st


def _e(x) -> str:
    return html.escape(str(x))


def render_page_header(title: str, desc: str, chips: dict[str, str] | None = None) -> None:
    chip_html = "".join(f"<span>{_e(k)} {_e(v)}</span>" for k, v in (chips or {}).items())
    st.markdown(f"<div class='ec-header'><h1>{_e(title)}</h1><p>{_e(desc)}</p>"
                f"<div class='ec-chips'>{chip_html}</div></div>", unsafe_allow_html=True)


def render_metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(f"<div class='ec-card'><div class='ec-label'>{_e(label)}</div>"
                f"<div class='ec-value'>{_e(value)}</div><div class='ec-mono'>{_e(note)}</div></div>",
                unsafe_allow_html=True)


def render_status_badge(verdict: str) -> str:
    return f"<span class='ec-badge ec-{_e(verdict)}'>{_e(verdict.replace('_', ' '))}</span>"


def render_empty_state(title: str, body: str) -> None:
    st.markdown(f"<div class='ec-card' style='text-align:center'><b>{_e(title)}</b><br>"
                f"<span class='ec-mono'>{_e(body)}</span></div>", unsafe_allow_html=True)


def render_research_card(title: str, body: str) -> None:
    st.markdown(f"<div class='ec-card'><div class='ec-label'>{_e(title)}</div>{_e(body)}</div>",
                unsafe_allow_html=True)


def render_evidence_card(i: int, ev: dict) -> None:
    page = ev.get("page") or "n/a"
    with st.expander(f"EVIDENCE_{i:02d} · {ev['source']} · sim {ev['similarity_score']:.2f}"):
        st.markdown(f"<div class='ec-mono'>{_e(ev['chunk_id'])} · page {_e(page)}</div>"
                    f"<div class='ec-evidence'>{_e(ev['text'])}</div>", unsafe_allow_html=True)


def render_claim_card(i: int, r: dict) -> None:
    st.markdown(f"<div class='ec-card'><div class='ec-label'>CLAIM {i:02d} · {_e(r.get('category',''))}</div>"
                f"<div style='margin:.35rem 0'>{_e(r['claim'])}</div>{render_status_badge(r['verdict'])} "
                f"<span class='ec-mono'>similarity {r['similarity']:.2f}</span></div>", unsafe_allow_html=True)
    for j, ev in enumerate(r.get("evidence", []), 1):
        render_evidence_card(j, ev)
