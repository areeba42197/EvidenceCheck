import json
import pandas as pd
import streamlit as st
from ui.state import settings, sample_retriever
from ui.components import render_page_header, render_metric_card, render_empty_state
from evidencecheck.evaluation.evaluator import evaluate_retrieval, evaluate_verifier
from evidencecheck.verification.verifier import SimilarityVerifier

s = settings()
render_page_header("Metrics", "Retrieval and verification quality against gold labels (computed live, no LLM needed).",
                   {"CORPUS": "bundled sample docs", "TOP-K": str(s.top_k)})
ret = sample_retriever()
if ret is None:
    render_empty_state("Index unavailable.", "The embedding model could not be loaded.")
    st.stop()
with st.spinner("Computing metrics…"):
    rt = evaluate_retrieval(ret)
    vf = evaluate_verifier(ret, SimilarityVerifier(s.supported_threshold, s.partial_threshold), s.top_k)
fmt = lambda x: f"{x:.2f}" if isinstance(x, float) else "N/A"
m = st.columns(4)
with m[0]: render_metric_card("Recall@3", fmt(rt.get("recall@3")), "document level")
with m[1]: render_metric_card("Precision@3", fmt(rt.get("precision@3")))
with m[2]: render_metric_card("Claim macro-F1", fmt(vf.get("macro_f1")))
with m[3]: render_metric_card("Gold claims", str(vf.get("n_gold_claims", "N/A")))
st.caption("Demo gold set: 8 synthetic questions and 17 author-labelled claims on the bundled documents. Indicative only; replace with reviewed data for research claims.")
if vf.get("status") != "ok":
    render_empty_state("N/A — no gold labels available.", "")
    st.stop()
st.subheader("Per-label results")
st.dataframe(pd.DataFrame(vf["per_label"]).T.round(2), use_container_width=True)
st.subheader("Confusion matrix (rows = gold, columns = predicted)")
st.dataframe(pd.DataFrame(vf["confusion_matrix"]).T, use_container_width=True)
st.download_button("Download metrics (JSON)", json.dumps({"retrieval": rt, "verification": {k: v for k, v in vf.items() if k != "rows"}}, indent=2),
                   "metrics.json", "application/json")
