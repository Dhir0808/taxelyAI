def build_compliance(input_obj, calc, credits):
    items = [{"id":"ct600","label":"Prepare CT600 return","required":True}]
    if any(c["code"]=="R&D_SME" for c in credits):
        items.append({"id":"rd","label":"Attach R&D relief schedule","required":True})
    if any(c["code"]=="PATENT_BOX" for c in credits):
        items.append({"id":"pb","label":"Patent Box computation notes","required":True})
    return {
        "checklist": items,
        "disclaimer": "Hackathon demo. Not tax advice.",
        "summary": {
            "profitAfterCapex": calc["profit_after_capex"],
            "rateNormal": calc["rate_normal"],
            "taxPatent": calc["tax_patent"],
            "taxNormal": calc["tax_normal"],
            "totalTax": calc["total_tax"]
        }
    }
