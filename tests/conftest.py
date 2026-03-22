from __future__ import annotations

from unittest.mock import patch

import pytest

from data_gov_uk.api import DataGovUk


@pytest.fixture
def sample_organizations():
    return ["department-for-transport", "environment-agency", "ministry-of-defence"]


@pytest.fixture
def sample_packages():
    return ["traffic-speed-data", "air-quality-index", "flood-risk-mapping"]


@pytest.fixture
def sample_package_show_result():
    """A realistic package_show result with resources."""
    return {
        "name": "traffic-speed-data",
        "title": "Traffic Speed Data",
        "resources": [
            {
                "description": "2024 data",
                "format": "CSV",
                "id": "res-1",
                "mimetype": "text/csv",
                "name": "traffic_2024.csv",
                "package_id": "traffic-speed-data",
                "resource_type": "file",
                "created": "2024-06-01T00:00:00",
                "url": "https://example.com/traffic_2024.csv",
            },
            {
                "description": "2023 data",
                "format": "CSV",
                "id": "res-2",
                "mimetype": "text/csv",
                "name": "traffic_2023.csv",
                "package_id": "traffic-speed-data",
                "resource_type": "file",
                "created": "2023-06-01T00:00:00",
                "url": "https://example.com/traffic_2023.csv",
            },
        ],
    }


@pytest.fixture
def client(sample_organizations, sample_packages):
    """DataGovUk client with pre-cached org and package lists (no HTTP)."""
    with patch("data_gov_uk.api.requests.Session"):
        c = DataGovUk()
    c._all_organizations = sample_organizations
    c._all_packages = sample_packages
    return c
