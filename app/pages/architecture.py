import streamlit as st
from ui.components import render_page_header
render_page_header("Architecture", "End-to-end pipeline.")
st.graphviz_chart("""digraph { rankdir=TB; node [shape=box style=rounded color="#6366f1" fontcolor="#e6e8ee"];
 Documents->Ingestion->Chunking->Embeddings->FAISS->Retriever->Groq->Answer->Claims->"Evidence Retrieval"->Verification->Metrics }""")
