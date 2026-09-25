"""Small HTTP JSON endpoint with no external dependencies."""

import json
import os
import re
from dataclasses import asdict, dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Mapping

from .providers import MockProvider, SmsProvider

MAX_BODY_BYTES = 65536
PHONE = re.compile(r"\+[1-9][0-9]{1,14}\Z")


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8080
    provider: str = "mock"
    api_credential: str = field(default="", repr=False)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        values = os.environ if env is None else env
        return cls(
            host=values.get("SMS_RELAY_HOST", "127.0.0.1"),
            port=int(values.get("SMS_RELAY_PORT", "8080")),
            provider=values.get("SMS_PROVIDER", "mock"),
            api_credential=values.get("SMS_PROVIDER_API_CREDENTIAL", ""),
        )


def build_provider(settings: Settings) -> SmsProvider:
    # Future adapters receive their credential here, never from a request body.
    if settings.provider != "mock":
        raise ValueError("Only the mock provider is supported")
    return MockProvider()


def validate_request(payload: object) -> dict[str, str]:
    if not isinstance(payload, dict) or set(payload) != {"to", "from", "message"}:
        raise ValueError("Exactly to, from, and message are required")
    for name in ("to", "from"):
        if not isinstance(payload[name], str) or PHONE.fullmatch(payload[name]) is None:
            raise ValueError(f"{name} must use E.164 format")
    if not isinstance(payload["message"], str) or not payload["message"].strip():
        raise ValueError("message must be a non-empty string")
    return payload


def make_server(settings: Settings, provider: SmsProvider | None = None) -> ThreadingHTTPServer:
    adapter = build_provider(settings) if provider is None else provider

    class Handler(BaseHTTPRequestHandler):
        server_version = "SmsRelayPrototype"
        sys_version = ""

        def log_message(self, format: str, *args: object) -> None:
            # Do not log paths, headers, bodies, credentials, or exception text.
            pass

        def setup(self) -> None:
            super().setup()
            self.connection.settimeout(10)

        def reply(self, status: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            if self.path != "/sms/deliver":
                self.reply(404, {"error": "not_found"})
                return
            if self.headers.get_content_type() != "application/json":
                self.reply(415, {"error": "application_json_required"})
                return
            lengths = self.headers.get_all("Content-Length", [])
            if self.headers.get("Transfer-Encoding") or len(lengths) != 1:
                self.reply(400, {"error": "invalid_content_length"})
                return
            try:
                if not lengths[0].isascii() or not lengths[0].isdigit():
                    raise ValueError()
                length = int(lengths[0])
                if length <= 0:
                    raise ValueError()
            except ValueError:
                self.reply(400, {"error": "invalid_content_length"})
                return
            if length > MAX_BODY_BYTES:
                self.reply(413, {"error": "request_too_large"})
                return
            try:
                raw = self.rfile.read(length)
                if len(raw) != length:
                    raise ValueError()
                payload = validate_request(json.loads(raw))
            except (ValueError, UnicodeError, RecursionError, OSError):
                self.reply(400, {"error": "invalid_request"})
                return
            try:
                result = adapter.deliver(
                    to=payload["to"], from_=payload["from"], message=payload["message"]
                )
                self.reply(200, asdict(result))
            except Exception:
                # Provider failures may contain credentials. Never echo or log them.
                self.reply(502, {"error": "provider_error"})

    return ThreadingHTTPServer((settings.host, settings.port), Handler)


def main() -> None:
    try:
        settings = Settings.from_env()
        server = make_server(settings)
    except Exception:
        raise SystemExit("SMS relay configuration/startup failed") from None
    print("SMS Relay prototype started (mock provider)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
