import streamlit as st
from ui.state import settings, get_retriever, provider
from ui.components import (render_page_header, render_metric_card, render_claim_card, render_empty_state)
from evidencecheck.generation.rag import rag_answer
from evidencecheck.generation.providers import ProviderError
from evidencecheck.claims.extractor import extract_claims
from evidencecheck.verification.verifier import SimilarityVerifier, verify_answer

s, p = settings(), provider()
render_page_header("Evaluate", "Test an answer, inspect its evidence, and measure claim-level reliability.",
                   {"MODEL": s.groq_model, "RETRIEVAL": f"top-{s.top_k}", "VERIFIER": "Similarity"})
ret = get_retriever()
if not p.configured:
    st.warning("No LLM API key found. Add one on the Configuration page to generate answers.")
    st.page_link("pages/settings.py", label="Open Configuration", icon=":material/tune:")
if ret is None:
    render_empty_state("No indexed documents", "Select sample documents or upload files on the Documents page.")
    st.stop()
EXAMPLES = ["When was Python first released?", "Where does photosynthesis take place in plants?", "Does RAG eliminate hallucination?"]
st.caption("Try an example (works with the sample documents):")
for col, ex in zip(st.columns(3), EXAMPLES):
    col.button(ex, key=ex, on_click=lambda e=ex: st.session_state.update(question=e))
q = st.text_area("Ask a factual question", key="question", height=80, placeholder="Enter your question…")
if st.button("Run Evaluation", type="primary") and q.strip():
    try:
        with st.status("Running evaluation…", expanded=True) as status:
            st.write("Retrieving evidence…"); st.write("Generating answer…")
            ans, ev = rag_answer(q, ret, p, s.top_k)
            st.write("Extracting claims…"); claims = extract_claims(ans, p)
            st.write("Verifying evidence…")
            out = verify_answer(claims, ret, SimilarityVerifier(s.supported_threshold, s.partial_threshold), s.top_k)
            status.update(label="Done", state="complete")
        st.session_state.result = {"answer": ans, "evidence": ev, **out}
    except ProviderError as e:
        st.error(f"Generation unavailable. {e}")
res = st.session_state.get("result")
if not res:
    render_empty_state("No evaluation yet.", "Ask a question to begin an evidence-based reliability analysis.")
    st.stop()
sm = res["summary"]
if sm["total"] == 0:
    st.warning("No verifiable claims were extracted from the answer.")
else:
    cols = st.columns(4)
    with cols[0]: render_metric_card("Reliability", f"{sm['reliability']:.0%}")
    with cols[1]: render_metric_card("Supported", str(sm["counts"]["SUPPORTED"]))
    with cols[2]: render_metric_card("Partial", str(sm["counts"]["PARTIALLY_SUPPORTED"]))
    with cols[3]: render_metric_card("Unsupported", str(sm["counts"]["UNSUPPORTED"]))
    st.caption("Reliability score is a project-defined experimental metric and should not be interpreted as a guarantee that an answer is factually true.")
st.subheader("Generated answer"); st.info(res["answer"])
st.subheader("Claim verification")
for i, r in enumerate(res["claims"], 1):
    render_claim_card(i, r)
