from typing import Any, Dict
from functools import lru_cache

# Portia SDK: minimal surface for running tools and handling OAuth clarifications.
SDK_AVAILABLE = True
try:
    from portia import Portia, ActionClarification, Plan, Step, PlanContext, Variable  # type: ignore
except Exception as e:
    SDK_AVAILABLE = False
    class ActionClarification(Exception):
        def __init__(self, action_url: str = "", clarification_id: str = ""):
            self.action_url = action_url
            self.clarification_id = clarification_id
    Portia = None  # type: ignore
    Plan = Step = PlanContext = Variable = None  # type: ignore

@lru_cache(maxsize=1)
def get_portia() -> "Portia | None":
    if not SDK_AVAILABLE:
        return None
    try:
        # Uses default_config(), which reads env (e.g., OPENAI_API_KEY)
        return Portia()  # type: ignore
    except Exception as e:
        # If misconfigured, treat as unavailable but report error downstream
        return None

def run_tool(tool_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    p = get_portia()
    if p is None:
        return {"ok": False, "sdkAvailable": False, "error": "Portia not initialized. Check API keys/provider."}
    try:
        # Build a one-step plan that invokes the tool with provided args
        variables = [Variable(name=k, description=f"input {k}") for k in args.keys()]
        step = Step(task=f"Run {tool_id}", inputs=variables, tool_id=tool_id, output="result")
        context = PlanContext(query=f"Execute tool {tool_id}", tool_ids=[tool_id])
        plan = Plan(plan_context=context, steps=[step])
        plan_run = p.run_plan(plan, plan_run_inputs=args)
        # Return raw plan run payload so caller can interpret
        return {"ok": True, "result": plan_run.model_dump()}
    except ActionClarification as ac:  # type: ignore
        return {
            "ok": False,
            "needsOAuth": True,
            "authUrl": getattr(ac, "action_url", ""),
            "clarificationId": getattr(ac, "clarification_id", ""),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def wait_for_ready(clarification_id: str, timeout_seconds: int = 180) -> Dict[str, Any]:
    p = get_portia()
    if p is None:
        return {"ok": True, "sdkAvailable": False, "result": {"clarification_id": clarification_id}}
    try:
        out = p.wait_for_ready(clarification_id=clarification_id, timeout=timeout_seconds)
        return {"ok": True, "result": out}
    except Exception as e:
        return {"ok": False, "error": str(e)}
