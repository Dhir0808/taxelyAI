from typing import Dict, Any
from pathlib import Path
import json

from ..tools.normalize import normalize_kv

KB_PATH = Path(__file__).resolve().parent.parent.joinpath("kb/uk_tax_rules.json")
KB = json.loads(KB_PATH.read_text()) if KB_PATH.exists() else {}

PATENT_BOX_RATE = 0.10
# Demo R&D additional deduction factor (illustrative only)
RD_ADDITIONAL_DEDUCTION = 0.86


def _band_rate(p: float, lower_lim=50_000, upper_lim=250_000, small=0.19, main=0.25) -> float:
    if p <= lower_lim:
        return small
    if p >= upper_lim:
        return main
    t = (p - lower_lim) / (upper_lim - lower_lim)
    return small + t * (main - small)


def compute_from_kv(kv: Dict[str, Any]) -> Dict[str, Any]:
    norm = normalize_kv(kv)
    ni = norm.get("normalized") or {}

    revenue = float(ni.get("revenueGBP") or 0)
    expenses = float(ni.get("expensesGBP") or 0)
    r_and_d_spend = float(ni.get("rAndDSpendGBP") or 0)
    capex = float(ni.get("capexGBP") or 0)
    patent_rev = float(ni.get("patentRevenueGBP") or 0)
    apply_credits = bool(ni.get("applyCredits", True))

    profit_before_capex = max(0.0, revenue - expenses)
    profit_after_capex = max(0.0, profit_before_capex - capex)

    rd_extra_deduction = (r_and_d_spend * RD_ADDITIONAL_DEDUCTION) if apply_credits else 0.0
    profit_after_rd = max(0.0, profit_after_capex - rd_extra_deduction)

    patent_slice = min(patent_rev, profit_after_rd)
    normal_slice = max(0.0, profit_after_rd - patent_slice)

    rate_normal = _band_rate(profit_after_rd)
    tax_patent = patent_slice * PATENT_BOX_RATE
    tax_normal = normal_slice * rate_normal
    total_tax = tax_patent + tax_normal

    breakdown = {
        "profit_before_capex": profit_before_capex,
        "profit_after_capex": profit_after_capex,
        "profit_after_rd": profit_after_rd,
        "patent_slice": patent_slice,
        "normal_slice": normal_slice,
        "rate_normal": rate_normal,
        "tax_patent": tax_patent,
        "tax_normal": tax_normal,
        "total_tax": total_tax,
        "rd_extra_deduction": rd_extra_deduction,
    }

    corpTax = KB.get("corpTax", {})
    notes = [
        KB.get("corpTax", {}).get("marginalReliefNote") or "Marginal relief approximated linearly.",
        "R&D relief illustrative only; not HMRC-compliant.",
        "Patent Box assumed at 10% for relevant profits.",
        "Hackathon demo. Not tax advice.",
    ]
    assumptions = {
        "bands": corpTax,
        "patentBoxRate": PATENT_BOX_RATE,
        "notes": notes,
    }

    # PDF-friendly fields
    pdf = {
        "company_name": ni.get("companyName") or "N/A",
        "utr": "1234567890",
        "period_start": f"{int(ni.get('accountingYear', 0))}-01-01" if ni.get("accountingYear") else "",
        "period_end": f"{int(ni.get('accountingYear', 0))}-12-31" if ni.get("accountingYear") else "",
        "taxable_profit": breakdown["profit_after_rd"],
        "corporation_tax_rate": round(rate_normal * 100, 2),
        "corporation_tax_due": total_tax,
    }

    return {
        "input": ni or None,
        "issues": norm.get("issues", []),
        "missing": norm.get("missing", []),
        "unknown": norm.get("unknown", []),
        "result": {
            "breakdown": breakdown,
            "assumptions": assumptions,
            "pdf": pdf,
        },
    }
