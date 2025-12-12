"""
Slack Webhook - FastAPI Proxy to Agent Engine

Enforces R3: Cloud Run as gateway only (proxy to Agent Engine via REST).

This service:
1. Receives Slack events (mentions, DMs)
2. Proxies to Agent Engine via REST API
3. Does NOT import Runner (R3 compliance)
4. Returns responses to Slack

Environment Variables:
- SLACK_BOT_TOKEN: Slack bot OAuth token (xoxb-...)
- SLACK_SIGNING_SECRET: Slack app signing secret
- AGENT_ENGINE_URL: Full URL to Agent Engine REST endpoint
- PROJECT_ID: GCP project ID
- LOCATION: GCP region
- AGENT_ENGINE_ID: Agent Engine instance ID
- PORT: Service port (default 8080)
- SLACK_SWE_PIPELINE_MODE: Routing mode (local|engine) - Phase AE2
- A2A_GATEWAY_URL: A2A gateway URL (for engine mode) - Phase AE2
"""

import os
import logging
import hashlib
import hmac
import time
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment configuration
SLACK_BOB_ENABLED = os.getenv("SLACK_BOB_ENABLED", "false").lower() == "true"
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")
PORT = int(os.getenv("PORT", "8080"))

# A2A Gateway URL (SLACK-ENDTOEND-DEV: S2)
# Preferred routing: Slack → a2a_gateway → Agent Engine
A2A_GATEWAY_URL = os.getenv("A2A_GATEWAY_URL")

# Resilience configuration (Phase 45)
AGENT_ENGINE_TIMEOUT_SECONDS = int(os.getenv("AGENT_ENGINE_TIMEOUT_SECONDS", "60"))
AGENT_ENGINE_RETRY_ENABLED = os.getenv("AGENT_ENGINE_RETRY_ENABLED", "true").lower() == "true"
AGENT_ENGINE_MAX_RETRIES = int(os.getenv("AGENT_ENGINE_MAX_RETRIES", "1"))

# Agent Engine REST API endpoint (fallback/legacy)
AGENT_ENGINE_URL = None
if LOCATION and PROJECT_ID and AGENT_ENGINE_ID:
    AGENT_ENGINE_URL = os.getenv(
        "AGENT_ENGINE_URL",
        f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}:query",
    )

# Validate required environment variables
def validate_config() -> tuple[bool, list[str]]:
    """
    Validate Slack bot configuration.

    Returns:
        (is_valid, missing_vars): Tuple of validation status and list of missing variables
    """
    if not SLACK_BOB_ENABLED:
        logger.info("Slack bot is DISABLED (SLACK_BOB_ENABLED=false)")
        return True, []  # Valid config when disabled

    missing = []

    # Required for Slack signature verification and API calls
    if not SLACK_BOT_TOKEN:
        missing.append("SLACK_BOT_TOKEN")
    if not SLACK_SIGNING_SECRET:
        missing.append("SLACK_SIGNING_SECRET")

    # Required for routing to Agent Engine
    # Option A: Via a2a_gateway (preferred)
    # Option B: Direct to Agent Engine (legacy)
    has_gateway = bool(A2A_GATEWAY_URL)
    has_direct = all([PROJECT_ID, LOCATION, AGENT_ENGINE_ID])

    if not has_gateway and not has_direct:
        missing.append("A2A_GATEWAY_URL or (PROJECT_ID + LOCATION + AGENT_ENGINE_ID)")

    if missing:
        logger.error(
            f"Slack bot ENABLED but missing required variables: {', '.join(missing)}"
        )
        return False, missing

    logger.info(
        f"Slack bot ENABLED and configured "
        f"(routing: {'a2a_gateway' if has_gateway else 'direct Agent Engine'})"
    )
    return True, []

config_valid, missing_vars = validate_config()

# Create FastAPI app
app = FastAPI(
    title="Bob's Brain Slack Webhook",
    description="Slack event handler proxying to Vertex AI Agent Engine",
    version="0.7.0",  # SLACK-ENDTOEND-DEV
)

# Slack API client (only if bot is enabled and configured)
slack_client = None
if SLACK_BOB_ENABLED and SLACK_BOT_TOKEN:
    slack_client = httpx.AsyncClient(
        base_url="https://slack.com/api",
        headers={
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json",
        },
    )


def verify_slack_signature(body: bytes, timestamp: str, signature: str) -> bool:
    """
    Verify Slack request signature.

    Args:
        body: Raw request body
        timestamp: X-Slack-Request-Timestamp header
        signature: X-Slack-Signature header

    Returns:
        bool: True if signature is valid
    """
    # Prevent replay attacks (timestamp > 5 min old)
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    # Compute expected signature
    sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    expected_signature = (
        "v0="
        + hmac.new(
            SLACK_SIGNING_SECRET.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
    )

    # Compare signatures (constant-time)
    return hmac.compare_digest(expected_signature, signature)


@app.post("/slack/events")
async def slack_events(
    request: Request,
    x_slack_request_timestamp: str = Header(None),
    x_slack_signature: str = Header(None),
) -> Dict[str, Any]:
    """
    Handle Slack events.

    Receives events from Slack (mentions, DMs) and proxies to Agent Engine.

    R3 Compliance: Does NOT run agent locally - proxies via REST.

    Events handled:
    - app_mention: @Bob mentions
    - message.im: Direct messages
    - message.channels: Channel messages

    Returns:
        dict: Slack-formatted response
    """
    # Generate correlation ID for request tracing (Phase 45)
    correlation_id = str(uuid.uuid4())

    try:
        # Read raw body for signature verification
        body = await request.body()

        # Verify Slack signature (production security)
        if x_slack_request_timestamp and x_slack_signature:
            if not verify_slack_signature(
                body, x_slack_request_timestamp, x_slack_signature
            ):
                logger.warning("Invalid Slack signature", extra={"correlation_id": correlation_id})
                raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse JSON
        data = await request.json()

        # Slack URL verification challenge
        if data.get("type") == "url_verification":
            logger.info("Slack URL verification challenge received", extra={"correlation_id": correlation_id})
            return {"challenge": data.get("challenge")}

        # Handle event callback
        if data.get("type") == "event_callback":
            event = data.get("event", {})
            event_type = event.get("type")

            # Ignore bot messages (prevent loops)
            if event.get("bot_id"):
                logger.info("Ignoring bot message", extra={"correlation_id": correlation_id})
                return {"ok": True}

            # Ignore retry attempts (Slack retries if no 200 within 3s)
            if request.headers.get("x-slack-retry-num"):
                logger.info("Ignoring Slack retry", extra={"correlation_id": correlation_id})
                return {"ok": True}

            # Extract message text
            text = event.get("text", "")
            user_id = event.get("user")
            channel_id = event.get("channel")
            thread_ts = event.get("thread_ts") or event.get("ts")

            logger.info(
                f"Slack event: {event_type}",
                extra={
                    "correlation_id": correlation_id,
                    "user": user_id,
                    "channel": channel_id,
                    "text_length": len(text),
                },
            )

            # Remove bot mention from text
            text = text.replace("<@U07NRCYJX8A>", "").strip()  # Bob's user ID

            if not text:
                logger.info("Empty message after mention removal", extra={"correlation_id": correlation_id})
                return {"ok": True}

            # Query Agent Engine via REST (R3: no local Runner)
            agent_response = await query_agent_engine(
                query=text, session_id=f"{user_id}_{channel_id}", correlation_id=correlation_id
            )

            # Post response to Slack
            await post_slack_message(
                channel=channel_id, text=agent_response, thread_ts=thread_ts, correlation_id=correlation_id
            )

            return {"ok": True}

        logger.warning(f"Unhandled Slack event type: {data.get('type')}", extra={"correlation_id": correlation_id})
        return {"ok": True}

    except Exception as e:
        logger.error(f"Slack event processing failed: {e}", extra={"correlation_id": correlation_id}, exc_info=True)
        # Return 200 to Slack to prevent retries
        return {"ok": True}


async def query_agent_engine(query: str, session_id: str, correlation_id: str = "") -> str:
    """
    Query Agent Engine via REST API with retry support (Phase 45).

    R3 Compliance: Proxies to Agent Engine, does not run locally.

    SLACK-ENDTOEND-DEV S2: Implements routing via A2A gateway (Option B).
    - Option B (preferred): Route through a2a_gateway for consistency
    - Option A (fallback): Direct Agent Engine proxy

    Phase 45 Enhancements:
    - Configurable timeout via AGENT_ENGINE_TIMEOUT_SECONDS
    - Retry logic for 5xx errors (bounded, safe for idempotent queries)
    - Correlation ID propagation for debugging

    Args:
        query: User query text
        session_id: Session identifier for memory
        correlation_id: Request correlation ID for tracing

    Returns:
        str: Agent response text
    """
    timeout = float(AGENT_ENGINE_TIMEOUT_SECONDS)
    max_retries = AGENT_ENGINE_MAX_RETRIES if AGENT_ENGINE_RETRY_ENABLED else 0
    attempt = 0
    last_error: Optional[Exception] = None

    while attempt <= max_retries:
        attempt += 1
        try:
            # ===========================================================================
            # SLACK-ENDTOEND-DEV S2: OPTION B ROUTING (IMPLEMENTED)
            # ===========================================================================
            if A2A_GATEWAY_URL:
                # Option B: Route through a2a_gateway for consistency with other frontends
                logger.info(
                    "Routing to a2a_gateway (Option B - via a2a protocol)",
                    extra={
                        "correlation_id": correlation_id,
                        "query_length": len(query),
                        "session_id": session_id,
                        "a2a_gateway_url": A2A_GATEWAY_URL,
                        "attempt": attempt,
                        "max_retries": max_retries,
                        "timeout_seconds": timeout,
                    },
                )

                # Build A2A call payload following A2AAgentCall schema
                a2a_payload = {
                    "agent_role": "bob",  # Target Bob orchestrator
                    "prompt": query,
                    "session_id": session_id,
                    "caller_spiffe_id": "spiffe://intent.solutions/slack/webhook",
                    "env": os.getenv("DEPLOYMENT_ENV", "dev"),
                }

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        f"{A2A_GATEWAY_URL}/a2a/run",
                        json=a2a_payload,
                        headers={"Content-Type": "application/json"},
                    )
                    response.raise_for_status()
                    result = response.json()

                # Extract response from A2AAgentResult
                response_text = result.get("response", "No response from A2A gateway")

                # Check for errors in A2A result
                if result.get("error"):
                    logger.error(
                        "A2A gateway returned error",
                        extra={
                            "correlation_id": correlation_id,
                            "error": result.get("error"),
                            "session_id": session_id,
                            "attempt": attempt,
                        },
                    )
                    return "Sorry, I encountered an error processing your request."

                logger.info(
                    "A2A gateway response received",
                    extra={
                        "correlation_id": correlation_id,
                        "response_length": len(response_text),
                        "session_id": result.get("session_id"),
                        "attempt": attempt,
                    },
                )

                return response_text

            else:
                # Option A (fallback): Direct Agent Engine proxy
                logger.info(
                    "Routing directly to Agent Engine (Option A - fallback)",
                    extra={
                        "correlation_id": correlation_id,
                        "query_length": len(query),
                        "session_id": session_id,
                        "agent_engine_url": AGENT_ENGINE_URL,
                        "attempt": attempt,
                        "max_retries": max_retries,
                        "timeout_seconds": timeout,
                    },
                )

                payload = {"query": query, "session_id": session_id}

                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        AGENT_ENGINE_URL,
                        json=payload,
                        headers={"Content-Type": "application/json"},
                    )

                    response.raise_for_status()
                    result = response.json()

                # Extract response text (adjust based on Agent Engine response format)
                response_text = result.get("response", "I couldn't generate a response.")

                logger.info(
                    "Agent Engine response received",
                    extra={
                        "correlation_id": correlation_id,
                        "response_length": len(response_text),
                        "session_id": session_id,
                        "attempt": attempt,
                    },
                )

                return response_text

        except httpx.HTTPStatusError as e:
            last_error = e
            status_code = e.response.status_code

            # Only retry on 5xx server errors (safe for idempotent queries)
            if 500 <= status_code < 600 and attempt <= max_retries:
                logger.warning(
                    f"HTTP {status_code} error, retrying ({attempt}/{max_retries + 1})",
                    extra={
                        "correlation_id": correlation_id,
                        "status_code": status_code,
                        "attempt": attempt,
                        "will_retry": attempt <= max_retries,
                    },
                )
                continue

            # Non-retryable error or exhausted retries
            logger.error(
                f"HTTP error during agent call: {status_code}",
                extra={
                    "correlation_id": correlation_id,
                    "detail": e.response.text[:500] if e.response.text else None,
                    "error_type": "http_status",
                    "attempt": attempt,
                },
                exc_info=True,
            )
            return "Sorry, I encountered an error processing your request."

        except httpx.TimeoutException as e:
            last_error = e
            logger.error(
                f"Request timed out after {timeout}s",
                extra={
                    "correlation_id": correlation_id,
                    "timeout_seconds": timeout,
                    "error_type": "timeout",
                    "attempt": attempt,
                },
                exc_info=True,
            )
            return "Sorry, my request timed out. Please try again."

        except httpx.RequestError as e:
            last_error = e
            logger.error(
                f"Failed to connect to backend: {e}",
                extra={
                    "correlation_id": correlation_id,
                    "error_type": "connection",
                    "attempt": attempt,
                },
                exc_info=True,
            )
            return "Sorry, I'm having trouble connecting to my backend."

        except Exception as e:
            last_error = e
            logger.error(
                f"Query processing failed: {e}",
                extra={
                    "correlation_id": correlation_id,
                    "error_type": "unknown",
                    "attempt": attempt,
                },
                exc_info=True,
            )
            return "Sorry, something went wrong."

    # Should not reach here, but handle exhausted retries
    logger.error(
        "All retry attempts exhausted",
        extra={
            "correlation_id": correlation_id,
            "total_attempts": attempt,
            "last_error": str(last_error) if last_error else None,
        },
    )
    return "Sorry, I encountered an error after multiple attempts."


async def post_slack_message(
    channel: str, text: str, thread_ts: Optional[str] = None, correlation_id: str = ""
) -> None:
    """
    Post message to Slack channel.

    Args:
        channel: Slack channel ID
        text: Message text
        thread_ts: Thread timestamp (for replies)
        correlation_id: Request correlation ID for tracing
    """
    try:
        payload = {"channel": channel, "text": text}

        if thread_ts:
            payload["thread_ts"] = thread_ts

        response = await slack_client.post("/chat.postMessage", json=payload)
        response.raise_for_status()

        logger.info(
            "Message posted to Slack",
            extra={"correlation_id": correlation_id, "channel": channel, "thread_ts": thread_ts},
        )

    except Exception as e:
        logger.error(
            f"Failed to post Slack message: {e}",
            extra={"correlation_id": correlation_id, "channel": channel},
            exc_info=True,
        )


@app.get("/health")
async def health() -> Dict[str, Any]:
    """
    Health check endpoint with configuration status.

    Returns:
        dict: Service health status and configuration
    """
    # Determine routing method
    routing = "disabled"
    if SLACK_BOB_ENABLED:
        if A2A_GATEWAY_URL:
            routing = "a2a_gateway"
        elif AGENT_ENGINE_URL:
            routing = "direct_agent_engine"
        else:
            routing = "misconfigured"

    return {
        "status": "healthy" if (not SLACK_BOB_ENABLED or config_valid) else "degraded",
        "service": "slack-webhook",
        "version": "0.8.0",  # Phase 45: Resilience & Error-Handling
        "slack_bot_enabled": SLACK_BOB_ENABLED,
        "config_valid": config_valid,
        "missing_vars": missing_vars if not config_valid else [],
        "routing": routing,
        "a2a_gateway_url": A2A_GATEWAY_URL if A2A_GATEWAY_URL else None,
        "agent_engine_url": AGENT_ENGINE_URL if AGENT_ENGINE_URL and not A2A_GATEWAY_URL else None,
        # Phase 45: Resilience configuration
        "resilience": {
            "timeout_seconds": AGENT_ENGINE_TIMEOUT_SECONDS,
            "retry_enabled": AGENT_ENGINE_RETRY_ENABLED,
            "max_retries": AGENT_ENGINE_MAX_RETRIES,
        },
    }


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint - service info.

    Returns:
        dict: Service metadata
    """
    return {
        "name": "Bob's Brain Slack Webhook",
        "version": "0.8.0",
        "description": "Slack event handler proxying to Vertex AI Agent Engine",
        "endpoints": {"events": "/slack/events", "health": "/health"},
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(
        f"Starting Slack Webhook on port {PORT}",
        extra={
            "project_id": PROJECT_ID,
            "location": LOCATION,
            "agent_engine_id": AGENT_ENGINE_ID,
        },
    )

    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
