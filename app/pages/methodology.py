import streamlit as st
from ui.components import render_page_header, render_research_card

render_page_header("Methodology & Limitations", "How EvidenceCheck estimates evidence support.")
render_research_card("Pipeline", "Documents → chunks → MiniLM embeddings → FAISS → Groq answer → claims → evidence retrieval → similarity verdict → reliability.")
render_research_card("Reliability", "reliability = supported_claims / total_verifiable_claims. A project-defined experimental metric, not a truth guarantee.")
render_research_card("Verification", "Semantic similarity measures textual/semantic relatedness and does not independently establish factual correctness. Thresholds (0.75 / 0.55) are project-defined and unvalidated.")
st.subheader("Limitations")
for l in ["Similarity does not guarantee truth", "Verifier can make mistakes", "Retrieval quality limits verification",
          "Atomic claim extraction is imperfect", "Multi-hop and numerical claims are hard", "Thresholds are project-defined",
          "Groq free-tier rate limits", "Human evaluation needed for stronger validation"]:
    st.markdown(f"- {l}")
st.caption("EvidenceCheck estimates whether generated claims are supported by retrieved evidence. It does not determine whether information is true.")
