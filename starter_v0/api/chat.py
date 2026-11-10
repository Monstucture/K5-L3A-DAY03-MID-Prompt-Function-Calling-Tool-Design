"""Vercel Python function: POST /api/chat {"message": str, "history": [{role, content}]}.

Stateless: the browser keeps the history. Run locally with `python api/chat.py` (serves public/ too).
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from chat import ARTIFACTS_DIR, json_text, run_model_tool_loop, trim_history  # noqa: E402  (chat.py also loads .env)
from providers import make_provider  # noqa: E402
from tools import load_tool_declarations, to_openai_tools  # noqa: E402

PROVIDER = os.getenv("DEMO_PROVIDER", "openrouter")
SYSTEM_PROMPT = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
TOOLS = to_openai_tools(load_tool_declarations(ARTIFACTS_DIR / "tools.yaml"))
MAX_MESSAGE_CHARS = 2000
LOG_FILE = Path(os.getenv("DEMO_LOG_FILE", ROOT / "logs" / "demo_chat.jsonl"))
_log_lock = threading.Lock()


def log_turn(entry: dict) -> None:
    """Print a short summary and append the full turn as one JSON line to LOG_FILE."""
    tools = ", ".join(f"{t['name']}{'' if t['ok'] else '(ERR)'}" for t in entry["tools"]) or "-"
    print(f"[{entry['time']}] Q: {entry['question'][:120]!r} | tools: {tools} | {entry['status']} | {entry['duration_s']}s")
    try:
        with _log_lock:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    except OSError as exc:  # e.g. read-only filesystem on Vercel: keep serving, just skip the file
        print(f"log write failed: {exc}")


class handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8"))

    def do_POST(self) -> None:
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            message = str(data.get("message", "")).strip()[:MAX_MESSAGE_CHARS]
            history = [
                {"role": m["role"], "content": str(m["content"])[:MAX_MESSAGE_CHARS]}
                for m in data.get("history", [])
                if isinstance(m, dict) and m.get("role") in ("user", "assistant") and "content" in m
            ]
        except (ValueError, TypeError, KeyError):
            return self._json(400, {"error": "invalid JSON body"})
        if not message:
            return self._json(400, {"error": "message is required"})

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *trim_history(history, 5),
            {"role": "user", "content": message},
        ]
        started = time.monotonic()
        entry = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "provider": PROVIDER,
            "question": message,
            "history_messages": len(history),
            "status": "provider_error",
            "tools": [],
            "reply": None,
        }
        try:
            result = run_model_tool_loop(
                provider=make_provider(PROVIDER), messages=messages, tools=TOOLS, model=None, max_tool_rounds=4
            )
        except Exception as exc:
            entry.update(error=f"{type(exc).__name__}: {exc}", duration_s=round(time.monotonic() - started, 1))
            log_turn(entry)
            return self._json(502, {"error": entry["error"]})
        # One entry per model round: what it said, which tools it called, and a trimmed view of each result.
        steps = [
            {
                "round": r["round"],
                "assistant_text": r["assistant_text"],
                "tools": [
                    {
                        "name": e["tool"],
                        "args": e["args"],
                        "ok": not (isinstance(e["result"], dict) and "error" in e["result"]),
                        "result": json_text(e["result"], max_chars=800),
                    }
                    for e in r["tool_results"]
                ],
            }
            for r in result["rounds"]
        ]
        entry.update(
            status=result["status"],
            reply=result["assistant_text"],
            duration_s=round(time.monotonic() - started, 1),
            tools=[
                {
                    "round": s["round"],
                    "name": t["name"],
                    "args": t["args"],
                    "ok": t["ok"],
                    "error": None if t["ok"] else t["result"][:300],
                }
                for s in steps
                for t in s["tools"]
            ],
        )
        log_turn(entry)
        self._json(200, {"status": result["status"], "reply": result["assistant_text"], "steps": steps})

    # Local dev only: Vercel serves public/ itself.
    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            return self._send(200, (ROOT / "public" / "index.html").read_bytes(), "text/html; charset=utf-8")
        self._json(404, {"error": "not found"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Demo on http://localhost:{port}  (provider={PROVIDER})")
    ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()
