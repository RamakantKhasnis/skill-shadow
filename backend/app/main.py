from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path
from datetime import datetime

# --------------------
# App setup
# --------------------
app = FastAPI(title="Skill-Shadow Backend")

# Path to local data file
DATA_FILE = Path("../data/traces.json")

# --------------------
# Data Model
# --------------------
class ThoughtTrace(BaseModel):
    error_signature: str
    summary: str
    files_changed: List[str]
    author: str

# --------------------
# Helper function
# --------------------
def read_traces():
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())

# --------------------
# Health check
# --------------------
@app.get("/")
def health_check():
    return {"status": "Skill-Shadow backend is running"}

# --------------------
# Save a Thought Trace
# --------------------
@app.post("/trace")
def save_trace(trace: ThoughtTrace):
    traces = read_traces()

    record = trace.dict()
    record["timestamp"] = datetime.utcnow().isoformat()

    traces.append(record)
    DATA_FILE.write_text(json.dumps(traces, indent=2))

    return {"message": "Thought Trace saved successfully"}

# --------------------
# Get all Thought Traces
# --------------------
@app.get("/traces")
def get_all_traces():
    return read_traces()

# --------------------
# Search Thought Traces
# --------------------
@app.get("/search")
def search_traces(q: str):
    traces = read_traces()
    q_lower = q.lower()

    results = [
        trace for trace in traces
        if q_lower in trace["error_signature"].lower()
        or q_lower in trace["summary"].lower()
    ]

    return {
        "query": q,
        "count": len(results),
        "results": results
    }