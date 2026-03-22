# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python client library wrapping the CKAN API at data.gov.uk. Provides organisation/package discovery, fuzzy search (NLTK Snowball stemmer + SequenceMatcher), resource retrieval, CLI tool, and export utilities. Not yet published on PyPI.

## Build & Development

```bash
# Setup (Poetry-managed, requires Python >=3.11)
poetry install

# Run all tests
poetry run pytest tests/ -v

# Run a single test file or test
poetry run pytest tests/test_api.py -v
poetry run pytest tests/test_api.py::TestInit::test_defaults -v

# Lint
poetry run ruff check .

# Fix lint issues + format
poetry run ruff check --fix . && poetry run ruff format .
```

CI runs on GitHub Actions (Python 3.11/3.12/3.13) — see `.github/workflows/ci.yml`.

## Architecture

**Entry point:** `data_gov_uk/api.py` — `DataGovUk` class. All public API methods live here. Uses `requests.Session` with `urllib3.Retry` for connection pooling and automatic retries. Supports context manager protocol (`with DataGovUk() as client:`).

**`data_gov_uk/models.py`** — `Resource` and `Package` dataclasses for structured API responses.

**`data_gov_uk/cli.py`** — argparse-based CLI (`data-gov-uk` command) with subcommands: `search-orgs`, `search-packages`, `get-org`, `get-package`, `get-resources`.

**`data_gov_uk/export.py`** — `export_resources_to_json()` and `export_resources_to_csv()` for data export.

**`data_gov_uk/utils/`** — Shared utilities:
- `response.py` — `Response` class wrapping `requests.Session` with JSON parsing. Used by `DataGovUk._get_response()`.
- `strings_and_lists.py` — `ListOperations` (fuzzy list search via Snowball stemmer and SequenceMatcher) and `StringOperations` (number parsing). The search pipeline in `DataGovUk._search_list_by_string` tries stemmer match first, then falls back to SequenceMatcher with 0.5 threshold.
- `log_helper.py` — `get_logger()` function + `BasicLogger` compatibility shim wrapping stdlib `logging`.

**`data_gov_uk/exceptions.py`** — `OrganizationNotFound`, `PackageNotFound`.

## Key Dependencies

- `requests` — HTTP calls to CKAN API (`https://data.gov.uk/api/3/action`)
- `nltk` — Snowball stemmer for fuzzy search (lazy-loaded on first use)

## Important Patterns

- `all_packages` and `all_organizations` are lazy-loaded cached properties. First access triggers an API call; subsequent accesses return cached data. Legacy uppercase aliases (`ALL_PACKAGES`, `ALL_ORGANIZATIONS`) are maintained for backward compatibility.
- All public methods validate string inputs via `_validate_string()` — rejects None, non-string, empty, whitespace-only.
- All HTTP requests share a single `requests.Session` with `urllib3.Retry` (3 retries, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]).
- URL query parameters are always passed via `params` dict (never interpolated into URL strings) to prevent injection.
- `ClassInitiationError` is the correct name; `ClassIntiationError` is a deprecated alias.
