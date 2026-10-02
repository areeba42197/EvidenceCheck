import streamlit as st
from ui.components import render_page_header, render_empty_state, render_evidence_card
render_page_header("Evidence", "Chunks retrieved for the latest question.")
res = st.session_state.get("result")
if not res or not res["evidence"]:
    render_empty_state("No evidence yet.", "Run an evaluation first.")
    st.stop()
for i, e in enumerate(res["evidence"], 1):
    render_evidence_card(i, e)
