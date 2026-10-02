# ADR-001: Python Runtime

## Status

Accepted

## Decision

FinGuard AI will use Python 3.13 as its primary application runtime.

## Context

FinGuard AI is a new Python project that will use modern AI/ML, API, database, testing, and cloud tooling.

The project requires a Python version that provides a good balance between:

- modern language and runtime improvements
- active support
- library compatibility
- production stability

## Decision Rationale

Python 3.13 was selected as the project's runtime.

It provides a modern, actively supported Python release while avoiding unnecessary dependence on the newest runtime version during the initial development of the project.

The project uses an isolated virtual environment (`.venv`) so dependencies are managed separately from the system Python installation.

## Consequences

- Developers should use Python 3.13 for local development.
- Project dependencies must be installed inside the project virtual environment.
- Library compatibility should be verified before adding dependencies.