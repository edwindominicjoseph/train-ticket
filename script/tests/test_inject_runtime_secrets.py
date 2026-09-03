import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "inject-runtime-secrets.py"
SPEC = importlib.util.spec_from_file_location("inject_runtime_secrets", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


TARGET = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: ts-travel-service
spec:
  template:
    spec:
      containers:
        - name: ts-travel-service
          envFrom:
            - configMapRef:
                name: nacos
"""


class InjectRuntimeSecretsTest(unittest.TestCase):
    def setUp(self):
        self.services = {"ts-travel-service"}

    def test_injects_jwt_secret_into_target_deployment(self):
        rendered = MODULE.inject(TARGET, self.services)

        self.assertIn("name: ts-jwt", rendered)
        self.assertLess(rendered.index("name: ts-jwt"), rendered.index("name: nacos"))

    def test_injection_is_idempotent(self):
        once = MODULE.inject(TARGET, self.services)

        self.assertEqual(once, MODULE.inject(once, self.services))
        self.assertEqual(1, once.count("name: ts-jwt"))

    def test_leaves_non_target_deployment_unchanged(self):
        self.assertEqual(TARGET, MODULE.inject(TARGET, {"ts-order-service"}))

    def test_rejects_target_without_env_from(self):
        document = TARGET.replace("          envFrom:\n", "")

        with self.assertRaisesRegex(ValueError, "has no envFrom section"):
            MODULE.inject(document, self.services)

    def test_render_accepts_crlf_document_separators(self):
        second = TARGET.replace("ts-travel-service", "ts-order-service")
        content = TARGET.replace("\n", "\r\n") + "---\r\n" + second.replace("\n", "\r\n")

        rendered = MODULE.render(content, self.services)

        self.assertEqual(1, rendered.count("name: ts-jwt"))
        self.assertIn("\n---\n", rendered)


if __name__ == "__main__":
    unittest.main()
