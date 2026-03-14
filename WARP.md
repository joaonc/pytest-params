# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

A library that provides simplified pytest test case parameters via the `@params` decorator and
the `get_request_param` function. Helps make parametrized tests more readable and declarative.

## Development Commands

Always use `uv`. Do not use `pip` or `pip-tools`.

### Task Runner
This project uses `typer-invoke` to organize development tasks into admin modules. The
configuration is in `pyproject.toml` under `[tool.typer-invoke]`.

Run tasks using Python module syntax:
```bash
python -m admin.lint --help
python -m admin.build --help
python -m admin.pip --help
python -m admin.test --help
```

### Linting and Formatting
All linter configurations are in `pyproject.toml`.

Run all linters in sequence:
```bash
python -m admin.lint all
```

Run individual linters:
```bash
python -m admin.lint ruff .
python -m admin.lint mypy .
```

### Testing

Run unit tests (installs the package temporarily):
```bash
python -m admin.test unit
```

### Building and Publishing

Clean build artifacts:
```bash
python -m admin.build clean
```

Update version (interactive or with flags):
```bash
python -m admin.build version --bump patch
python -m admin.build version --version 1.2.3
```

Build and publish package:
```bash
python -m admin.build publish
```

### Package Management

Compile requirements files (uses uv):
```bash
python -m admin.pip compile
python -m admin.pip compile --clean
```

Sync environment with requirements:
```bash
python -m admin.pip sync
```

Install requirements:
```bash
python -m admin.pip install
```

## Code Architecture

### Module Structure
```
src/pytest_params/
├── __init__.py              # Package exports and version
├── params.py                # @params decorator implementation
└── request_params.py        # get_request_param() function

admin/                        # Development task modules
├── __init__.py              # Project constants (PROJECT_ROOT, SOURCE_DIR)
├── utils.py                 # Shared utilities (run, logger, etc.)
├── build.py                 # Build, version, and publish tasks
├── lint.py                  # Linting tasks (ruff, mypy)
├── pip.py                   # Package management tasks
├── test.py                  # Test tasks
└── requirements/            # Requirements files (.in and .txt)

tests/                        # Test suite
```

## Code Style

- Follow PEP8 with 100 character line limit (enforced by ruff)
- Single quotes for strings, triple double quotes for docstrings
- Python 3.12+ syntax and type hints (use `str | None` not `Optional[str]`)
- 4 spaces for indentation
