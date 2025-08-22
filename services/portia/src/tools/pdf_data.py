from typing import Dict, Any

def build_ct600_pdf_data(normalized: Dict[str, Any], compute: Dict[str, Any]) -> Dict[str, Any]:
    bd = (compute or {}).get("breakdown", {})
    taxable_profit = float(bd.get("profit_after_rd", 0) or 0)
    corp_tax_rate = float(bd.get("rate_normal", 0) or 0) * 100.0
    corp_tax_due = float(bd.get("total_tax", 0) or 0)

    year_end = normalized.get("yearEnd") or f"{normalized.get('accountingYear')}-12-31"
    period_start = f"{normalized.get('accountingYear')}-01-01"
    period_end = year_end

    return {
        "company_name": normalized.get("companyName") or "N/A",
        "utr": "1234567890",
        "period_start": period_start,
        "period_end": period_end,
        "taxable_income": round(taxable_profit, 2),
        "corporation_tax_rate": round(corp_tax_rate, 2),
        "corp_tax_due": round(corp_tax_due, 2),
    }


def build_rd_pdf_data(normalized: Dict[str, Any], compute: Dict[str, Any]) -> Dict[str, Any]:
    bd = (compute or {}).get("breakdown", {})
    rd_spend = float(normalized.get("rAndDSpendGBP", 0) or 0)
    rd_extra = float(bd.get("rd_extra_deduction", 0) or 0)

    year_end = normalized.get("yearEnd") or f"{normalized.get('accountingYear')}-12-31"
    period_start = f"{normalized.get('accountingYear')}-01-01"
    period_end = year_end

    return {
        "company_name": normalized.get("companyName") or "N/A",
        "period_start": period_start,
        "period_end": period_end,
        "rd_expenditure": round(rd_spend, 2),
        "rd_relief": round(rd_extra, 2),
        "rd_credit": 0.0,
    }
