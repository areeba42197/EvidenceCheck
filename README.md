# EvidenceCheck
Evidence-based hallucination detection and reliability evaluation for Retrieval-Augmented Generation. A research prototype: it estimates whether generated claims are supported by retrieved evidence, not whether they are true.

**Research question:** How reliably can evidence-based claim verification identify unsupported claims in RAG systems? (RQ1-RQ4 in `docs/`.)
**Contribution:** an evaluation framework and verification pipeline, not a new model.

Pipeline: Retrieve → Generate → Extract Claims → Verify → Measure.
Stack: Python 3.11+, Groq (free tier), sentence-transformers (MiniLM), FAISS, Streamlit. Cost: $0.

## Setup
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # set GROQ_API_KEY (never commit)
```
## Run
```bash
streamlit run app/streamlit_app.py
python scripts/ingest_documents.py && python scripts/build_index.py
python scripts/run_evaluation.py                          # offline: needs gold labels
python scripts/run_experiments.py --experiment baseline   # also top-k, chunk-size (needs Groq)
pytest -q tests
```
Add documents to `data/raw/`; questions and gold labels go in `data/evaluation/` (see `data/README.md`).

## Results
Not evaluated yet. No dataset or gold labels are included; metrics show N/A until you add them.

## Limitations
See `docs/limitations.md`. Similarity thresholds are project-defined; the reliability score is not a truth guarantee.

## Deployment (Streamlit Community Cloud)
1. Push the repo to GitHub (`.env` and `.streamlit/secrets.toml` are gitignored).
2. share.streamlit.io → New app → main file `app/streamlit_app.py` → Advanced settings: **Python 3.12**.
3. Paste into Secrets: `GEMINI_API_KEY = "..."` (see `.streamlit/secrets.toml.example`).
4. Every page works online: Metrics and Threshold Sensitivity run live without an LLM; Experiments run on demand; Error Analysis cases are logged in-app (download to keep).
Notes: the server key is shared by all visitors (free-tier rate limits apply); visitors can use their own key under Configuration. Disk is ephemeral, so results persist per session. Free-tier Gemini content may be used by Google to improve products. Demo URL: _not deployed yet_.
