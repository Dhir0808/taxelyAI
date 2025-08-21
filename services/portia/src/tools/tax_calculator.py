from dataclasses import dataclass

@dataclass
class TaxCalcResult:
    profit_before_capex: float
    profit_after_capex: float
    rate_normal: float
    patent_slice: float
    normal_slice: float
    tax_patent: float
    tax_normal: float
    total_tax: float

def _band_rate(p: float, lower_lim=50_000, upper_lim=250_000, small=0.19, main=0.25) -> float:
    if p <= lower_lim: return small
    if p >= upper_lim: return main
    t = (p - lower_lim) / (upper_lim - lower_lim)
    return small + t * (main - small)

def compute_corp_tax(profit_gbp: float, patent_revenue_gbp: float | None, capex_gbp: float | None) -> TaxCalcResult:
    profit_before_capex = max(0.0, profit_gbp)
    profit_after_capex  = max(0.0, profit_before_capex - (capex_gbp or 0.0))
    patent_slice = min(patent_revenue_gbp or 0.0, profit_after_capex)
    normal_slice = max(0.0, profit_after_capex - patent_slice)
    rate_normal  = _band_rate(profit_after_capex)
    tax_patent   = patent_slice * 0.10
    tax_normal   = normal_slice * rate_normal
    total_tax    = tax_patent + tax_normal
    return TaxCalcResult(
        profit_before_capex, profit_after_capex, rate_normal,
        patent_slice, normal_slice, tax_patent, tax_normal, total_tax
    )
