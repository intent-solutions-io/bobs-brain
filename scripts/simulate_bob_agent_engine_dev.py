#!/usr/bin/env python3
"""
Dev E2E Simulation: Bob Agent Engine

Simulates a query to Bob on Vertex AI Agent Engine (dev environment).
This script:
1. Reads dev config from environment/config files
2. Constructs a test query for Bob
3. Either makes a real API call (if credentials present) or prints simulation info

Usage:
    python scripts/simulate_bob_agent_engine_dev.py

Environment:
    DEPLOYMENT_ENV: Environment (default: dev)
    PROJECT_ID: GCP project ID
    LOCATION: GCP region (default: us-central1)
    BOB_AGENT_ENGINE_ID: Bob's Agent Engine ID (optional - uses config if not set)

Exit Codes:
    0: Success (real call or simulation)
    1: Configuration error
    2: API call failed
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test query for Bob
TEST_QUERY = "You are Bob. Reply with your current version and a single sentence summary of your purpose."

# Default configuration
DEFAULT_ENV = "dev"
DEFAULT_LOCATION = "us-central1"
DEFAULT_PROJECT_ID = "bobs-brain-dev"


def load_config():
    """Load configuration from environment and config files."""
    config = {
        "env": os.getenv("DEPLOYMENT_ENV", DEFAULT_ENV),
        "project_id": os.getenv("PROJECT_ID", DEFAULT_PROJECT_ID),
        "location": os.getenv("LOCATION", DEFAULT_LOCATION),
        "agent_engine_id": os.getenv("BOB_AGENT_ENGINE_ID"),
    }

    # Try to load from agent_engine_envs.yaml if available
    config_path = os.path.join(project_root, "config", "agent_engine_envs.yaml")
    if os.path.exists(config_path):
        try:
            import yaml
            with open(config_path, "r") as f:
                yaml_config = yaml.safe_load(f)

            # Extract bob's dev engine ID
            bob_config = yaml_config.get("agents", {}).get("bob", {})
            dev_config = bob_config.get("environments", {}).get("dev", {})

            if not config["agent_engine_id"]:
                config["agent_engine_id"] = dev_config.get("engine_id")
            if not config["project_id"] or config["project_id"] == DEFAULT_PROJECT_ID:
                config["project_id"] = dev_config.get("project_id", config["project_id"])

            logger.info(f"Loaded config from {config_path}")
        except Exception as e:
            logger.warning(f"Could not load YAML config: {e}")

    return config


def check_credentials():
    """Check if GCP credentials are available."""
    try:
        from google.auth import default
        from google.auth.transport.requests import Request

        credentials, project = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])

        # Try to refresh to verify credentials are valid
        if not credentials.valid:
            credentials.refresh(Request())

        logger.info(f"GCP credentials available (project: {project})")
        return True, credentials.token
    except Exception as e:
        logger.warning(f"GCP credentials not available: {e}")
        return False, None


def build_request_payload(config: dict) -> dict:
    """Build the request payload for Agent Engine."""
    return {
        "query": TEST_QUERY,
        "session_id": f"dev-simulation-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "context": {
            "simulation": True,
            "caller": "simulate_bob_agent_engine_dev.py",
            "env": config["env"],
        }
    }


def build_request_url(config: dict) -> str:
    """Build the Agent Engine REST API URL."""
    return (
        f"https://{config['location']}-aiplatform.googleapis.com/v1/"
        f"projects/{config['project_id']}/locations/{config['location']}/"
        f"reasoningEngines/{config['agent_engine_id']}:query"
    )


def simulate_only(config: dict, payload: dict, url: str):
    """Print simulation info without making API call."""
    print("\n" + "=" * 70)
    print("DEV E2E SIMULATION - AGENT ENGINE (SIMULATION ONLY)")
    print("=" * 70)
    print("\n⚠️  NO API CALL PERFORMED - missing credentials or engine ID\n")

    print("Configuration:")
    print(f"  Environment: {config['env']}")
    print(f"  Project ID:  {config['project_id']}")
    print(f"  Location:    {config['location']}")
    print(f"  Engine ID:   {config['agent_engine_id'] or 'NOT SET'}")

    print("\nRequest URL (would be):")
    if config['agent_engine_id'] and "TODO" not in str(config['agent_engine_id']):
        print(f"  {url}")
    else:
        print("  [Cannot build URL - engine ID not configured]")

    print("\nRequest Payload (would be):")
    print(json.dumps(payload, indent=2))

    print("\nExpected Response Shape:")
    expected_response = {
        "response": "I am Bob, version X.Y.Z. I serve as the conversational AI assistant...",
        "session_id": payload["session_id"],
        "metadata": {
            "agent_role": "bob",
            "env": config["env"],
        }
    }
    print(json.dumps(expected_response, indent=2))

    print("\n" + "=" * 70)
    print("To enable real API calls:")
    print("  1. Set BOB_AGENT_ENGINE_ID environment variable")
    print("  2. Authenticate with: gcloud auth application-default login")
    print("  3. Or run on GCP with appropriate service account")
    print("=" * 70 + "\n")


def make_real_call(config: dict, payload: dict, url: str, token: str):
    """Make real API call to Agent Engine."""
    import httpx

    print("\n" + "=" * 70)
    print("DEV E2E SIMULATION - AGENT ENGINE (LIVE CALL)")
    print("=" * 70)

    print("\nConfiguration:")
    print(f"  Environment: {config['env']}")
    print(f"  Project ID:  {config['project_id']}")
    print(f"  Location:    {config['location']}")
    print(f"  Engine ID:   {config['agent_engine_id']}")

    print(f"\nCalling: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-Correlation-ID": f"dev-sim-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

        print("\n✅ SUCCESS - Agent Engine Response:")
        print(json.dumps(result, indent=2))
        print("\n" + "=" * 70 + "\n")
        return True

    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP ERROR: {e.response.status_code}")
        print(f"Response: {e.response.text[:500]}")
        print("\n" + "=" * 70 + "\n")
        return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n" + "=" * 70 + "\n")
        return False


def main():
    """Main entry point."""
    print("\n🚀 Bob Agent Engine Dev Simulation")
    print("-" * 40)

    # Load configuration
    config = load_config()

    # Check if engine ID is configured
    engine_id = config.get("agent_engine_id")
    engine_configured = engine_id and "TODO" not in str(engine_id)

    # Check credentials
    has_credentials, token = check_credentials()

    # Build request
    payload = build_request_payload(config)
    url = build_request_url(config) if engine_configured else "[URL not built - no engine ID]"

    # Decide: simulation or real call
    if engine_configured and has_credentials:
        success = make_real_call(config, payload, url, token)
        sys.exit(0 if success else 2)
    else:
        simulate_only(config, payload, url)
        sys.exit(0)


if __name__ == "__main__":
    main()
