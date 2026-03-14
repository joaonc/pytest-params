# Development
## Requirements
[`uv`](https://docs.astral.sh/uv/) is required. Install it first, then set up the environment:
```bash
uv venv
uv sync --all-groups
```

## Tasks
This project uses **typer-invoke** ([GitHub](https://github.com/joaonc/typer-invoke)) to
facilitate executing miscellaneous tasks that help with development.

### Using typer-invoke
After syncing dependencies (which include `typer-invoke`), try the commands below.

* Help for a module
  ```
  python -m admin.lint --help
  python -m admin.build --help
  python -m admin.pip --help
  python -m admin.test --help
  ```
* Help with a specific command
  ```
  python -m admin.pip compile --help
  ```
* Use `--dry` to see what a command does without executing it.

## Development and testing
[pytest](https://docs.pytest.org/en/stable/) is used to run the tests.

Given that we're testing a fixture for pytest tests, some of the tests (modules ending with
`_output`) are done by running the tests in memory and examining the results report.  
That is done using [pytester](https://docs.pytest.org/en/stable/reference/reference.html#pytester).
See test cases implementation on how `pytester` is used and the report output analyzed.

To run tests:
```bash
python -m admin.test unit
```
