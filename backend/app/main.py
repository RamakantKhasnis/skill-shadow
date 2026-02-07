from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path
from datetime import datetime

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# --------------------
# App setup
# --------------------
app = FastAPI(title="Skill-Shadow Backend")

DATA_FILE = Path("../data/traces.json")
VECTOR_FILE = Path("../data/vectors.index")

# Load embedding model (local & free)
model = SentenceTransformer("all-MiniLM-L6-v2")
EMBEDDING_DIM = 384

# Load or create FAISS index
if VECTOR_FILE.exists():
    index = faiss.read_index(str(VECTOR_FILE))
else:
    index = faiss.IndexFlatL2(EMBEDDING_DIM)

# --------------------
# Data Model
# --------------------
class ThoughtTrace(BaseModel):
    error_signature: str
    summary: str
    files_changed: List[str]
    author: str

# --------------------
# Helpers
# --------------------
def read_traces():
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())

def save_traces(traces):
    DATA_FILE.write_text(json.dumps(traces, indent=2))

def save_index():
    faiss.write_index(index, str(VECTOR_FILE))

# --------------------
# Health check
# --------------------
@app.get("/")
def health_check():
    return {"status": "Skill-Shadow backend is running"}

# --------------------
# Save Thought Trace + embedding
# --------------------
@app.post("/trace")
def save_trace(trace: ThoughtTrace):
    traces = read_traces()

    record = trace.dict()
    record["timestamp"] = datetime.utcnow().isoformat()

    # Create embedding from error + summary
    text = f"{trace.error_signature}. {trace.summary}"
    embedding = model.encode([text])

    index.add(np.array(embedding).astype("float32"))
    save_index()

    traces.append(record)
    save_traces(traces)

    return {"message": "Thought Trace saved with embedding"}

# --------------------
# Get all traces
# --------------------
@app.get("/traces")
def get_all_traces():
    return read_traces()

# --------------------
# Semantic search
# --------------------
@app.get("/semantic-search")
def semantic_search(q: str, top_k: int = 3):
    traces = read_traces()
    if len(traces) == 0:
        return {"results": []}

    query_embedding = model.encode([q]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx in indices[0]:
        if idx < len(traces):
            results.append(traces[idx])

    return {
        "query": q,
        "results": results,
        "count": len(results)
    }