# Phase 33: Gemini Code Assist Setup

**Date:** 2025-12-11
**Status:** In Progress
**Branch:** `feature/phase-33-gemini-code-assist-setup`

## Objective

Enable Gemini Code Assist to automatically review pull requests, providing AI-powered code review aligned with Bob's Brain Hard Mode rules.

## Non-Goals

- Modifying existing CI workflows
- Replacing human code review
- Adding blocking gates (informational only)

## Deliverables

1. **Gemini Configuration**
   - `.gemini/settings.json` - Review settings (severity threshold, max comments)
   - `.gemini/styleguide.md` - Project-specific style guide for AI reviewer

2. **Documentation**
   - Phase PLAN doc (this file)
   - Phase AAR doc (after completion)

## Configuration Details

### settings.json
```json
{
  "code_review": {
    "enabled": true,
    "auto_review_on_pr": true,
    "severity_threshold": "MEDIUM",
    "max_comments": 20,
    "ignore_paths": ["000-docs/**", "*.md", "*.json", "*.yaml"]
  },
  "summary": {
    "enabled": true,
    "auto_summary_on_pr": true
  }
}
```

### styleguide.md
- References Hard Mode rules (R1-R8)
- Documents ADK-specific patterns
- Security focus areas
- Testing requirements

## Prerequisites

1. Gemini Code Assist GitHub App must be installed at org level
2. App available at: https://github.com/marketplace/gemini-code-assist

## Implementation Steps

1. Create `.gemini/` directory with config files
2. Create phase documentation
3. Push and create PR
4. Verify Gemini Code Assist activates on the PR

---
**Last Updated:** 2025-12-11
