"""Credential-free executable checks for the documented API contract.

These checks validate the specification now. If SPEC_BASE_URL is set, a later
implementation can also be exercised without AWS credentials. They deliberately
do not create data, follow redirects, or print response bodies/tokens.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "docs" / "api" / "openapi.yaml"
THREATS = ROOT / "docs" / "threat-model.md"


class ContractDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = SPEC.read_text(encoding="utf-8")

    def test_openapi_shape_and_required_paths(self) -> None:
        self.assertIn("openapi: 3.1.0", self.spec)
        for path in (
            "/healthz:",
            "/readyz:",
            "/v1/links:",
            "/v1/links/{code}:",
            "/r/{code}:",
        ):
            self.assertIn(path, self.spec)
        for status in (
            "'200'",
            "'201'",
            "'204'",
            "'302'",
            "'400'",
            "'401'",
            "'403'",
            "'404'",
            "'409'",
            "'410'",
            "'422'",
            "'429'",
            "'503'",
        ):
            self.assertIn(f"        {status}:", self.spec)

    def test_security_and_redirect_invariants(self) -> None:
        self.assertIn("bearerAuth:", self.spec)
        self.assertIn("security: []", self.spec)
        self.assertIn("302 response with a Location header", self.spec)
        self.assertIn("does not follow the destination", self.spec)
        self.assertIn("never reused", self.spec)
        self.assertIn("pattern: '^[A-Za-z0-9_-]{6,32}$'", self.spec)

    def test_required_schema_and_error_fields(self) -> None:
        for marker in (
            "CreateLinkRequest:",
            "UpdateLinkRequest:",
            "Link:",
            "HealthResponse:",
            "ReadinessResponse:",
            "ErrorResponse:",
            "requestId:",
            "expiresAt:",
            "enabled:",
            "status:",
        ):
            self.assertIn(marker, self.spec)

    def test_threat_model_is_mapped(self) -> None:
        threat_doc = THREATS.read_text(encoding="utf-8")
        lowered = threat_doc.lower()
        for marker in ("ssrf", "open redirect", "rate", "oidc", "tombstone", "residual-risk"):
            self.assertIn(marker, lowered)


class OptionalLocalContractSmokeTests(unittest.TestCase):
    """Run only when a local implementation URL is explicitly provided."""

    @unittest.skipUnless(
        os.getenv("SPEC_BASE_URL"), "set SPEC_BASE_URL to exercise a local service"
    )
    def test_health_and_readiness(self) -> None:
        base = os.environ["SPEC_BASE_URL"].rstrip("/")
        for route in ("/healthz", "/readyz"):
            request = Request(f"{base}{route}", headers={"Accept": "application/json"})
            with urlopen(request, timeout=3) as response:
                self.assertEqual(response.status, 200)

    @unittest.skipUnless(
        os.getenv("SPEC_BASE_URL"), "set SPEC_BASE_URL to exercise a local service"
    )
    def test_unknown_code_does_not_redirect(self) -> None:
        base = os.environ["SPEC_BASE_URL"].rstrip("/")
        request = Request(f"{base}/r/spec-unknown", headers={"Accept": "application/json"})
        try:
            with urlopen(request, timeout=3) as response:
                self.assertIn(response.status, (404, 410))
                self.assertNotIn("Location", response.headers)
        except HTTPError as error:
            self.assertIn(error.code, (404, 410))
            self.assertNotIn("Location", error.headers)
        except URLError as error:
            self.fail(f"local service could not be reached: {error.reason}")


if __name__ == "__main__":
    unittest.main()
