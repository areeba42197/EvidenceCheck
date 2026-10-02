import streamlit as st
from ui.state import settings, provider
from ui.components import render_page_header
from evidencecheck.generation.providers import ProviderError

s = settings()
render_page_header("Configuration", "Set your LLM provider and API key, then tune retrieval and verification.")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Retrieval")
    s.top_k = st.slider("Top K", 1, 5, s.top_k)
    s.chunk_size = st.select_slider("Chunk size", [200, 500, 800], s.chunk_size)
    s.chunk_overlap = st.slider("Chunk overlap", 0, s.chunk_size - 1, min(s.chunk_overlap, s.chunk_size - 1))
with c2:
    st.subheader("Verification (project-defined thresholds)")
    s.supported_threshold = st.slider("Supported threshold", 0.0, 1.0, s.supported_threshold, 0.01)
    s.partial_threshold = st.slider("Partial threshold", 0.0, 1.0, min(s.partial_threshold, s.supported_threshold), 0.01)
    if s.partial_threshold > s.supported_threshold:
        st.error("Partial threshold must not exceed supported threshold.")

st.subheader("LLM")
s.llm_provider = st.selectbox("Provider", ["gemini", "groq"], index=["gemini", "groq"].index(s.llm_provider if s.llm_provider in ("gemini", "groq") else "gemini"))
if s.llm_provider == "gemini":
    s.gemini_model = st.text_input("Gemini model", s.gemini_model)
    
else:
    s.groq_model = st.text_input("Groq model", s.groq_model)
st.caption(f"`.env` path: `{env_file()}` · exists: {env_file().is_file()}")
with st.expander("Use your own API key (optional)"):
    k = st.text_input(f"{s.llm_provider.title()} API key (this session only, not saved)", type="password",
                      value=st.session_state.get(f"key_{s.llm_provider}", ""))
    st.session_state[f"key_{s.llm_provider}"] = k.strip().strip("\"'")
    st.caption("If left empty, the app's built-in key is used.")
p = provider()
src = "your session key" if st.session_state.get(f"key_{s.llm_provider}") else ("built-in key" if p.configured else "none")
st.markdown(f"Provider: **{s.llm_provider}** · API key detected: **{'Yes' if p.configured else 'No'}** · source: {src}")
if st.button("Test connection"):
    try:
        p.generate("Reply with: ok")
        st.success(f"Connection works (model: {p.active_model}).")
    except ProviderError as e:
        st.error(str(e))
