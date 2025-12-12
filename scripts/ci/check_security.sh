#!/usr/bin/env bash
# Security Validation Script (Phase 46)
# Run this in CI to check for security issues

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Security Validation (Phase 46) ==="
echo "Checking repository: $REPO_ROOT"
echo ""

ERRORS=0
WARNINGS=0

# Check for service account keys in repo
echo "Checking for service account keys..."
if find "$REPO_ROOT" -type f \( -name "*.json" -o -name "*.p12" -o -name "*.pem" \) | xargs grep -l "private_key" 2>/dev/null | grep -v node_modules | grep -v .venv; then
    echo "ERROR: Found potential service account keys in repository!"
    ((ERRORS++))
else
    echo "OK: No service account keys found"
fi
echo ""

# Check for hardcoded secrets patterns
# Note: This looks for actual secrets, not documentation/comments mentioning formats
echo "Checking for hardcoded secrets..."

# Check for actual Slack tokens (full format, not just prefix in docs)
# Real tokens have a specific format: xoxb-NUMBERS-NUMBERS-ALPHANUMERIC
if grep -rn "xoxb-[0-9]\{9,\}-[0-9]\{9,\}-[a-zA-Z0-9]\{24\}" "$REPO_ROOT" --include="*.py" --include="*.tf" --include="*.yml" --include="*.yaml" --include="*.json" 2>/dev/null | grep -v ".git" | grep -v node_modules | grep -v ".venv" | grep -v "test" | head -5; then
    echo "ERROR: Found potential real Slack bot token!"
    ((ERRORS++))
fi

# Check for GitHub tokens (actual tokens, not test values)
if grep -rn "ghp_[A-Za-z0-9]\{36\}" "$REPO_ROOT" --include="*.py" --include="*.tf" --include="*.yml" --include="*.yaml" 2>/dev/null | grep -v ".git" | grep -v node_modules | grep -v ".venv" | head -5; then
    echo "ERROR: Found potential GitHub personal access token!"
    ((ERRORS++))
fi

# Check for Google API keys (actual keys, not documentation)
if grep -rn "AIza[A-Za-z0-9_-]\{35\}" "$REPO_ROOT" --include="*.py" --include="*.tf" --include="*.yml" --include="*.yaml" 2>/dev/null | grep -v ".git" | grep -v node_modules | grep -v ".venv" | head -5; then
    echo "ERROR: Found potential Google API key!"
    ((ERRORS++))
fi

# Check for AWS access keys
if grep -rn "AKIA[A-Z0-9]\{16\}" "$REPO_ROOT" --include="*.py" --include="*.tf" --include="*.yml" --include="*.yaml" 2>/dev/null | grep -v ".git" | grep -v node_modules | grep -v ".venv" | head -5; then
    echo "ERROR: Found potential AWS access key!"
    ((ERRORS++))
fi

echo "OK: No obvious hardcoded secrets found"
echo ""

# Check Terraform for overly permissive IAM
echo "Checking Terraform for overly permissive IAM..."

# Check for roles/owner in actual TF code (not docs or comments)
if grep -rn 'role\s*=\s*"roles/owner"' "$REPO_ROOT/infra/terraform" --include="*.tf" 2>/dev/null; then
    echo "ERROR: Found roles/owner in Terraform - too permissive!"
    ((ERRORS++))
fi

# Check for roles/editor in actual TF code (not docs or comments)
if grep -rn 'role\s*=\s*"roles/editor"' "$REPO_ROOT/infra/terraform" --include="*.tf" 2>/dev/null; then
    echo "WARNING: Found roles/editor in Terraform - consider more specific roles"
    ((WARNINGS++))
fi

echo "OK: Terraform IAM permissions checked"
echo ""

# Check for allAuthenticatedUsers (INFO only - often intentional for public APIs)
echo "Checking for allAuthenticatedUsers IAM..."
if grep -rn "allAuthenticatedUsers" "$REPO_ROOT/infra/terraform" --include="*.tf" 2>/dev/null; then
    echo "INFO: Found allAuthenticatedUsers - verify this is intentional"
else
    echo "OK: No allAuthenticatedUsers found"
fi
echo ""

# Check for proper Secret Manager usage
echo "Checking Secret Manager patterns..."
if grep -rn "SLACK_BOT_TOKEN\s*=" "$REPO_ROOT/infra/terraform" --include="*.tf" 2>/dev/null | grep -v "secret_id" | grep -v "SECRET_ID"; then
    echo "WARNING: Found direct SLACK_BOT_TOKEN assignment - use Secret Manager reference"
    ((WARNINGS++))
fi
echo "OK: Secret Manager patterns checked"
echo ""

# Check Cloud Run ingress settings
echo "Checking Cloud Run ingress settings..."
# This is informational - ingress settings depend on architecture
if grep -rn "allow_unauthenticated" "$REPO_ROOT/infra/terraform" --include="*.tf" 2>/dev/null; then
    echo "INFO: Found allow_unauthenticated settings - verify intentional"
fi
echo ""

# Check for .env files (excluding templates and examples)
echo "Checking for .env files in git..."
if git -C "$REPO_ROOT" ls-files | grep -E "\.env$" | grep -v ".env.example" | grep -v ".env.template" | grep -v "archive/"; then
    echo "ERROR: Found .env files tracked in git!"
    ((ERRORS++))
else
    echo "OK: No .env files tracked in git"
fi
echo ""

# Summary
echo "=== Security Validation Summary ==="
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo "FAILED: $ERRORS security error(s) found"
    exit 1
fi

if [ $WARNINGS -gt 0 ]; then
    echo "PASSED with $WARNINGS warning(s)"
else
    echo "PASSED: No security issues found"
fi

exit 0
