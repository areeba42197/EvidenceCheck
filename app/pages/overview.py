import streamlit as st
import textwrap
from ui.state import get_retriever, provider, corpus_docs, settings


# ---------------------------------------------------------
# Hero
# ---------------------------------------------------------

st.markdown("""
<div class='ec-hero'>
  <span class='tag'>OPEN RESEARCH PROTOTYPE · NLP · RAG</span>
  <h1>Can NLP help detect unsupported claims in AI answers?</h1>
  <p>EvidenceCheck breaks an LLM answer into individual claims and
                  checks each claim against retrieved evidence to identify what is
                  supported, partly supported, or unsupported.</p>
  <div class='ec-flow'><b>Retrieve</b><i>→</i><b>Generate</b><i>→</i><b>Extract claims</b><i>→</i><b>Verify</b><i>→</i><b>Score</b></div>
</div>""", unsafe_allow_html=True)



# ---------------------------------------------------------
# What is EvidenceCheck?
# ---------------------------------------------------------

st.subheader("What is EvidenceCheck?")

st.markdown(
    """
    Large Language Models can produce answers that sound convincing but
    contain claims that are not supported by the available information.

    EvidenceCheck studies this problem using **Natural Language Processing
    (NLP)** and **Retrieval-Augmented Generation (RAG)**.

    Instead of treating an entire answer as simply "right" or "wrong",
    the system looks at it **claim by claim** and traces each claim back
    to relevant evidence.
    """
)


# ---------------------------------------------------------
# Simple explanation
# ---------------------------------------------------------

c1, c2, c3 = st.columns(3)

with c1:
    with st.container(border=True):
        st.markdown("### 01 · Generate")
        st.markdown(
            "Retrieve relevant information and use an LLM to generate an answer."
        )

with c2:
    with st.container(border=True):
        st.markdown("### 02 · Analyze")
        st.markdown(
            "Use NLP to break the answer into individual factual claims."
        )

with c3:
    with st.container(border=True):
        st.markdown("### 03 · Verify")
        st.markdown(
            "Compare each claim with retrieved evidence and assign a verdict."
        )


# ---------------------------------------------------------
# Research Questions
# ---------------------------------------------------------

st.subheader("Research Questions")

st.caption(
    "The system is designed to investigate four questions about "
    "evidence grounding in LLM-generated answers."
)

research_questions = [
    (
        "RQ1",
        "RAG vs. Direct LLM",
        "Does providing retrieved evidence make LLM answers more reliably supported?",
    ),
    (
        "RQ2",
        "Claim Verification",
        "Can claim-level evidence verification identify unsupported claims in RAG-generated answers?",
    ),
    (
        "RQ3",
        "Retrieval Settings",
        "How do settings such as top-k and chunk size affect the reliability of generated answers?",
    ),
    (
        "RQ4",
        "Difficult Claims",
        "Which types of claims are hardest to verify, such as numerical, date, causal, or multi-hop claims?",
    ),
]

for rq, title, question in research_questions:
    with st.container(border=True):
        st.markdown(f"**{rq} · {title}**")
        st.write(question)


# ---------------------------------------------------------
# What the system produces
# ---------------------------------------------------------

st.subheader("What does the system produce?")

left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.markdown("### Claim-level analysis")
        st.markdown(
            """
            Each generated answer is broken into individual claims.

            **Supported**  
            Evidence supports the claim.

            **Partially supported**  
            Evidence supports only part of the claim.

            **Unsupported**  
            No sufficient supporting evidence was retrieved.
            """
        )

with right:
    with st.container(border=True):
        st.markdown("### Research analysis")
        st.markdown(
            """
            The system can also compare different configurations and examine:

            - Direct LLM vs. RAG
            - Retrieval settings
            - Claim types
            - Verification performance
            - Failure cases
            """
        )


# ---------------------------------------------------------
# Current system status
# ---------------------------------------------------------

st.subheader("Current System Status")

s = settings()
r = get_retriever()
docs = corpus_docs()
llm = provider()

status_items = [
    (
        llm.configured,
        "LLM",
        f"{s.llm_provider.title()} configured"
        if llm.configured
        else f"{s.llm_provider.title()} key missing",
        "pages/settings.py",
        "Configure",
    ),
    (
        len(docs) > 0,
        "Documents",
        f"{len(docs)} active file(s)"
        if docs
        else "No documents added",
        "pages/documents.py",
        "Manage",
    ),
    (
        r is not None,
        "Search Index",
        f"{len(r.chunks)} chunks indexed"
        if r
        else "Index not built",
        "pages/documents.py",
        "Open",
    ),
]

for col, (ok, title, detail, page, label) in zip(
    st.columns(3),
    status_items,
):
    with col.container(border=True):
        status = "✓" if ok else "○"

        st.markdown(
            f"**{status} {title}**  \n"
            f"<span class='{'ec-ok' if ok else 'ec-todo'}'>{detail}</span>",
            unsafe_allow_html=True,
        )

        st.page_link(page, label=label)


# ---------------------------------------------------------
# Explore
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Footer note
# ---------------------------------------------------------

st.divider()

st.caption(
    "EvidenceCheck estimates whether generated claims are supported by "
    "retrieved evidence. It does not establish factual truth."
)

