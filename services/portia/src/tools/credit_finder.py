import json
from pathlib import Path

KB = json.loads(Path(__file__).resolve().parent.parent.joinpath("kb/uk_tax_rules.json").read_text())

def find_credits(r_and_d_spend_gbp: float | None, capex_gbp: float | None, patent_revenue_gbp: float | None):
    suggestions = []
    if (r_and_d_spend_gbp or 0) > 0:
        suggestions.append({"code":"R&D_SME","title":"SME R&D Relief","note":KB["credits"]["RD_SME"]["summary"],"estBenefit":"Enhanced deduction (demo)"})
    if (capex_gbp or 0) > 0:
        suggestions.append({"code":"AIA","title":"Annual Investment Allowance","note":KB["credits"]["AIA"]["summary"],"estBenefit":"Capex deducted (demo)"})
    if (patent_revenue_gbp or 0) > 0:
        suggestions.append({"code":"PATENT_BOX","title":"Patent Box","note":KB["credits"]["PATENT_BOX"]["summary"],"estBenefit":"10% on patent profits (demo)"})
    return suggestions
