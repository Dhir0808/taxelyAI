import base64, os, httpx, json
from pathlib import Path

BASE = "https://api.company-information.service.gov.uk/company/"

def _auth_header():
    key = os.getenv("COMPANIES_HOUSE_KEY","")
    token = base64.b64encode(f"{key}:".encode()).decode()
    return {"Authorization": f"Basic {token}"}

def lookup_company(company_number: str | None, company_name: str | None = None):
    # For hackathon: prefer number. If missing, return mock (name search needs different endpoint).
    try:
        if not company_number:
            raise ValueError("No company_number provided")
        url = BASE + company_number
        with httpx.Client(timeout=6.0) as c:
            r = c.get(url, headers=_auth_header())
            r.raise_for_status()
            return {"ok": True, "data": r.json(), "fallback": False}
    except Exception as e:
        mock_path = Path(__file__).resolve().parent.parent.joinpath("mock/companies_house_acme.json")
        return {"ok": False, "data": json.loads(mock_path.read_text()), "fallback": True, "error": str(e)}
