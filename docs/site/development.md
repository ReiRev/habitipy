# Development

## Local Setup

Use Poetry for local development:

```bash
poetry install --extras dev
poetry run pre-commit install
```

## Quality Checks

Run the full local quality pass before finishing Python changes:

```bash
poetry run isort habitipie tests
poetry run black habitipie tests
poetry run ruff check habitipie tests
poetry run mypy habitipie
```

Or use the dedicated tox environment:

```bash
poetry run tox run -e quality
```

Run a focused test slice:

```bash
poetry run pytest tests/test_habits.py
```

Generate coverage locally:

```bash
poetry run pytest --cov=habitipie --cov-report=term-missing
```

Run the declared Python support matrix with `tox`:

```bash
poetry run tox run -e py310,py311,py312,py313
```

## Documentation Workflow

Build the docs locally:

```bash
poetry run mkdocs build --strict
```

Run the live preview server:

```bash
poetry run mkdocs serve
```

GitHub Actions validates the docs build on pull requests and deploys the generated site
to GitHub Pages from `main`.

## Release

Pushing a version tag triggers the `Release` GitHub Actions workflow, which runs
quality checks, the test matrix, builds the distributions, and publishes them to PyPI.

Before tagging a release:

- update `version` in `pyproject.toml`
- make sure the `pypi` GitHub environment and PyPI trusted publishing are configured

Create and push a release tag whose name matches `v<version>`:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The workflow verifies that the tag matches `pyproject.toml` before publishing.