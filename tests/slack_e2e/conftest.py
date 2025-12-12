"""
Pytest fixtures for Slack E2E synthetic tests.

Part of Phase 44: Slack Dev/Stage Synthetic E2E Tests.
"""

import os
import pytest


@pytest.fixture
def slack_gateway_url():
    """
    Get Slack gateway URL from environment.

    Falls back to localhost for local testing.
    """
    return os.getenv("SLACK_GATEWAY_URL_DEV", "http://localhost:8080")


@pytest.fixture
def synthetic_app_mention_event():
    """
    Generate a synthetic Slack app_mention event.

    This simulates what Slack sends when a user mentions the bot.
    """
    return {
        "type": "event_callback",
        "token": "synthetic-token",
        "team_id": "T12345678",
        "api_app_id": "A12345678",
        "event": {
            "type": "app_mention",
            "user": "U12345678",
            "text": "<@U07NRCYJX8A> Hello Bob, this is a synthetic test",
            "ts": "1234567890.123456",
            "channel": "C12345678",
            "event_ts": "1234567890.123456",
        },
        "event_id": "Ev12345678",
        "event_time": 1234567890,
    }


@pytest.fixture
def synthetic_message_event():
    """
    Generate a synthetic Slack message event (DM).
    """
    return {
        "type": "event_callback",
        "token": "synthetic-token",
        "team_id": "T12345678",
        "api_app_id": "A12345678",
        "event": {
            "type": "message",
            "channel_type": "im",
            "user": "U12345678",
            "text": "Hello Bob",
            "ts": "1234567890.123456",
            "channel": "D12345678",
            "event_ts": "1234567890.123456",
        },
        "event_id": "Ev12345679",
        "event_time": 1234567890,
    }


@pytest.fixture
def url_verification_payload():
    """
    Generate a Slack URL verification challenge payload.
    """
    return {
        "type": "url_verification",
        "token": "synthetic-token",
        "challenge": "test-challenge-string-12345",
    }


@pytest.fixture
def bot_message_event():
    """
    Generate a synthetic bot message event (should be ignored).
    """
    return {
        "type": "event_callback",
        "token": "synthetic-token",
        "team_id": "T12345678",
        "api_app_id": "A12345678",
        "event": {
            "type": "message",
            "bot_id": "B12345678",  # Bot message indicator
            "text": "I am a bot message",
            "ts": "1234567890.123456",
            "channel": "C12345678",
            "event_ts": "1234567890.123456",
        },
        "event_id": "Ev12345680",
        "event_time": 1234567890,
    }
