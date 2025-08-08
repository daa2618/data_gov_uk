# data_gov_uk

**data_gov_uk** is a Python wrapper to work with [data.gov.uk](https://data.gov.uk) easily and reliably. It simplifies accessing UK police data via their public API, helping you fetch, filter, and analyze open source data from the UK government.

---

## 🚀 Features

- 🔍 Search data by location, date, or category
- 🧑‍✈️ Access department spendings and rumenerations
- 🧩 Fetch neighbourhood boundary and data
- ⚙️ Simple Pythonic interface
- 🧪 Designed for analysts, data scientists, and developers

---

## 🧪 Prerequisites

- Python 3.11+
- `requests` library (installed automatically with pip)
- `pandas`
- `nltk`

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 📦 Installation

Clone and install locally:

```bash
git clone https://github.com/daa2618/data_gov_uk.git
cd data_gov_uk
pip install .
```

Or install directly using pip (once published on PyPI):

```bash
pip install data_gov_uk
```

---

## 🎯 Usage

Here’s how to get started:

```python
from data_gov_uk.api import DataGovUk

client = DataPoliDataGovUkceUK()

# Get all available organizations
orgs = client.ALL_ORGANIZATIONS
print(f"The following orgaizations are found in data.gov.uk website: {', '.join(orgs)}")

---
# Filter data by organization
dept = "Department of Transport"
matched_data = client.filter_dataset_for_organization(dept)
print(f"'{len(matched_data)}' datasets are available for '{dept}'")

---
# Get organization info
org_info = client.get_organization_info(dept)
print(org_info)

```

## 🧾 Contributing

Contributions welcome! You can help by:

- Submitting bug reports or feature requests via Issues
- Improving documentation
- Writing tests or fixing bugs
- Extending API support

Please open a PR or reach out via GitHub Issues.

---

## ⚖️ License

This project is licensed under the [MIT License](LICENSE).

---
