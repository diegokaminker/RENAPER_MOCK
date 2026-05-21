from __future__ import annotations

import os
from typing import Any, Dict, Iterator, Optional

import httpx
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MOCK_USER", "mock_user")
os.environ.setdefault("MOCK_PASS", "mock_pass")

DEFAULT_CLOUD_RUN_URL = (
    "https://renaper-mock-569660039899.us-central1.run.app"
)


class _HttpGetClient:
    """Minimal client interface shared by TestClient and httpx."""

    def get(self, path: str, params: Optional[Dict[str, str]] = None) -> Any:
        raise NotImplementedError


class _RemoteClient(_HttpGetClient):
    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def get(self, path: str, params: Optional[Dict[str, str]] = None) -> httpx.Response:
        return self._http.get(path, params=params)


@pytest.fixture
def client(request: pytest.FixtureRequest) -> Iterator[_HttpGetClient]:
    base_url = os.environ.get("RENAPER_BASE_URL", "").strip()
    if not base_url and request.config.getoption("--cloud", default=False):
        base_url = DEFAULT_CLOUD_RUN_URL

    if base_url:
        with httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=30.0,
        ) as http:
            yield _RemoteClient(http)
    else:
        from app.main import app  # noqa: WPS433

        yield TestClient(app)


@pytest.fixture
def auth_params() -> Dict[str, str]:
    return {
        "usuario": os.environ["MOCK_USER"],
        "clave": os.environ["MOCK_PASS"],
    }


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--cloud",
        action="store_true",
        default=False,
        help="Run search tests against Cloud Run (default URL or RENAPER_BASE_URL)",
    )
