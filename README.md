# data_gov_uk

`data_gov_uk` is a lightweight Python client for the CKAN API that powers [data.gov.uk](https://data.gov.uk). It wraps the most common workflows — discovering organisations, locating datasets, drilling into resources — behind a single `DataGovUk` client so analysts and developers can focus on the data rather than the HTTP plumbing.

---

## Key capabilities

- Cache the complete catalogue of organisations and dataset package identifiers so repeated lookups stay fast.
- Search organisations or packages by free text with fuzzy matching (Snowball stemmer + SequenceMatcher).
- Retrieve rich metadata for an organisation, including its constituent packages and datasets.
- Pull package-level details and resource download links in one call.
- Export resources to JSON or CSV with built-in utilities.
- Interact from the terminal via the `data-gov-uk` CLI.
- Automatic retries with exponential backoff for transient errors (429, 5xx).
- Raise clear custom exceptions (`OrganizationNotFound`, `PackageNotFound`) when lookups fail.

---

## Requirements

- Python 3.11 or newer
- `requests` and `nltk` (installed automatically with the package)

---

## Installation

Poetry (recommended for development):

```bash
poetry install
```

Or install from the source tree:

```bash
pip install .
```

For editable installs while iterating locally:

```bash
pip install -e .
```

Once the project is published on PyPI you will be able to install with:

```bash
pip install data-gov-uk
```

---

## Quick start

```python
from data_gov_uk import DataGovUk

with DataGovUk() as client:
    # List all organisations (cached after the first call)
    organisations = client.all_organizations
    print(f"{len(organisations)} organisations available")

    # Search for a specific organisation (fuzzy match)
    matches = client.search_available_organizations("department for transport")
    print("Closest matches:", matches)

    # Fetch datasets for an organisation
    dept_id = "department-for-transport"
    datasets = client.filter_dataset_for_organization(dept_id)
    print("Datasets count:", datasets["count"])

    # Inspect organisation metadata
    org_info = client.get_organization_info(dept_id, show_datasets=True)
    print(org_info["title"])

    # Explore a package and its resources
    package_id = client.search_available_packages("traffic-speed")[0]
    package = client.get_info_for_package_id(package_id)
    resources = client.get_resources_for_package_id(package_id)
    print("Package resources:", resources[package["name"]])
```

### Exporting data

```python
from data_gov_uk.export import export_resources_to_json, export_resources_to_csv

# resources is a dict mapping package names to lists of resource dicts
export_resources_to_json(resources, "output.json")
export_resources_to_csv(resources, "output.csv")
```

### Data models

Structured dataclasses are available for type-safe work:

```python
from data_gov_uk import Resource, Package
```

---

## CLI

After installation, the `data-gov-uk` command is available:

```bash
# Search for organisations
data-gov-uk search-orgs "transport"

# Search for packages
data-gov-uk search-packages "traffic"

# Get organisation info (add --datasets for full package info)
data-gov-uk get-org department-for-transport --datasets

# Get package metadata
data-gov-uk get-package traffic-speed-data

# Get resources for a package
data-gov-uk get-resources traffic-speed-data
```

---

## Error handling

- `OrganizationNotFound` — raised when an organisation cannot be found.
- `PackageNotFound` — raised when a package identifier cannot be resolved.

```python
from data_gov_uk import DataGovUk, OrganizationNotFound

with DataGovUk() as client:
    try:
        client.search_available_organizations("nonexistent")
    except OrganizationNotFound as e:
        print(f"Not found: {e}")
```

---

## Development

```bash
# Install dev dependencies
poetry install

# Run tests
poetry run pytest tests/ -v

# Run a single test
poetry run pytest tests/test_api.py::TestInit::test_defaults -v

# Lint
poetry run ruff check .

# Auto-fix lint issues and format
poetry run ruff check --fix . && poetry run ruff format .
```

CI runs on GitHub Actions across Python 3.11, 3.12, and 3.13. See `.github/workflows/ci.yml`.

### Pre-commit hooks

```bash
poetry run pre-commit install
```

This enables automatic linting and formatting on every commit via ruff.

### Architecture

- **`data_gov_uk/api.py`** — `DataGovUk` client class. Uses `requests.Session` with connection pooling and `urllib3.Retry` for automatic retries. Supports the context manager protocol.
- **`data_gov_uk/models.py`** — `Resource` and `Package` dataclasses.
- **`data_gov_uk/cli.py`** — argparse-based CLI entry point.
- **`data_gov_uk/export.py`** — JSON and CSV export utilities.
- **`data_gov_uk/utils/`** — Shared utilities: HTTP response handling, fuzzy string matching, logging.
- **`data_gov_uk/exceptions.py`** — Custom exception classes.

---

## License

This project is released under the [MIT License](LICENSE).
