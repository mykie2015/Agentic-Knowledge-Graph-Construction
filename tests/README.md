# Tests Directory

This directory contains all test files for the Agentic Knowledge Graph Construction project.

## Structure

```
tests/
├── __init__.py                    # Main tests package
├── test_imports.py               # System integration tests
├── agents/                       # Agent-specific tests
│   ├── __init__.py
│   └── test_user_intent_config.py  # User Intent Agent configuration tests
├── config/                       # Configuration tests
│   ├── __init__.py
│   └── test_config_parsing.py     # Configuration parsing tests
├── core/                         # Core functionality tests
│   └── __init__.py
└── utils/                        # Utility function tests
    └── __init__.py
```

## Running Tests

### All Tests
```bash
# Run system integration tests
python tests/test_imports.py
```

### Category-Specific Tests
```bash
# Test agent functionality
python tests/agents/test_user_intent_config.py

# Test configuration parsing
python tests/config/test_config_parsing.py
```

### Manual Testing
```bash
# Test agents interactively
cd src
python -c "from agents.user_intent_agent import UserIntentAgent; print(UserIntentAgent().health_check())"
```

## Writing New Tests

When creating new test files:

1. **Location**: Save under the appropriate subdirectory that matches your source code structure
2. **Naming**: Use the format `test_<functionality>.py`
3. **Structure**: Include proper docstrings and error handling
4. **Dependencies**: Import from the `src` directory using relative imports

## Test Guidelines

- All test files are preserved for debugging and validation
- Tests should be self-contained and not depend on external state
- Include both positive and negative test cases where applicable
- Follow the project's coding standards and type hints
- Document any special setup requirements in the test file

## Integration with Development

The test structure follows the cursor rules defined in `.cursorrules`:
- Test files must be saved under `tests/` folder
- Test files should NOT be removed
- Tests are organized to match the source code structure
- Follow naming conventions for consistency
