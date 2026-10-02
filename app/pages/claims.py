import pandas as pd
import streamlit as st
from ui.components import render_page_header, render_empty_state, render_claim_card
render_page_header("Claims", "Browse and filter verified claims from the latest evaluation.")
res = st.session_state.get("result")
if not res or not res["claims"]:
    render_empty_state("No claims yet.", "Run an evaluation first.")
    st.stop()
c1, c2 = st.columns(2)
verdict = c1.selectbox("Verdict", ["All", "SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED"])
cats = sorted({r["category"] for r in res["claims"]})
cat = c2.selectbox("Category", ["All"] + cats)
rows = [r for r in res["claims"] if verdict in ("All", r["verdict"]) and cat in ("All", r["category"])]
st.dataframe(pd.DataFrame([{"Claim": r["claim"], "Verdict": r["verdict"], "Similarity": round(r["similarity"], 3),
             "Evidence": (r.get("best_evidence") or {}).get("source", ""), "Category": r["category"]} for r in rows]),
             use_container_width=True, hide_index=True)
for i, r in enumerate(rows, 1):
    render_claim_card(i, r)
