import streamlit as st
from ui.state import get_retriever, provider, corpus_docs, settings

st.markdown("""
<div class='ec-hero'>
  <span class='tag'>OPEN RESEARCH PROTOTYPE · RAG RELIABILITY</span>
  <h1>Can NLP help detect unsupported claims in AI answers?</h1>
  <p>Using NLP,EvidenceCheck splits an LLM answer into individual claims and checks each one against your documents,
  so you can see exactly what is supported, partly supported, or unsupported.</p>
  <div class='ec-flow'><b>Retrieve</b><i>→</i><b>Generate</b><i>→</i><b>Extract claims</b><i>→</i><b>Verify</b><i>→</i><b>Score</b></div>
</div>""", unsafe_allow_html=True)
a, b, _ = st.columns([1.2, 1.2, 3])
a.page_link("pages/evaluate.py", label="Run an evaluation", icon=":material/play_arrow:")
b.page_link("pages/documents.py", label="Add documents", icon=":material/upload_file:")

st.subheader("Get started")
s, r, docs = settings(), get_retriever(), corpus_docs()
items = [
    (provider().configured, "LLM key", f"{s.llm_provider.title()} key {'detected' if provider().configured else 'missing'}",
     "pages/settings.py", "Open Configuration"),
    (len(docs) > 0, "Documents", f"{len(docs)} active page(s)/file(s)", "pages/documents.py", "Manage documents"),
    (r is not None, "Search index", f"{len(r.chunks)} chunks indexed" if r else "not built yet", "pages/documents.py", "View index"),
]
for col, (ok, title, detail, page, label) in zip(st.columns(3), items):
    with col.container(border=True):
        st.markdown(f"**{'✓' if ok else '○'} {title}**  \n<span class='{'ec-ok' if ok else 'ec-todo'}'>{detail}</span>", unsafe_allow_html=True)
        st.page_link(page, label=label)
if all(i[0] for i in items):
    st.success("Everything is ready. Ask your first question on the Evaluate page.")
else:
    st.info("Finish the items above, then run an evaluation. **Configuration** is where you set your LLM provider, API key and retrieval options.")

st.subheader("What each page does")
cards = [
    ("Documents", "Pick sample docs or upload your own (.txt, .md, .pdf).", "pages/documents.py", ":material/folder:"),
    ("Evaluate", "Ask a question, get an answer and a claim-by-claim reliability score.", "pages/evaluate.py", ":material/fact_check:"),
    ("Claims", "Browse and filter every claim by verdict and type.", "pages/claims.py", ":material/list:"),
    ("Evidence", "Read the exact passages retrieved for the answer.", "pages/evidence.py", ":material/search:"),
    ("Experiments", "Compare direct LLM vs RAG, top-k and chunk size.", "pages/experiments.py", ":material/science:"),
    ("Metrics", "Recall@K, precision and claim F1 against gold labels.", "pages/metrics.py", ":material/monitoring:"),
    ("Error Analysis", "Reviewed failure cases grouped by category.", "pages/error_analysis.py", ":material/bug_report:"),
    ("Methodology", "How verdicts and the reliability score are computed.", "pages/methodology.py", ":material/menu_book:"),
    ("Configuration", "LLM provider, API key, retrieval and thresholds.", "pages/settings.py", ":material/tune:"),
]
for i in range(0, len(cards), 3):
    for col, (t, d, page, icon) in zip(st.columns(3), cards[i:i + 3]):
        with col.container(border=True):
            st.markdown(f"**{t}**  \n<span class='ec-mono'>{d}</span>", unsafe_allow_html=True)
            st.page_link(page, label="Open", icon=icon)
st.caption("Verdicts estimate whether claims are supported by retrieved text. They do not establish factual truth.")
