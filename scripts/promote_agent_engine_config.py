#!/usr/bin/env python3
"""
Agent Engine Promotion Config Helper

Shows the current Agent Engine environment mapping and validates
configuration readiness for promotion. Does NOT make any API calls
or deploy anything - config validation only.

Usage:
    # Show all agent mappings
    python scripts/promote_agent_engine_config.py --agent all

    # Show specific agent promotion path
    python scripts/promote_agent_engine_config.py --from-env dev --to-env stage --agent bob

    # Validate promotion readiness
    python scripts/promote_agent_engine_config.py --from-env stage --to-env prod --agent all --validate

Exit Codes:
    0 - Success (config valid or shown)
    1 - Config file error
    2 - Validation failed (TODOs remain)
"""

import argparse
import sys
from pathlib import Path

import yaml

# Config file path
CONFIG_FILE = Path(__file__).parent.parent / "config" / "agent_engine_envs.yaml"


def load_config() -> dict:
    """Load agent engine environment config."""
    if not CONFIG_FILE.exists():
        print(f"ERROR: Config file not found: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def show_agent_mapping(config: dict, agent_name: str) -> None:
    """Display environment mapping for an agent."""
    agents = config.get("agents", {})

    if agent_name not in agents:
        print(f"ERROR: Agent '{agent_name}' not found in config")
        print(f"Available agents: {', '.join(agents.keys())}")
        sys.exit(1)

    agent = agents[agent_name]
    print(f"\n{'='*60}")
    print(f"Agent: {agent_name}")
    print(f"Display Name: {agent.get('display_name', 'N/A')}")
    print(f"Directory: {agent.get('agent_dir', 'N/A')}")
    print(f"{'='*60}")

    envs = agent.get("environments", {})
    for env_name in ["dev", "stage", "prod"]:
        if env_name in envs:
            env = envs[env_name]
            engine_id = env.get("engine_id", "NOT SET")
            status = env.get("status", "unknown")
            project = env.get("project_id", "N/A")

            # Mark TODOs
            is_todo = "TODO" in str(engine_id)
            status_icon = "[ ]" if is_todo else "[x]"

            print(f"\n  {env_name.upper()}")
            print(f"    {status_icon} Engine ID: {engine_id}")
            print(f"        Project: {project}")
            print(f"        Status: {status}")


def show_promotion_path(
    config: dict, from_env: str, to_env: str, agent_name: str
) -> int:
    """Show promotion path from one env to another."""
    agents = config.get("agents", {})
    todo_count = 0

    print(f"\n{'='*60}")
    print(f"PROMOTION PATH: {from_env.upper()} -> {to_env.upper()}")
    print(f"{'='*60}")

    agent_list = list(agents.keys()) if agent_name == "all" else [agent_name]

    for name in agent_list:
        if name not in agents:
            print(f"WARNING: Agent '{name}' not found, skipping")
            continue

        agent = agents[name]
        envs = agent.get("environments", {})

        from_config = envs.get(from_env, {})
        to_config = envs.get(to_env, {})

        from_id = from_config.get("engine_id", "NOT SET")
        to_id = to_config.get("engine_id", "NOT SET")

        from_todo = "TODO" in str(from_id)
        to_todo = "TODO" in str(to_id)

        if from_todo:
            todo_count += 1
        if to_todo:
            todo_count += 1

        print(f"\n  {name}:")
        print(f"    {from_env}: {from_id} {'(TODO)' if from_todo else ''}")
        print(f"    {to_env}:   {to_id} {'(TODO)' if to_todo else ''}")

    # Show promotion requirements
    promo_key = f"{from_env}_to_{to_env}"
    promo_config = config.get("promotion", {}).get(promo_key, {})

    if promo_config:
        print(f"\n  Required Checks:")
        for check in promo_config.get("required_checks", []):
            print(f"    - {check}")

        if promo_config.get("manual_approval"):
            channel = promo_config.get("approval_channel", "#general")
            print(f"\n  Manual Approval Required: Yes ({channel})")

    return todo_count


def validate_promotion(
    config: dict, from_env: str, to_env: str, agent_name: str
) -> bool:
    """Validate that promotion config is complete (no TODOs)."""
    todo_count = show_promotion_path(config, from_env, to_env, agent_name)

    print(f"\n{'='*60}")
    if todo_count == 0:
        print("VALIDATION: PASS - All engine IDs configured")
        return True
    else:
        print(f"VALIDATION: FAIL - {todo_count} TODO(s) remaining")
        print("\nTo fix:")
        print("  1. Deploy agents to environments")
        print("  2. Get engine IDs from deployment output")
        print("  3. Update config/agent_engine_envs.yaml")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Agent Engine Promotion Config Helper"
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent name (bob, foreman) or 'all'",
    )
    parser.add_argument(
        "--from-env",
        choices=["dev", "stage", "prod"],
        help="Source environment",
    )
    parser.add_argument(
        "--to-env",
        choices=["dev", "stage", "prod"],
        help="Target environment",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate promotion readiness (exit 2 if TODOs remain)",
    )

    args = parser.parse_args()

    config = load_config()

    # Show schema version
    print(f"Config Version: {config.get('schema_version', 'unknown')}")
    print(f"App Version: {config.get('app_version', 'unknown')}")

    # If from/to specified, show promotion path
    if args.from_env and args.to_env:
        if args.validate:
            valid = validate_promotion(config, args.from_env, args.to_env, args.agent)
            sys.exit(0 if valid else 2)
        else:
            show_promotion_path(config, args.from_env, args.to_env, args.agent)
    else:
        # Just show agent mapping
        if args.agent == "all":
            for agent_name in config.get("agents", {}).keys():
                show_agent_mapping(config, agent_name)
        else:
            show_agent_mapping(config, args.agent)


if __name__ == "__main__":
    main()
