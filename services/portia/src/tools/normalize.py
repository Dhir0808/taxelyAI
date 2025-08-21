from typing import Dict, Any, List
from ..schema.input_schema import NormalizedInput, _coerce_num

REQUIRED = ["accountingYear", "revenueGBP", "expensesGBP"]
OPTIONAL = [
    "companyName",
    "companyNumber",
    "yearEnd",
    "rAndDSpendGBP",
    "capexGBP",
    "patentRevenueGBP",
    "applyCredits",
]

def _coerce_bool(v):
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("1", "true", "yes", "y"):
        return True
    if s in ("0", "false", "no", "n"):
        return False
    return None


def normalize_kv(kv: Dict[str, Any]) -> Dict[str, Any]:
    ks = {str(k).strip(): kv[k] for k in kv}
    missing = [k for k in REQUIRED if k not in ks]
    unknown = [k for k in ks if k not in REQUIRED + OPTIONAL]
    issues: List[Dict[str, str]] = []

    candidate: Dict[str, Any] = {}

    # passthrough strings
    for k in ("companyName", "companyNumber", "yearEnd"):
        if k in ks:
            candidate[k] = None if ks[k] in ("", None) else str(ks[k]).strip()

    # numbers
    for k in (
        "accountingYear",
        "revenueGBP",
        "expensesGBP",
        "rAndDSpendGBP",
        "capexGBP",
        "patentRevenueGBP",
    ):
        if k in ks:
            val = _coerce_num(ks[k])
            if val is None:
                issues.append({"field": k, "problem": "not_numeric", "hint": "Provide a number (e.g., 1200000)"})
            else:
                if k == "accountingYear":
                    val = int(val)
                candidate[k] = val

    if "applyCredits" in ks:
        b = _coerce_bool(ks["applyCredits"])
        if b is None:
            issues.append({"field": "applyCredits", "problem": "not_boolean", "hint": "Use true/false or yes/no"})
        else:
            candidate["applyCredits"] = b

    normalized = None
    try:
        normalized = NormalizedInput(**candidate).dict()
    except Exception as e:
        issues.append({"field": "__pydantic__", "problem": "validation_error", "hint": str(e)})

    return {
        "normalized": normalized,
        "missing": missing,
        "unknown": unknown,
        "issues": issues,
    }
