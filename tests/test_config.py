# SPDX-License-Identifier: Apache-2.0

import httpx
import pytest

from lexmachina_agent.agent_executor import (
    APIAgentConfiguration,
    MissingConfigurationError,
    RequiredConfigurationError,
)


def test_config_missing_all(monkeypatch: pytest.MonkeyPatch) -> None:
    for k in ["API_TOKEN", "CLIENT_ID", "CLIENT_SECRET", "DELEGATION_URL"]:
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(MissingConfigurationError):
        APIAgentConfiguration()


def test_config_client_id_without_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("API_TOKEN", raising=False)
    monkeypatch.setenv("CLIENT_ID", "cid")
    monkeypatch.delenv("CLIENT_SECRET", raising=False)
    with pytest.raises(RequiredConfigurationError) as exc:
        APIAgentConfiguration()
    assert "CLIENT_SECRET" in str(exc.value)


def test_config_client_secret_without_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("API_TOKEN", raising=False)
    monkeypatch.delenv("CLIENT_ID", raising=False)
    monkeypatch.setenv("CLIENT_SECRET", "csecret")
    with pytest.raises(RequiredConfigurationError) as exc:
        APIAgentConfiguration()
    assert "CLIENT_ID" in str(exc.value)


def test_config_oauth_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("API_TOKEN", raising=False)
    monkeypatch.setenv("CLIENT_ID", "cid")
    monkeypatch.setenv("CLIENT_SECRET", "csecret")

    class FakeResp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, str]:
            return {"access_token": "fetched_token"}

    def fake_post(url: str, data: dict[str, str], headers: dict[str, str]) -> FakeResp:  # type: ignore[override]
        assert data["client_id"] == "cid"
        assert data["client_secret"] == "csecret"  # noqa: S105
        return FakeResp()

    monkeypatch.setattr(httpx, "post", fake_post)
    cfg = APIAgentConfiguration()
    agent = cfg.build_agent()
    assert "Bearer fetched_token" in agent._headers["Authorization"]
