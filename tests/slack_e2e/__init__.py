"""
Slack E2E Synthetic Tests

Tests for Slack gateway using synthetic (non-real-Slack) HTTP requests.
Part of Phase 44: Slack Dev/Stage Synthetic E2E Tests.

These tests validate:
- Gateway HTTP endpoints respond correctly
- Event parsing logic works
- Error handling is appropriate

These tests DO NOT:
- Require real Slack credentials
- Send messages to actual Slack
- Verify Agent Engine responses
"""
