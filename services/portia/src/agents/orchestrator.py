from pydantic import BaseModel
from typing import Optional, Any, Dict, List

# Attempt to import Portia SDK. If unavailable or symbol names differ, fall back to minimal shims.
try:  # type: ignore
    from portia import Agent as PortiaAgent, Tool as PortiaTool, Plan as PortiaPlan, Step as PortiaStep  # noqa: F401
    USING_PORTIA = True
except Exception:  # pragma: no cover
    USING_PORTIA = False
    PortiaAgent = None
    PortiaTool = object  # type: ignore
    PortiaPlan = object  # type: ignore
    PortiaStep = object  # type: ignore

from ..tools.opencorporates import lookup_company
from ..tools.tax_calculator import compute_corp_tax
from ..tools.credit_finder import find_credits
from ..tools.compliance import build_compliance
from ..services.pdf_generator import generate_ct600_pdf, generate_rd_schedule_pdf
from pathlib import Path

class CompanyInput(BaseModel):
    companyName: Optional[str] = None
    companyNumber: Optional[str] = None
    accountingYear: int
    revenueGBP: float
    expensesGBP: float
    rAndDSpendGBP: Optional[float] = 0.0
    patentRevenueGBP: Optional[float] = 0.0
    capexGBP: Optional[float] = 0.0
    applyCredits: Optional[bool] = True

def _calc_profit(ci: CompanyInput) -> float:
    r = ci.revenueGBP or 0.0
    e = ci.expensesGBP or 0.0
    return r - e if (r - e) > 0 else 0.0

# --- Minimal shim classes if Portia SDK is absent ---
if not USING_PORTIA:
    class Tool:  # noqa: D401
        """Minimal Tool base class with a call(args) method to override."""
        name: str = "tool"
        description: str = ""
        def call(self, args: dict) -> Any:  # pragma: no cover
            raise NotImplementedError

    class Step:
        def __init__(self, id: str, tool: Optional[str] = None, input_schema: Optional[dict] = None):
            self.id = id
            self.tool = tool
            self.input_schema = input_schema or {}

    class Plan:
        def __init__(self, steps: List[Step]):
            self.steps = steps

    class Agent:
        def __init__(self, name: str, plan: Plan, tools: List[Tool], human_in_the_loop: bool = True):
            self.name = name
            self.plan = plan
            self.tools = {t.name: t for t in tools}
            self.human_in_the_loop = human_in_the_loop
        def use(self, tool_name: str, args: dict) -> Any:
            tool = self.tools.get(tool_name)
            if tool is None:
                raise ValueError(f"Unknown tool: {tool_name}")
            return tool.call(args)
else:  # If Portia SDK is available, alias to its classes
    Tool = PortiaTool  # type: ignore
    Step = PortiaStep  # type: ignore
    Plan = PortiaPlan  # type: ignore
    class Agent(PortiaAgent):  # type: ignore
        pass

# --- Tools ---
class OpenCorporatesTool(Tool):
    name = "opencorporates_lookup"
    description = "Fetch company details from OpenCorporates; fallback to mock if request fails."
    def call(self, args: dict) -> Any:
        return lookup_company(args.get("companyNumber"), args.get("companyName"))

class TaxCalculatorTool(Tool):
    name = "tax_calculator"
    description = "Compute UK corp tax using simplified rules (demo)."
    def call(self, args: dict) -> Any:
        calc = compute_corp_tax(args["profitGBP"], args.get("patentRevenueGBP"), args.get("capexGBP"))
        return calc.__dict__

class CreditFinderTool(Tool):
    name = "credit_finder"
    description = "Suggest credits (R&D, AIA, Patent Box) from offline KB."
    def call(self, args: dict) -> Any:
        return find_credits(args.get("rAndDSpendGBP"), args.get("capexGBP"), args.get("patentRevenueGBP"))

class ComplianceTool(Tool):
    name = "compliance_builder"
    description = "Build compliance checklist + summary."
    def call(self, args: dict) -> Any:
        return build_compliance(args["input"], args["calc"], args["credits"])

def build_agent() -> Agent:
    tools = [OpenCorporatesTool(), TaxCalculatorTool(), CreditFinderTool(), ComplianceTool()]
    plan = Plan(steps=[
        Step(id="calc-profit", tool=None, input_schema={"fields":["revenueGBP","expensesGBP"]}),
        Step(id="opencorporates", tool="opencorporates_lookup"),
        Step(id="corp-tax", tool="tax_calculator"),
        Step(id="credits", tool="credit_finder"),
        Step(id="hitl", tool=None),
        Step(id="compliance", tool="compliance_builder")
    ])
    return Agent(name="Taxely UK Copilot", plan=plan, tools=tools, human_in_the_loop=True)

def run_orchestration(payload: dict) -> dict:
    ci = CompanyInput(**payload)
    agent = build_agent()

    trace: List[Dict[str, Any]] = []

    # Step 1: profit
    profit_gbp = _calc_profit(ci)
    trace.append({"step":"calc-profit", "profitGBP": profit_gbp})

    # Step 2: OpenCorporates
    oc = agent.use("opencorporates_lookup", {"companyNumber": ci.companyNumber, "companyName": ci.companyName})
    trace.append({"step":"opencorporates", "ok": oc.get("ok"), "fallback": oc.get("fallback")})

    # Step 3: corp tax (offline)
    calc = agent.use("tax_calculator", {
        "profitGBP": profit_gbp,
        "patentRevenueGBP": ci.patentRevenueGBP,
        "capexGBP": ci.capexGBP
    })
    trace.append({"step":"corp-tax", "detail": {"rate": calc["rate_normal"], "totalTax": calc["total_tax"]}})

    # Step 4: credits
    credits = agent.use("credit_finder", {
        "rAndDSpendGBP": ci.rAndDSpendGBP,
        "capexGBP": ci.capexGBP,
        "patentRevenueGBP": ci.patentRevenueGBP
    })
    trace.append({"step":"credits", "count": len(credits)})

    # Step 5: human-in-the-loop (simulated by flag)
    trace.append({"step":"hitl", "applyCredits": bool(ci.applyCredits)})

    # Step 6: compliance
    compliance = agent.use("compliance_builder", {"input": ci.model_dump(), "calc": calc, "credits": credits})
    trace.append({"step":"compliance", "items": len(compliance["checklist"])})

    # Generate PDFs (HMRC-style fields)
    outputs_dir = Path(__file__).resolve().parents[2].joinpath("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)

    period_start = f"{ci.accountingYear}-01-01"
    period_end = f"{ci.accountingYear}-12-31"

    ct600_data = {
        "company_name": ci.companyName or "N/A",
        "utr": "1234567890",
        "period_start": period_start,
        "period_end": period_end,
        "taxable_income": calc.get("profit_after_capex") or calc.get("profit_before_capex") or 0,
        "corp_tax_due": calc.get("total_tax") or 0,
    }
    rd_data = {
        "company_name": ci.companyName or "N/A",
        "period_start": period_start,
        "period_end": period_end,
        "rd_expenditure": ci.rAndDSpendGBP or 0,
        "rd_relief": 0,
        "rd_credit": 0,
    }

    ct600_path = outputs_dir.joinpath("ct600.pdf")
    rd_path = outputs_dir.joinpath("rd_schedule.pdf")
    try:
        generate_ct600_pdf(ct600_data, str(ct600_path))
        generate_rd_schedule_pdf(rd_data, str(rd_path))
    except Exception:
        pass

    return {
        "plan": trace,
        "company": oc.get("data"),
        "input": ci.model_dump(),
        "result": {
            "taxBreakdown": calc,
            "credits": credits,
            "compliance": compliance,
            "outputs": {"ct600": str(ct600_path), "rd_schedule": str(rd_path)}
        }
    }
