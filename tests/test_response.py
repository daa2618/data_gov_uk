from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from data_gov_uk.utils.response import GET_RESPONSE, POST_RESPONSE, MethodError, Response

# ── Initialization ──────────────────────────────────────────────────


class TestResponseInit:
    def test_default_method_is_get(self):
        with patch("data_gov_uk.utils.response.requests.Session"):
            r = Response("https://example.com")
        assert r.method == "GET"

    def test_invalid_method_raises(self):
        with pytest.raises(MethodError):
            Response("https://example.com", method="PATCH")

    def test_default_headers_include_user_agent(self):
        with patch("data_gov_uk.utils.response.requests.Session"):
            r = Response("https://example.com")
        assert "User-Agent" in r.headers

    def test_custom_headers_merged(self):
        with patch("data_gov_uk.utils.response.requests.Session"):
            r = Response("https://example.com", headers={"X-Custom": "yes"})
        assert r.headers["X-Custom"] == "yes"
        assert "User-Agent" in r.headers

    def test_trust_env_default_false(self):
        with patch("data_gov_uk.utils.response.requests.Session") as MockSession:
            mock_session = MockSession.return_value
            Response("https://example.com")
        assert mock_session.trust_env is False

    def test_trust_env_override(self):
        with patch("data_gov_uk.utils.response.requests.Session") as MockSession:
            mock_session = MockSession.return_value
            Response("https://example.com", trust_env=True)
        assert mock_session.trust_env is True


# ── response property ───────────────────────────────────────────────


class TestResponseProperty:
    def test_calls_session_get(self):
        mock_session = MagicMock()
        r = Response("https://example.com", session=mock_session)
        _ = r.response
        mock_session.get.assert_called_once()

    def test_calls_session_post(self):
        mock_session = MagicMock()
        r = Response("https://example.com", method="POST", session=mock_session)
        _ = r.response
        mock_session.post.assert_called_once()

    def test_response_cached(self):
        mock_session = MagicMock()
        r = Response("https://example.com", session=mock_session)
        _ = r.response
        _ = r.response
        assert mock_session.get.call_count == 1


# ── assert_response ─────────────────────────────────────────────────


class TestAssertResponse:
    def test_200_returns_response(self):
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_session.get.return_value = mock_resp

        r = Response("https://example.com", session=mock_session)
        result = r.assert_response()
        assert result is mock_resp

    def test_non_200_raises(self):
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = "Not Found"
        mock_resp.raise_for_status.side_effect = Exception("404 Client Error")
        mock_session.get.return_value = mock_resp

        r = Response("https://example.com", session=mock_session)
        with pytest.raises(Exception, match="404"):
            r.assert_response()


# ── get_json_from_response ──────────────────────────────────────────


class TestGetJsonFromResponse:
    def test_success(self):
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"success": True, "result": []}
        mock_session.get.return_value = mock_resp

        r = Response("https://example.com", session=mock_session)
        assert r.get_json_from_response() == {"success": True, "result": []}

    def test_failure_returns_none(self):
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Server Error"
        mock_resp.raise_for_status.side_effect = Exception("500")
        mock_session.get.return_value = mock_resp

        r = Response("https://example.com", session=mock_session)
        assert r.get_json_from_response() is None


# ── get_base_url ────────────────────────────────────────────────────


class TestGetBaseUrl:
    def test_extracts_base(self):
        mock_session = MagicMock()
        r = Response("https://data.gov.uk/api/3/action/package_list", session=mock_session)
        assert r.get_base_url() == "https://data.gov.uk"


# ── Subclasses ──────────────────────────────────────────────────────


class TestSubclasses:
    def test_get_response_method(self):
        mock_session = MagicMock()
        r = GET_RESPONSE("https://example.com", session=mock_session)
        assert r.method == "GET"

    def test_post_response_method(self):
        mock_session = MagicMock()
        r = POST_RESPONSE("https://example.com", session=mock_session)
        assert r.method == "POST"
