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

# --- Normalization endpoints ---
from .tools.normalize import normalize_kv

class NormalizeReq(BaseModel):
    kv: dict

@app.post("/api/normalize")
def api_normalize(req: NormalizeReq):
    return normalize_kv(req.kv)

@app.get("/api/schema/template")
def api_schema_template():
    csv_text = (
        "key,value\n"
        "companyName,ACME TECH LTD\n"
        "companyNumber,01234567\n"
        "accountingYear,2024\n"
        "yearEnd,2024-12-31\n"
        "revenueGBP,20000000\n"
        "expensesGBP,14000000\n"
        "rAndDSpendGBP,3000000\n"
        "capexGBP,1000000\n"
        "patentRevenueGBP,500000\n"
        "applyCredits,true\n"
    )
    return {"templateCsv": csv_text}

# --- Compute endpoint (normalized breakdown) ---
from .tools.compute import compute_from_kv

class ComputeReq(BaseModel):
    kv: dict

@app.post("/api/compute")
def api_compute(req: ComputeReq):
    return compute_from_kv(req.kv)
