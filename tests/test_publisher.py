"""Offline tests execute the workflow's Python without contacting GitHub or TRMNL."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import textwrap
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github/workflows/push-agent-says.yml").read_text()
CODE = textwrap.dedent(WORKFLOW.split("        run: |\n", 1)[1])
NAMESPACE = {"__name__": "offline_test"}
exec(compile(CODE, "publisher_workflow", "exec"), NAMESPACE)


class PublisherTests(unittest.TestCase):
    def compose(self, data):
        return json.loads(NAMESPACE["compose"]({"client_payload": data}))["merge_variables"]

    def test_approved_hello(self):
        result = self.compose({"message": "Hello Andrea — Rusty is connected."})
        self.assertEqual(result["agent_name"], "Rusty")
        self.assertEqual(result["message"], "Hello Andrea — Rusty is connected.")
        for i in range(1, 6):
            self.assertEqual(result[f"priority_{i}"], "")

    def test_all_five_priorities(self):
        result = self.compose({"message": "Hello", "priorities": [str(i) for i in range(5)]})
        self.assertEqual(result["priority_5"], "4")

    def test_invalid_payloads(self):
        cases = [None, [], {}, {"message": ""}, {"message": " "}, {"message": 42},
                 {"message": "x" * 801}, {"message": "line\nbreak"},
                 {"message": "control\x7f"}, {"message": "ok", "priorities": "wrong"},
                 {"message": "ok", "priorities": ["x"] * 6},
                 {"message": "ok", "priorities": ["x" * 101]},
                 {"message": "ok", "priorities": [None]},
                 {"message": "ok", "priorities": [""]},
                 {"message": "ok", "webhook": "https://example.com"},
                 {"message": "ok", "agent_name": "Luna"}, {"message": "🦀" * 800}]
        for data in cases:
            with self.subTest(data_type=type(data).__name__):
                with self.assertRaises(ValueError):
                    self.compose(data)

    def test_shell_and_workflow_text_remain_data(self):
        text = '$(touch /tmp/never-execute) `id` ${{ secrets.ANYTHING }} "quotes" <b>hello</b>'
        self.assertEqual(self.compose({"message": text})["message"], text)
        self.assertNotIn("github.event.client_payload", WORKFLOW)
        self.assertNotIn("GITHUB_OUTPUT", WORKFLOW)

    def test_template_escapes_every_display_field(self):
        import re
        template = (ROOT / "agent-says/template.liquid").read_text()
        fields = re.findall(r"{{\s*(.*?)\s*}}", template)
        self.assertEqual(len(fields), 6)
        self.assertTrue(all("| escape" in field for field in fields if field != "i"))

    def run_main(self, endpoint, status=200, message="approved hello"):
        with tempfile.TemporaryDirectory() as directory:
            event = Path(directory) / "event.json"
            event.write_text(json.dumps({"client_payload": {"message": message}}))
            with patch.dict(os.environ, {"GITHUB_EVENT_PATH": str(event),
                                         "TRMNL_WEBHOOK_URL": endpoint}):
                with patch("http.client.HTTPSConnection") as connection:
                    connection.return_value.getresponse.return_value.status = status
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                        try:
                            NAMESPACE["main"]()
                        except ValueError:
                            pass
                    return connection, output.getvalue()

    def test_endpoint_validation_before_network(self):
        for endpoint in ["", "http://trmnl.com/api/custom_plugins/" + "a" * 36,
                         "https://example.com/", "https://trmnl.com@evil.test/",
                         "https://trmnl.com/api/custom_plugins/not-a-uuid"]:
            connection, _ = self.run_main(endpoint)
            connection.assert_not_called()
        connection, _ = self.run_main("https://trmnl.com/", message="")
        connection.assert_not_called()

    def test_delivery_status_no_redirect_retry_or_secret_logging(self):
        endpoint = "https://trmnl.com/api/custom_plugins/00000000-0000-0000-0000-000000000000"
        for status in [200, 201, 302, 404, 429, 500]:
            connection, output = self.run_main(endpoint, status)
            connection.return_value.request.assert_called_once()
            connection.return_value.close.assert_called_once()
            self.assertEqual("accepted" in output, 200 <= status < 300)
            self.assertIn(str(status), output)
            self.assertNotIn(endpoint, output)
            self.assertNotIn("approved hello", output)


if __name__ == "__main__":
    unittest.main()
