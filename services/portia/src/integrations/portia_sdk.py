from typing import Any, Dict

# Portia SDK: allow import even if version differs; keep surface minimal.
SDK_AVAILABLE = True
try:
    from portia import Client, ActionClarification  # type: ignore
except Exception as e:  # fallback shims so code still imports
    SDK_AVAILABLE = False
    class ActionClarification(Exception):
        def __init__(self, action_url: str = "", clarification_id: str = ""):
            self.action_url = action_url
            self.clarification_id = clarification_id
    class Client:  # type: ignore
        def __init__(self, *args, **kwargs): ...
        def run_tool(self, tool_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
            return {"ok": False, "error": "Portia SDK not available"}
        def wait_for_ready(self, clarification_id: str, timeout: int = 180) -> Dict[str, Any]:
            return {"ok": True, "clarification_id": clarification_id}

def _client() -> "Client":
    # No API key required: tools requiring OAuth will raise ActionClarification with auth URL.
    return Client()

def run_tool(tool_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if not SDK_AVAILABLE:
        return {"ok": False, "sdkAvailable": False, "error": "Portia SDK not available"}
    client = _client()
    try:
        out = client.run_tool(tool_id=tool_id, args=args)
        return {"ok": True, "result": out}
    except ActionClarification as ac:  # type: ignore
        return {
            "ok": False,
            "needsOAuth": True,
            "authUrl": getattr(ac, "action_url", ""),
            "clarificationId": getattr(ac, "clarification_id", "")
        }

def wait_for_ready(clarification_id: str, timeout_seconds: int = 180) -> Dict[str, Any]:
    if not SDK_AVAILABLE:
        return {"ok": True, "sdkAvailable": False, "result": {"clarification_id": clarification_id}}
    client = _client()
    out = client.wait_for_ready(clarification_id=clarification_id, timeout=timeout_seconds)
    return {"ok": True, "result": out}
