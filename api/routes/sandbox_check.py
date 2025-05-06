from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.sandbox_client import call_sandbox_microservice  # ✅ safe import


router = APIRouter()

class SandboxInput(BaseModel):
    url: str

@router.post("/sandbox-check")
async def sandbox_check(input: SandboxInput):
    report = await call_sandbox_microservice(input.url)
    if "error" in report:
        raise HTTPException(status_code=500, detail=report["error"])
    return {"sandbox_report": report}

