from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from sandbox.sandbox_runner import sandbox_analyze

app = FastAPI(title="Sandbox Microservice")

# 📥 Input schema
class SandboxRequest(BaseModel):
    url: str

# 🚀 Endpoint to trigger sandbox analysis
@app.post("/analyze")
async def analyze_url(input: SandboxRequest):
    try:
        report = await sandbox_analyze(input.url)
        return {"sandbox_report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sandbox analysis failed: {str(e)}")

# 🌐 Health check
@app.get("/")
def root():
    return {"message": "Sandbox service is up and running!"}

