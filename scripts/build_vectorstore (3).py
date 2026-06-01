# scripts/build_vectorstore.py
# =============================
# Builds a FAISS vector index for each agent from data/bubbles/.
# Each agent gets its own index in assets/vectorstores/<slug>/
#
# HOW TO USE:
#   python scripts/build_vectorstore.py

# Imports
from pathlib import Path
import pickle
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# Folder paths and embedding model name

BUBBLES_DIR = Path("data/bubbles")
VECTOR_DIR = Path("assets/vectorstores")
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

VECTOR_DIR.mkdir(parents=True, exist_ok=True)

# Load the embedding model
model = SentenceTransformer(MODEL_NAME)

# Read bubble files
for bubble_path in sorted(BUBBLES_DIR.glob("*.jsonl")):
    slug = bubble_path.stem
    df = pd.read_json(bubble_path, lines=True)

    df = df[df["text"].fillna("").str.strip() != ""].copy()
    if df.empty:
        # Print progress
        print(f"{slug}: skipped, no texts")
        continue

    texts = df["text"].tolist()
# Generate embeddings
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    ).astype("float32")
# Create the FAISS index
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    out_dir = VECTOR_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
# Save index.faiss
    faiss.write_index(index, str(out_dir / "index.faiss"))
# Save index.pkl
    with open(out_dir / "index.pkl", "wb") as f:
        pickle.dump(df.to_dict(orient="records"), f)
# Print progress
    print(f"{slug}: {len(texts)} texte -> {out_dir}")
# Print progress
print("Gata. Vectorstore-urile au fost create.")