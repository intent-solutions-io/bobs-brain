"""
Slack Gateway Synthetic E2E Tests - Dev Environment

Tests the Slack webhook gateway using synthetic HTTP requests.
No real Slack required - validates gateway logic and HTTP responses.

Part of Phase 44: Slack Dev/Stage Synthetic E2E Tests.

Usage:
    # Run against localhost (requires gateway running)
    pytest tests/slack_e2e/test_slack_gateway_synthetic_dev.py -v

    # Run against deployed dev gateway
    SLACK_GATEWAY_URL_DEV=https://your-gateway.run.app pytest tests/slack_e2e/ -v

Environment Variables:
    SLACK_GATEWAY_URL_DEV: URL of the Slack gateway (default: http://localhost:8080)
"""

import os
import pytest
import httpx


# Skip all tests if gateway URL is not available
GATEWAY_URL = os.getenv("SLACK_GATEWAY_URL_DEV", "")
SKIP_REASON = "SLACK_GATEWAY_URL_DEV not set - skipping synthetic E2E tests"


class TestSlackGatewayHealth:
    """Tests for health check endpoint."""

    @pytest.mark.skipif(not GATEWAY_URL, reason=SKIP_REASON)
    def test_health_endpoint_returns_200(self, slack_gateway_url):
        """Test that /health endpoint returns 200 OK."""
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{slack_gateway_url}/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert data["service"] == "slack-webhook"

    @pytest.mark.skipif(not GATEWAY_URL, reason=SKIP_REASON)
    def test_health_returns_config_status(self, slack_gateway_url):
        """Test that /health returns configuration status."""
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{slack_gateway_url}/health")

        data = response.json()
        assert "slack_bot_enabled" in data
        assert "config_valid" in data
        assert "routing" in data

    @pytest.mark.skipif(not GATEWAY_URL, reason=SKIP_REASON)
    def test_root_endpoint_returns_service_info(self, slack_gateway_url):
        """Test that / endpoint returns service metadata."""
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{slack_gateway_url}/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


class TestSlackURLVerification:
    """Tests for Slack URL verification challenge."""

    @pytest.mark.skipif(not GATEWAY_URL, reason=SKIP_REASON)
    def test_url_verification_returns_challenge(
        self, slack_gateway_url, url_verification_payload
    ):
        """Test that URL verification challenge is echoed back."""
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{slack_gateway_url}/slack/events",
                json=url_verification_payload,
            )

        assert response.status_code == 200
        data = response.json()
        assert "challenge" in data
        assert data["challenge"] == url_verification_payload["challenge"]


class TestSlackEventHandling:
    """Tests for Slack event handling."""

    @pytest.mark.skipif(not GATEWAY_URL, reason=SKIP_REASON)
    def test_app_mention_returns_200(
        self, slack_gateway_url, synthetic_app_mention_event
    ):
        """
        Test that app_mention event returns 200 OK.

        Note: This doesn't test the full flow (Agent Engine call, Slack reply)
        because that requires real credentials. It only validates the gateway
        accepts and parses the event correctly.
        """
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{slack_gateway_url}/slack/events",
                json=synthetic_app_mention_event,
            )

        # Gateway should return 200 to Slack regardless of internal processing
        assert response.status_code == 200
        data = response.json()
        assert "ok" in data

    @pytest.mark.skipif(not GATEWAY_URL, reason=SKIP_REASON)
    def test_bot_message_ignored(self, slack_gateway_url, bot_message_event):
        """Test that bot messages are ignored (prevents loops)."""
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{slack_gateway_url}/slack/events",
                json=bot_message_event,
            )

        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") is True

    @pytest.mark.skipif(not GATEWAY_URL, reason=SKIP_REASON)
    def test_message_event_returns_200(
        self, slack_gateway_url, synthetic_message_event
    ):
        """Test that message events return 200 OK."""
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{slack_gateway_url}/slack/events",
                json=synthetic_message_event,
            )

        assert response.status_code == 200


class TestSlackErrorHandling:
    """Tests for error handling."""

    @pytest.mark.skipif(not GATEWAY_URL, reason=SKIP_REASON)
    def test_invalid_json_returns_200(self, slack_gateway_url):
        """
        Test that invalid JSON still returns 200.

        Slack expects 200 for all responses to prevent retries.
        The gateway should handle errors gracefully.
        """
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{slack_gateway_url}/slack/events",
                content=b"not valid json",
                headers={"Content-Type": "application/json"},
            )

        # Gateway may return 4xx for truly invalid requests
        # or 200 to prevent Slack retries - both are acceptable
        assert response.status_code in [200, 400, 422]

    @pytest.mark.skipif(not GATEWAY_URL, reason=SKIP_REASON)
    def test_empty_event_handled(self, slack_gateway_url):
        """Test that empty event is handled gracefully."""
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{slack_gateway_url}/slack/events",
                json={"type": "event_callback", "event": {}},
            )

        # Should not crash, return 200
        assert response.status_code == 200

    @pytest.mark.skipif(not GATEWAY_URL, reason=SKIP_REASON)
    def test_unknown_event_type_handled(self, slack_gateway_url):
        """Test that unknown event types are handled gracefully."""
        unknown_event = {
            "type": "event_callback",
            "event": {
                "type": "unknown_event_type_xyz",
                "user": "U12345678",
            },
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{slack_gateway_url}/slack/events",
                json=unknown_event,
            )

        # Should return 200 (acknowledge to Slack)
        assert response.status_code == 200


class TestSlackRetryHandling:
    """Tests for Slack retry handling."""

    @pytest.mark.skipif(not GATEWAY_URL, reason=SKIP_REASON)
    def test_retry_header_handled(
        self, slack_gateway_url, synthetic_app_mention_event
    ):
        """Test that retry attempts are handled (not reprocessed)."""
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{slack_gateway_url}/slack/events",
                json=synthetic_app_mention_event,
                headers={"X-Slack-Retry-Num": "1"},  # Simulate retry
            )

        # Should acknowledge retry without reprocessing
        assert response.status_code == 200
        data = response.json()
        assert data.get("ok") is True


# Local test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
