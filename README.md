# EvidenceCheck

**Evidence-Based Reliability Checking for LLM-Generated Answers**

EvidenceCheck is an NLP research prototype that evaluates whether claims made in AI-generated answers are supported by relevant evidence.

The system combines **Retrieval-Augmented Generation (RAG)** with claim-level verification to analyze an answer beyond simply treating it as correct or incorrect.

### How It Works

```text
Question → Retrieve Evidence → Generate Answer
                              ↓
                 Extract Claims → Verify
                              ↓
             Supported / Partial / Unsupported
```

EvidenceCheck retrieves relevant passages, generates an answer using an LLM, breaks the answer into individual claims, and checks each claim against the available evidence.

### Research Focus

The project explores:

* Whether retrieved evidence improves the reliability of LLM answers
* Whether claim-level verification can identify unsupported claims
* How retrieval settings affect reliability
* Which types of claims are harder to verify

### Technology

**Python · FAISS · Sentence Transformers · Groq · PyTorch · Streamlit**

## Setup

Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
```

**Windows:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

Add your Groq API key to `.env`:

```env
GROQ_API_KEY=your_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

## Usage

Add your source documents to:

```text
data/raw/
```

Then build the document index:

```bash
python scripts/ingest_documents.py
python scripts/build_index.py
```

Start the application:

```bash
streamlit run app/streamlit_app.py
```

Open the local Streamlit URL shown in the terminal and use **Evaluate** to submit a question and inspect the generated answer, claims, evidence, and verification results.

### Important Note

EvidenceCheck measures whether a claim is **supported by the evidence available to the system**. It does not guarantee that a claim is universally true.

**Status:** Research Prototype
