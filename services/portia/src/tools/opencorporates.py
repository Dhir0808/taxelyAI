import httpx, json
from pathlib import Path

BASE = "https://api.opencorporates.com/v0.4/companies"

def lookup_company(company_number: str | None = None, company_name: str | None = None):
    """
    Minimal wrapper:
    - If company_number is provided and jurisdiction is GB (default), use /companies/gb/{num} style.
    - Else if company_name is provided, use search endpoint.
    - Fallback to mock JSON if request fails.
    """
    try:
        with httpx.Client(timeout=6.0) as c:
            if company_number:
                url = f"{BASE}/gb/{company_number}"
                r = c.get(url)
                r.raise_for_status()
                return {"ok": True, "data": r.json(), "fallback": False}
            elif company_name:
                url = f"{BASE}/search?q={company_name}"
                r = c.get(url)
                r.raise_for_status()
                return {"ok": True, "data": r.json(), "fallback": False}
            else:
                raise ValueError("Provide company_number or company_name")
    except Exception as e:
        mock_path = Path(__file__).resolve().parent.parent.joinpath("mock/opencorporates_acme.json")
        if mock_path.exists():
            return {"ok": False, "data": json.loads(mock_path.read_text()), "fallback": True, "error": str(e)}
        return {"ok": False, "data": {"error":"fallback-missing","detail":str(e)}, "fallback": True, "error": str(e)}
