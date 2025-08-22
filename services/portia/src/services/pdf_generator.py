from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors


def generate_ct600_pdf(data: dict, filepath: str):
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, height - 40, "HM Revenue & Customs – CT600 (2025)")
    c.setFont("Helvetica", 10)
    c.drawString(30, height - 60, f"Company: {data.get('company_name', 'N/A')}")
    c.drawString(30, height - 75, f"UTR: {data.get('utr', '1234567890')}")
    c.drawString(30, height - 90, f"Period: {data.get('period_start','')} to {data.get('period_end','')}")

    # pull values (accept both direct fields and nested under result.pdf)
    taxable = data.get("taxable_profit") or data.get("taxable_income") or 0
    rate_pct = data.get("corporation_tax_rate") or 25
    tax_due = data.get("corporation_tax_due") or data.get("corp_tax_due") or 0

    table_data = [
        ["Tax Computation", ""],
        ["Taxable Profit (£)", f"{float(taxable):,.2f}"],
        ["Corporation Tax Rate (%)", f"{rate_pct}"],
        ["Corporation Tax Due (£)", f"{float(tax_due):,.2f}"],
    ]
    table = Table(table_data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    table.wrapOn(c, width, height)
    table.drawOn(c, 30, height - 200)

    c.drawString(30, height - 300, "Declaration:")
    c.drawString(30, height - 315, "Submitted by Taxely AI")
    c.save()


def generate_rd_schedule_pdf(data: dict, filepath: str):
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, height - 40, "HM Revenue & Customs – CT600L (R&D Relief)")
    c.setFont("Helvetica", 10)
    c.drawString(30, height - 60, f"Company: {data.get('company_name', 'N/A')}")
    c.drawString(30, height - 75, f"Period: {data.get('period_start','')} to {data.get('period_end','')}")

    rd_exp = data.get("rd_expenditure") or 0
    rd_relief = data.get("rd_relief") or 0
    rd_credit = data.get("rd_credit") or 0

    table_data = [
        ["R&D Relief Schedule", ""],
        ["Qualifying Expenditure (£)", f"{float(rd_exp):,.2f}"],
        ["Relief Claimed (£)", f"{float(rd_relief):,.2f}"],
        ["Carry-forward/Credit (£)", f"{float(rd_credit):,.2f}"],
    ]
    table = Table(table_data, colWidths=[220, 180])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    table.wrapOn(c, width, height)
    table.drawOn(c, 30, height - 200)

    c.drawString(30, height - 300, "Declaration:")
    c.drawString(30, height - 315, "Submitted by Taxely AI")
    c.save()
