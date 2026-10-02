import streamlit as st
import ui.state  # noqa: F401  (sets sys.path)
from ui.styles import inject

st.set_page_config(page_title="EvidenceCheck", page_icon="🔎", layout="wide")
inject()
nav = st.navigation({
    "": [st.Page("pages/overview.py", title="Overview", icon=":material/home:", default=True)],
    "Workspace": [st.Page("pages/documents.py", title="Documents", icon=":material/folder:"),
                  st.Page("pages/evaluate.py", title="Evaluate", icon=":material/fact_check:"),
                  st.Page("pages/claims.py", title="Claims", icon=":material/list:"),
                  st.Page("pages/evidence.py", title="Evidence", icon=":material/search:")],
    "Research": [st.Page("pages/experiments.py", title="Experiments", icon=":material/science:"),
                 st.Page("pages/metrics.py", title="Metrics", icon=":material/monitoring:"),
                 st.Page("pages/error_analysis.py", title="Error Analysis", icon=":material/bug_report:")],
    "Docs": [st.Page("pages/methodology.py", title="Methodology", icon=":material/menu_book:"),
             st.Page("pages/architecture.py", title="Architecture", icon=":material/account_tree:")],
    "Setup": [st.Page("pages/settings.py", title="Configuration", icon=":material/tune:")],
})
st.sidebar.markdown("**EvidenceCheck**  \n`v0.1 · prototype`")
nav.run()
