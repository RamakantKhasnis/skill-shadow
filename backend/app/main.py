from fastapi import FastAPI

app = FastAPI(title="Skill-Shadow Backend")

@app.get("/")
def health_check():
    return {"status": "Skill-Shadow backend is running"}