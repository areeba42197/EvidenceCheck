import streamlit as st
from ui.state import sample_docs, corpus_docs, get_retriever
from ui.components import render_page_header
from evidencecheck.ingestion.loaders import load_uploaded

render_page_header("Documents", "Choose which documents the system can retrieve evidence from.")
samples = sorted({d["source"] for d in sample_docs()})
st.subheader("Sample documents")
st.multiselect("Included sample documents", samples, default=st.session_state.get("sample_sel", samples), key="sample_sel")
st.subheader("Upload your own")
files = st.file_uploader("Upload .txt, .md or .pdf", type=["txt", "md", "pdf"], accept_multiple_files=True)
if files:
    up, errs = [], []
    for f in files:
        try:
            up += load_uploaded(f.name, f.getvalue())
        except Exception:
            errs.append(f.name)
    st.session_state.uploads = up
    if errs:
        st.error(f"Could not read: {', '.join(errs)} (scanned PDFs without text are not supported).")
elif "uploads" in st.session_state and not files:
    st.session_state.uploads = []
st.caption("Uploads are kept only for this browser session and are not saved to disk. Max size is set by Streamlit (200 MB).")
docs = corpus_docs()
st.subheader(f"Active corpus ({len(docs)} pages/files)")
if not docs:
    st.warning("No documents selected. Choose a sample or upload a file.")
else:
    r = get_retriever()
    st.write(f"Indexed **{len(r.chunks)}** chunks." if r else "Index unavailable (embedding model failed to load).")
    for name in sorted({d["source"] for d in docs}):
        st.markdown(f"- `{name}`")
