# Contributing to Serpentine Engine

Thank you for contributing to the Serpentine Engine! Please follow these guidelines to ensure consistency and quality.

## 1. Getting Started

1.  **Read the Docs**: Start with [Architecture Overview](des_docs/ARCHITECTURE.md) and [Engine Overview](des_docs/architecture/engine_overview.md).
2.  **Environment**: See the [Offline Development Guide](des_docs/guides/offline_dev_guide.md) for setting up your environment.

## 2. Development Workflow

1.  **Create a Branch**: Always work on a feature branch (`feat/new-system`, `fix/collision-bug`).
2.  **Write Tests**: Every new feature must have accompanying tests. See [Testing Strategy](des_docs/guides/testing_strategy.md).
3.  **Document**: Update `des_docs/` if you change architecture. Follow [Documentation Rules](des_docs/dev_docs_rules.md).

## 3. Code Style & Standards

### 3.1. Python
*   **Type Hints**: Strict typing is required. Use `typing.List`, `typing.Optional`, etc.
*   **Pydantic**: Use `pydantic.BaseModel` for all data structures (Components, Messages).
*   **Async**: The core engine is asynchronous. Use `async def` for I/O bound tasks.
*   **Formatting**: We follow PEP8. (Run `black` if available).

### 3.2. ECS Specifics
*   **Components**: Must be pure data. No logic methods.
*   **Systems**: Must be stateless. Logic only.
*   **Entities**: Are just UUIDs. Do not extend the `Entity` class.

## 4. Pull Request Checklist

Before submitting a PR, ensure you have:

- [ ] Run `pytest` and verified all tests pass.
- [ ] Added unit tests for new functionality.
- [ ] Updated relevant documentation in `des_docs/`.
- [ ] Verified no new dependencies were added (unless discussed).
- [ ] Checked for sensitive data (API keys) in the code.

## 5. Reporting Issues

*   **Bugs**: provide a minimal reproduction script.
*   **Features**: RFCs should be drafted in `des_docs/planning/` before implementation.
