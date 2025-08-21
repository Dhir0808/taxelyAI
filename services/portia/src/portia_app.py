import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .agents.orchestrator import run_orchestration

app = FastAPI(title="Taxely Agent Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.post("/api/run")
def run(payload: dict):
    try:
        return run_orchestration(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Additional endpoints: Sheets import via Portia + OAuth wait ---
from pydantic import BaseModel
from fastapi import Query
from .tools.sheets_portia import import_financials, list_user_sheets
from .integrations.portia_sdk import wait_for_ready

class SheetsImportReq(BaseModel):
    spreadsheetId: str
    rangeA1: str | None = "Sheet1!A1:B10"

@app.post("/api/sheets/import")
def api_sheets_import(req: SheetsImportReq):
    out = import_financials(req.spreadsheetId, req.rangeA1 or "Sheet1!A1:B10")
    return out

@app.get("/api/portia/wait")
def api_portia_wait(clarification_id: str = Query(...)):
    return wait_for_ready(clarification_id)

@app.get("/api/sheets/list")
def api_sheets_list():
    return list_user_sheets()
