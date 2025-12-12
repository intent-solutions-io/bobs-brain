# Tests Directory

This directory contains test suites for the IAM department.

## Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── test_agents.py
│   └── test_tools.py
├── integration/       # Integration tests
│   └── test_a2a.py
└── arv_golden/        # Golden tests for ARV (optional)
    └── test_arv_golden.py
```

## Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ --cov=agents --cov-report=html
```

## Test Patterns

### Unit Tests
- Test individual functions/methods
- Mock external dependencies
- Fast execution (<1s per test)

### Integration Tests
- Test agent interactions
- Test A2A protocol compliance
- May use real (dev) Agent Engine

### ARV Golden Tests
- Test complete workflows
- Compare against expected outputs
- Non-blocking in CI

## CI Integration

Tests run in CI workflow:
```yaml
- name: Run unit tests
  run: pytest tests/unit/ -v
```

## Reference

See bobs-brain test patterns:
- `tests/unit/`
- `tests/integration/`

## TODO

1. [ ] Create test structure
2. [ ] Add unit tests for agents
3. [ ] Add A2A protocol tests
4. [ ] Configure pytest.ini
