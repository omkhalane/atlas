import json
import logging
from typing import Optional, Dict, Any
from urllib.request import urlopen, Request

logger = logging.getLogger("atlas.browser.api")

class BrowserAPI:
    def __init__(self, connector_url: str = "http://127.0.0.1:3210"):
        self.connector_url = connector_url
        self.session_id: Optional[str] = None
        self._find_active_session()

    def _find_active_session(self):
        # In a real implementation, we'd query the connector server for active WS sessions
        # For this prototype, assume the connector knows where to route if session_id is omitted or discovered.
        pass

    def _send_command(self, action: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Executing browser command: {action} with {kwargs}")
        payload = {"action": action, **kwargs}
        # In the full implementation, this will send a REST call or WS message to connector_server.py
        # which forwards it to the extension.
        return {"status": "ok", "action": action}

    def open(self, url: str) -> None:
        """Navigates the connected browser to the specified URL."""
        self._send_command("navigate", url=url)

    def back(self) -> None:
        self._send_command("execute", script="window.history.back()")

    def forward(self) -> None:
        self._send_command("execute", script="window.history.forward()")

    def reload(self) -> None:
        self._send_command("execute", script="window.location.reload()")

    def click(self, target: str) -> None:
        """Clicks an element by intent or selector."""
        # This will use the intent_resolver in a later step
        from .intent_resolver import resolve_intent
        selector = resolve_intent(target)
        script = f"document.querySelector('{selector}').click()"
        self._send_command("execute", script=script)

    def type(self, target: str, text: str) -> None:
        from .intent_resolver import resolve_intent
        selector = resolve_intent(target)
        script = f"""
        const el = document.querySelector('{selector}');
        el.value = '{text}';
        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        """
        self._send_command("execute", script=script)

    def scroll(self, direction: str = "down") -> None:
        y_offset = 500 if direction == "down" else -500
        script = f"window.scrollBy(0, {y_offset})"
        self._send_command("execute", script=script)

    def get_page(self) -> Dict[str, Any]:
        """Returns the current state of the page."""
        return self._send_command("get_state")
