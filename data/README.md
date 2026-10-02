# Data
- `raw/`: source documents (.txt/.md/.pdf). Use only openly licensed material; record source and license here.
- `evaluation/questions.json`: questions (mark LLM-generated ones `"synthetic": true`). See the template.
- `evaluation/gold_claims.json`: gold labels from **manual evidence review**. Never auto-generate.
Both files ship empty, so metrics display "N/A" until you add data.

## Bundled demo set
`questions.json` (8, synthetic) and `gold_claims.json` (17) were authored against the bundled sample documents. They are a **demo-sized** set for exercising the pipeline, not independent human annotation. Replace them with your own reviewed data for real research claims.
