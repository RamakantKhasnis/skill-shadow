from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json
from pathlib import Path
from datetime import datetime

# Initialize app
app = FastAPI(title="Skill-Shadow Backend")

# Path to local data file
DATA_FILE = Path("../data/traces.json")


# -----------------------
# Data Model
# -----------------------
class ThoughtTrace(BaseModel):
    error_signature: str
    summary: str
    files_changed: List[str]
    author: str


# -----------------------
# Health Check
# -----------------------
@app.get("/")
def health_check():
    return {"status": "Skill-Shadow backend is running"}


# -----------------------
# Save Thought Trace
# -----------------------
@app.post("/trace")
def save_trace(trace: ThoughtTrace):
    # Ensure data file exists
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("[]")

    # Load existing traces
    existing_traces = json.loads(DATA_FILE.read_text())

    # Create new record
    record = trace.dict()
    record["timestamp"] = datetime.utcnow().isoformat()

    # Append and save
    existing_traces.append(record)
    DATA_FILE.write_text(json.dumps(existing_traces, indent=2))

    return {"message": "Thought Trace saved successfully"}