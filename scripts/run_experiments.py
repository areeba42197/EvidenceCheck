import argparse, sys
import _common  # noqa
from evidencecheck.config import Settings
from evidencecheck.generation.providers import make_provider
from evidencecheck.retrieval.embeddings import SentenceTransformerEmbedder
from evidencecheck.experiments.runner import run

ap = argparse.ArgumentParser()
ap.add_argument("--experiment", choices=["baseline", "top-k", "chunk-size"], required=True)
a = ap.parse_args()
try:
    print(run(a.experiment, SentenceTransformerEmbedder(), make_provider(Settings())))
except (RuntimeError, FileNotFoundError) as e:
    sys.exit(str(e))
