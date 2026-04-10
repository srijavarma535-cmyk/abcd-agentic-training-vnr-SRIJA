import os
import httpx
from langchain_core.tools import tool

@tool
def send_pushover_alert(title: str, message: str) -> dict:
    """Send a push notification via Pushover."""
    user_key = os.getenv("PUSHOVER_USER_KEY", "")
    app_token = os.getenv("PUSHOVER_APP_TOKEN", "")
    if not user_key or not app_token:
        print("[Pushover] Skipped - credentials not set in .env")
        return {"status": "skipped"}
    try:
        resp = httpx.post("https://api.pushover.net/1/messages.json", data={
            "token": app_token, "user": user_key,
            "title": title[:250], "message": message[:1024],
        }, timeout=10)
        return resp.json()
    except Exception as e:
        return {"status": "error", "reason": str(e)}
