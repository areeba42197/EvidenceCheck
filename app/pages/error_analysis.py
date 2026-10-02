import pandas as pd
import streamlit as st
from ui.state import settings, sample_retriever
from ui.components import render_page_header, render_empty_state, render_research_card
from evidencecheck.evaluation.error_analysis import load_cases, category_counts, CATEGORIES, FIELDS
from evidencecheck.evaluation.evaluator import evaluate_verifier
from evidencecheck.verification.verifier import SimilarityVerifier

s = settings()
render_page_header("Error Analysis", "Log and categorise failure cases from real runs. Categories are your judgement.")
cases = st.session_state.setdefault("cases", [])
cands = []
ret = sample_retriever()
if ret:
    for r in evaluate_verifier(ret, SimilarityVerifier(s.supported_threshold, s.partial_threshold), s.top_k).get("rows", []):
        if r["gold"] != r["pred"]:
            cands.append({"label": f"[verifier vs gold] {r['claim'][:70]} (gold {r['gold']}, got {r['pred']})",
                          "question": r["question_id"], "claim": r["claim"], "evidence": r["evidence"], "verdict": r["pred"]})
res = st.session_state.get("result")
for r in (res or {}).get("claims", []):
    if r["verdict"] != "SUPPORTED":
        cands.append({"label": f"[latest evaluation] {r['claim'][:70]} ({r['verdict']})",
                      "question": st.session_state.get("question", ""), "claim": r["claim"],
                      "evidence": (r.get("best_evidence") or {}).get("text", ""), "verdict": r["verdict"]})
st.subheader("Log a case")
if not cands:
    st.caption("No candidates yet. Run an evaluation, or adjust thresholds so the verifier disagrees with gold labels.")
else:
    with st.form("case"):
        pick = st.selectbox("Candidate", range(len(cands)), format_func=lambda i: cands[i]["label"])
        cat = st.selectbox("Failure category", CATEGORIES)
        note = st.text_area("Analysis")
        if st.form_submit_button("Add case"):
            c = cands[pick]
            cases.append({"case_id": f"{len(cases) + 1:02d}", "question": c["question"], "claim": c["claim"],
                          "evidence": c["evidence"], "verdict": c["verdict"], "category": cat, "analysis": note})
allc = load_cases() + cases
if not allc:
    render_empty_state("No cases recorded.", "Add a case above.")
    st.stop()
st.subheader("Failure distribution")
st.bar_chart(pd.Series(category_counts(allc), name="cases"))
for r in allc:
    render_research_card(f"CASE {r['case_id']} · {r['category']}", f"Claim: {r['claim']} | Verdict: {r['verdict']} | {r['analysis']}")
st.download_button("Download cases (CSV)", pd.DataFrame(allc, columns=FIELDS).to_csv(index=False), "error_analysis.csv", "text/csv")
st.caption("Cases live in this session; download them to keep them.")
