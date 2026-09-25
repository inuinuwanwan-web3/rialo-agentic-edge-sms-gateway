import contextlib
import http.client
import io
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest

from sms_relay.providers import DeliveryResult
from sms_relay.server import Settings, build_provider, make_server


VALID = {"to": "+12025550101", "from": "+12025550102", "message": "Mock SMS"}


class RelayTests(unittest.TestCase):
    def setUp(self):
        self.server = make_server(Settings(port=0))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def post(self, payload, path="/sms/deliver"):
        client = http.client.HTTPConnection(*self.server.server_address, timeout=3)
        try:
            client.request("POST", path, json.dumps(payload), {"Content-Type": "application/json"})
            response = client.getresponse()
            return response.status, response.getheader("Content-Type"), json.loads(response.read())
        finally:
            client.close()

    def test_valid_request_and_response_format(self):
        status, content_type, body = self.post(VALID)
        self.assertEqual(status, 200)
        self.assertTrue(content_type.startswith("application/json"))
        self.assertEqual(set(body), {"message_id", "status"})
        self.assertEqual(body["status"], "delivered")
        self.assertRegex(body["message_id"], r"^mock_[0-9a-f]{32}$")

    def test_invalid_phone(self):
        for field in ("to", "from"):
            for value in ("123", "+0123", "+１２３", "+123\n", None):
                with self.subTest(field=field, value=value):
                    self.assertEqual(self.post({**VALID, field: value})[0], 400)

    def test_missing_or_empty_message(self):
        self.assertEqual(self.post({"to": VALID["to"], "from": VALID["from"]})[0], 400)
        for value in ("", "  ", None, 123):
            self.assertEqual(self.post({**VALID, "message": value})[0], 400)

    def test_mock_delivery_success_and_unique_ids(self):
        first = self.post(VALID)[2]
        second = self.post(VALID)[2]
        self.assertEqual(second["status"], "delivered")
        self.assertNotEqual(first["message_id"], second["message_id"])

    def test_no_credentials_in_response_or_logs(self):
        # Synthetic marker, never an actual credential.
        marker = "SYNTHETIC_CREDENTIAL_CANARY"
        settings = Settings.from_env({"SMS_PROVIDER_API_CREDENTIAL": marker})
        self.assertEqual(settings.api_credential, marker)
        self.assertNotIn(marker, repr(settings))
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            success = self.post({**VALID, "message": marker})
            failure = self.post({**VALID, "api_key": marker})
            missing = self.post(VALID, "/" + marker)
        self.assertNotIn(marker, output.getvalue() + json.dumps([success, failure, missing]))


class AdapterTests(unittest.TestCase):
    def test_boundary_and_provider_error_redaction(self):
        marker = "SYNTHETIC_PROVIDER_ERROR_CANARY"

        class Adapter:
            calls = []

            def deliver(self, **kwargs):
                self.calls.append(kwargs)
                if len(self.calls) == 1:
                    return DeliveryResult("adapter-test", "delivered")
                raise RuntimeError(marker)

        adapter = Adapter()
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            server = make_server(Settings(port=0, api_credential=marker), adapter)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                for expected in (200, 502):
                    client = http.client.HTTPConnection(*server.server_address, timeout=3)
                    client.request("POST", "/sms/deliver", json.dumps(VALID), {"Content-Type": "application/json"})
                    response = client.getresponse()
                    self.assertEqual(response.status, expected)
                    self.assertNotIn(marker, response.read().decode())
                    client.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
        self.assertNotIn(marker, output.getvalue())
        self.assertEqual(adapter.calls[0], {"to": VALID["to"], "from_": VALID["from"], "message": VALID["message"]})

    def test_real_provider_not_enabled(self):
        with self.assertRaises(ValueError):
            build_provider(Settings(provider="twilio"))

    def test_env_is_ignored_but_example_is_not(self):
        ignore = Path(__file__).resolve().parents[1] / ".gitignore"
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "--quiet", tmp], check=True)
            Path(tmp, ".gitignore").write_bytes(ignore.read_bytes())
            for name in (".env", ".env.local", ".env.production"):
                result = subprocess.run(["git", "-C", tmp, "check-ignore", "--quiet", name])
                self.assertEqual(result.returncode, 0)
            result = subprocess.run(["git", "-C", tmp, "check-ignore", "--quiet", ".env.example"])
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
