import json
import pandas as pd
import streamlit as st
from ui.state import settings, provider, get_embedder, sample_docs, sample_retriever, RESULTS
from ui.components import render_page_header, render_empty_state
from evidencecheck.experiments.runner import run, load_questions, n_steps
from evidencecheck.generation.providers import ProviderError
from evidencecheck.evaluation.evaluator import threshold_sweep

s = settings()
try:
    qs = load_questions()
except FileNotFoundError:
    qs = []
render_page_header("Experiments", "Compare retrieval and generation configurations under controlled conditions.",
                   {"CORPUS": "bundled sample docs", "QUESTIONS": f"{len(qs)} demo (synthetic)", "VERIFIER": "Similarity"})
names = {"Baseline Comparison": "baseline", "Top-K Analysis": "top-k", "Chunk Size Analysis": "chunk-size",
         "Threshold Sensitivity": "threshold"}
key = names[st.selectbox("Experiment", list(names))]

if key == "threshold":
    st.caption("Runs offline (no LLM): how verdict quality on gold claims changes with the supported threshold.")
    ret = sample_retriever()
    rows = threshold_sweep(ret, s.top_k, s.partial_threshold) if ret else []
    if not rows:
        render_empty_state("N/A — no gold labels available.", "Add data/evaluation/gold_claims.json.")
    else:
        df = pd.DataFrame(rows)
        st.line_chart(df.set_index("supported_threshold")[["macro_f1", "accuracy"]])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption("Demo gold set (17 claims, author-labelled). Indicative only.")
    st.stop()

store = st.session_state.setdefault("exp_results", {})
if not qs:
    render_empty_state("No questions available.", "Add questions to data/evaluation/questions.json.")
    st.stop()
n = st.slider("Questions to run", 1, len(qs), min(4, len(qs)))
st.caption(f"≈ {n_steps(key, n) * 2} LLM calls (answer + claim extraction). Free tiers are rate-limited, so this can take a few minutes.")
if st.button("Run experiment", type="primary"):
    p = provider()
    if not p.configured:
        st.warning("No LLM API key found. Add one on the Configuration page.")
        st.page_link("pages/settings.py", label="Open Configuration", icon=":material/tune:")
    else:
        total, done = n_steps(key, n), [0]
        bar = st.progress(0.0, text="Running…")
        def tick():
            done[0] += 1
            bar.progress(min(done[0] / total, 1.0))
        try:
            store[key] = run(key, get_embedder(), p, qs[:n], sample_docs(), tick=tick)
        except ProviderError as e:
            st.error(str(e))
        bar.empty()
data = store.get(key)
f = RESULTS / "tables" / f"{key}.json"
if data is None and f.exists():
    data = json.loads(f.read_text(encoding="utf-8"))
if not data:
    render_empty_state("Not evaluated yet.", "Click Run experiment to generate results.")
    st.stop()
st.caption(f"Model: {data['model']}")
rows = [{**r.get("config", {}), "system": r.get("system", ""), "claims": r["total"], "reliability": r["reliability"],
         "partial_rate": r["partial_rate"], "unsupported_rate": r["unsupported_rate"]} for r in data["results"]]
df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)
if df["reliability"].notna().any():
    label = df.apply(lambda r: r["system"] or f"k={r.get('top_k')}, size={r.get('chunk_size')}", axis=1)
    st.bar_chart(pd.DataFrame({"reliability": df["reliability"].fillna(0).values}, index=label))
st.download_button("Download results (JSON)", json.dumps(data, indent=2), f"{key}.json", "application/json")
