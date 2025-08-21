from typing import Dict, Any, List
from ..integrations.portia_sdk import run_tool, SDK_AVAILABLE

SHEETS_GET_TOOL_ID = "portia:google:sheets:get_spreadsheet"
DRIVE_LIST_TOOL_ID = "portia:google:drive:list_files"

def import_financials(spreadsheet_id: str, range_a1: str = "Sheet1!A1:B10") -> Dict[str, Any]:
    if not SDK_AVAILABLE:
        return {"ok": False, "sdkAvailable": False, "detail": "Portia SDK not available in this environment."}
    res = run_tool(SHEETS_GET_TOOL_ID, {"spreadsheet_id": spreadsheet_id, "range": range_a1})
    if res.get("needsOAuth"):
        return {"needsOAuth": True, "auth": {"authUrl": res["authUrl"], "clarificationId": res["clarificationId"]}}

    raw = (res.get("result") or {})
    values = raw.get("values") or raw.get("data") or []
    kv: Dict[str, Any] = {}
    if isinstance(values, list):
        for row in values:
            if isinstance(row, list) and len(row) >= 2:
                k, v = row[0], row[1]
                try:
                    kv[str(k).strip()] = float(str(v).replace(",", "").strip())
                except Exception:
                    kv[str(k).strip()] = v
    return {"parsed": kv, "raw": raw}


def list_user_sheets() -> Dict[str, Any]:
    if not SDK_AVAILABLE:
        return {"ok": False, "sdkAvailable": False, "detail": "Portia SDK not available in this environment."}
    res = run_tool(DRIVE_LIST_TOOL_ID, {
        "q": "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
        "fields": "files(id,name,mimeType,modifiedTime)",
        "page_size": 100,
    })
    if res.get("needsOAuth"):
        return {"needsOAuth": True, "auth": {"authUrl": res["authUrl"], "clarificationId": res["clarificationId"]}}

    raw = res.get("result") or {}
    files: List[Dict[str, Any]] = raw.get("files") or raw.get("items") or []
    out = []
    for f in files:
        out.append({
            "id": f.get("id"),
            "name": f.get("name") or f.get("title"),
            "modifiedTime": f.get("modifiedTime"),
        })
    return {"files": out, "raw": raw}
