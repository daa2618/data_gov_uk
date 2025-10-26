# data_gov_uk

`data_gov_uk` is a lightweight Python helper around the CKAN API that powers [data.gov.uk](https://data.gov.uk). It wraps the most common workflows (discovering organisations, locating datasets, drilling into resources) behind a single `DataGovUk` client so analysts and developers can focus on the data rather than the HTTP plumbing.

---

## Key capabilities

- Cache the complete catalogue of organisations and dataset package identifiers so repeated lookups stay fast.
- Search organisations or packages by free text with simple fuzzy matching.
- Retrieve rich metadata for an organisation, including its constituent packages and datasets.
- Pull package-level details and resource download links in one call.
- Raise clear custom exceptions (`OrganizationNotFound`, `PackageNotFound`) when lookups fail.

---

## Requirements

- Python 3.11 or newer
- `requests`, `pandas`, and `nltk` (installed automatically when you install the package)

To work in isolation, create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Installation

Install the package straight from the source tree:

```bash
pip install .
```

If you prefer editable installs while iterating locally:

```bash
pip install -e .
```

Poetry users can instead run:

```bash
poetry install
```

Once the project is published on PyPI you will be able to install it with:

```bash
pip install data-gov-uk
```

---

## Quick start

```python
from data_gov_uk.api import DataGovUk

client = DataGovUk()

# List all organisations (cached after the first call)
organisations = client.ALL_ORGANIZATIONS
print(f"{len(organisations)} organisations available")

# Search for a specific organisation (fuzzy match)
matches = client.search_available_organizations("department for transport")
print("Closest matches:", matches)

# Fetch datasets for an organisation (<=1000 datasets returned)
dept_id = "department-for-transport"
datasets = client.filter_dataset_for_organization(dept_id)
print("Datasets count:", datasets["count"])

# Inspect organisation metadata (set show_datasets=True for full package info)
org_info = client.get_organization_info(dept_id, show_datasets=True)
print(org_info["title"])

# Explore a package and its resources
package_id = client.search_available_packages("traffic-speed")[0]
package = client.get_info_for_package_id(package_id)
resources = client.get_resources_for_package_id(package_id)
print("Package resources:", resources[package["name"]])
```

The methods above return dictionaries mirroring the CKAN API responses so you can feed the data straight into `pandas` for analysis or export.

---

## Error handling

- `OrganizationNotFound` is raised when searching for an organisation that does not exist.
- `PackageNotFound` is raised when a package identifier cannot be resolved.

Catch these exceptions in your code path to present user-friendly messages or retries.

---

## Development notes

- Logging is handled via an internal helper (`BasicLogger`) and is silent by default. Enable verbose output by adjusting the helper in `data_gov_uk/api.py` if you need request traces while debugging.
- Methods prefixed with `_` (for example `_get_all_packages_and_datasets_for_organization`) are internal helpers and may change without notice; stick to the public methods documented above for stability.

Contributions are welcome—bug reports, documentation tweaks, or additional API coverage all help. Open an issue or submit a pull request.

---

## License

This project is released under the [MIT License](LICENSE).

