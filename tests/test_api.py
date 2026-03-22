from __future__ import annotations

from unittest.mock import patch

import pytest

from data_gov_uk.api import DataGovUk
from data_gov_uk.exceptions import OrganizationNotFound, PackageNotFound

# ── Initialization ──────────────────────────────────────────────────


class TestInit:
    def test_defaults(self):
        with patch("data_gov_uk.api.requests.Session"):
            c = DataGovUk()
        assert c.url == "https://data.gov.uk/api/3/action"
        assert c._all_packages is None
        assert c._all_organizations is None

    def test_context_manager(self):
        with patch("data_gov_uk.api.requests.Session") as MockSession:
            with DataGovUk() as c:
                assert c.url == "https://data.gov.uk/api/3/action"
            MockSession.return_value.close.assert_called_once()


# ── _get_response ───────────────────────────────────────────────────


class TestGetResponse:
    def test_success(self, client):
        with patch("data_gov_uk.api.Response") as MockResp:
            mock_inst = MockResp.return_value
            mock_inst.get_json_from_response.return_value = {
                "success": True,
                "result": {"data": 1},
            }
            result = client._get_response("https://example.com")
        assert result == {"data": 1}

    def test_failure_returns_none(self, client):
        with patch("data_gov_uk.api.Response") as MockResp:
            mock_inst = MockResp.return_value
            mock_inst.get_json_from_response.return_value = {
                "success": False,
                "error": {"__type": "Not Found", "message": "not found"},
            }
            result = client._get_response("https://example.com")
        assert result is None

    def test_none_response_returns_none(self, client):
        with patch("data_gov_uk.api.Response") as MockResp:
            mock_inst = MockResp.return_value
            mock_inst.get_json_from_response.return_value = None
            result = client._get_response("https://example.com")
        assert result is None

    def test_passes_session_and_kwargs(self, client):
        with patch("data_gov_uk.api.Response") as MockResp:
            mock_inst = MockResp.return_value
            mock_inst.get_json_from_response.return_value = {
                "success": True,
                "result": [],
            }
            client._get_response("https://example.com", params={"rows": "10"})
        MockResp.assert_called_with("https://example.com", session=client._session, params={"rows": "10"})


# ── Input validation ────────────────────────────────────────────────


class TestInputValidation:
    def test_rejects_none(self, client):
        with pytest.raises(TypeError, match="must be a string"):
            client.filter_dataset_for_organization(None)

    def test_rejects_integer(self, client):
        with pytest.raises(TypeError, match="must be a string"):
            client.get_info_for_package_id(123)

    def test_rejects_empty_string(self, client):
        with pytest.raises(ValueError, match="must not be empty"):
            client.search_available_organizations("")

    def test_rejects_whitespace_only(self, client):
        with pytest.raises(ValueError, match="must not be empty"):
            client.search_available_packages("   ")

    def test_strips_whitespace(self, client):
        result = client.search_available_organizations("  transport  ")
        assert any("transport" in o for o in result)


# ── Lazy-cached properties ──────────────────────────────────────────


class TestCachedProperties:
    def test_all_packages_caches(self, client):
        client._all_packages = None
        with patch.object(client, "_get_response", return_value=["pkg-a"]) as mock:
            _ = client.all_packages
            _ = client.all_packages
        assert mock.call_count == 1

    def test_all_organizations_caches(self, client):
        client._all_organizations = None
        with patch.object(client, "_get_response", return_value=["org-alpha"]) as mock:
            _ = client.all_organizations
            _ = client.all_organizations
        assert mock.call_count == 1

    def test_all_packages_returns_list(self, client):
        client._all_packages = None
        with patch.object(client, "_get_response", return_value=["a", "b"]):
            result = client.all_packages
        assert result == ["a", "b"]


# ── Assertion helpers ───────────────────────────────────────────────


class TestAssertions:
    def test_assert_organization_exists_passes(self, client):
        client._assert_organization_exists("department-for-transport")

    def test_assert_organization_exists_raises(self, client):
        with pytest.raises(OrganizationNotFound):
            client._assert_organization_exists("nonexistent-org")

    def test_assert_package_exists_passes(self, client):
        client._assert_package_exists("traffic-speed-data")

    def test_assert_package_exists_raises(self, client):
        with pytest.raises(PackageNotFound):
            client._assert_package_exists("nonexistent-pkg")


# ── filter_dataset_for_organization ─────────────────────────────────


class TestFilterDataset:
    def test_valid_org(self, client):
        with patch.object(client, "_get_response", return_value={"count": 5}) as mock:
            result = client.filter_dataset_for_organization("department-for-transport")
        assert result == {"count": 5}
        mock.assert_called_with(
            f"{client.url}/package_search",
            params={"fq": "organization:department-for-transport"},
        )

    def test_invalid_org_raises(self, client):
        with pytest.raises(OrganizationNotFound):
            client.filter_dataset_for_organization("nonexistent")


# ── get_organization_info ───────────────────────────────────────────


class TestGetOrganizationInfo:
    def test_without_datasets(self, client):
        with patch.object(client, "_get_response", return_value={"title": "DfT"}) as mock:
            client.get_organization_info("department-for-transport")
        mock.assert_called_with(
            f"{client.url}/organization_show",
            params={"id": "department-for-transport", "include_datasets": "False"},
        )

    def test_with_datasets(self, client):
        with patch.object(client, "_get_response", return_value={"title": "DfT"}) as mock:
            client.get_organization_info("department-for-transport", show_datasets=True)
        mock.assert_called_with(
            f"{client.url}/organization_show",
            params={"id": "department-for-transport", "include_datasets": "True"},
        )

    def test_invalid_org_raises(self, client):
        with pytest.raises(OrganizationNotFound):
            client.get_organization_info("nonexistent")


# ── search_available_organizations / packages ───────────────────────


class TestSearch:
    def test_search_orgs_found(self, client):
        result = client.search_available_organizations("transport")
        assert any("transport" in o for o in result)

    def test_search_orgs_not_found(self, client):
        with pytest.raises(OrganizationNotFound):
            client.search_available_organizations("xyznonexistent999")

    def test_search_packages_found(self, client):
        result = client.search_available_packages("traffic")
        assert any("traffic" in p for p in result)

    def test_search_packages_not_found(self, client):
        with pytest.raises(PackageNotFound):
            client.search_available_packages("xyznonexistent999")


# ── _fetch_packages_and_datasets ────────────────────────────────────


class TestFetchPackagesAndDatasets:
    def test_returns_dict_with_correct_keys(self, client, sample_package_show_result):
        data = client._fetch_packages_and_datasets([sample_package_show_result])
        assert "traffic-speed-data" in data
        assert len(data["traffic-speed-data"]) == 2

    def test_sorts_by_created_at_descending(self, client, sample_package_show_result):
        data = client._fetch_packages_and_datasets([sample_package_show_result])
        resources = data["traffic-speed-data"]
        assert resources[0]["created_at"] >= resources[1]["created_at"]

    def test_resource_fields_extracted(self, client, sample_package_show_result):
        data = client._fetch_packages_and_datasets([sample_package_show_result])
        resource = data["traffic-speed-data"][0]
        expected_keys = {
            "description",
            "file_format",
            "file_id",
            "mime_type",
            "name",
            "package_id",
            "resource_type",
            "created_at",
            "file_url",
        }
        assert set(resource.keys()) == expected_keys


# ── get_info_for_package_id ─────────────────────────────────────────


class TestGetInfoForPackageId:
    def test_valid_package(self, client):
        with patch.object(client, "_get_response", return_value={"name": "traffic-speed-data"}):
            result = client.get_info_for_package_id("traffic-speed-data")
        assert result["name"] == "traffic-speed-data"

    def test_invalid_package_raises(self, client):
        with pytest.raises(PackageNotFound):
            client.get_info_for_package_id("nonexistent-pkg")


# ── get_resources_for_package_id ────────────────────────────────────


class TestGetResourcesForPackageId:
    def test_valid_package(self, client, sample_package_show_result):
        with patch.object(client, "_get_response", return_value=sample_package_show_result):
            result = client.get_resources_for_package_id("traffic-speed-data")
        assert "traffic-speed-data" in result

    def test_none_response_returns_none(self, client):
        with patch.object(client, "_get_response", return_value=None):
            result = client.get_resources_for_package_id("traffic-speed-data")
        assert result is None


# ── _get_packages_from_organization_for_under_1000 ──────────────────


class TestGetPackagesUnder1000:
    def test_normal_count(self, client, sample_package_show_result):
        responses = [
            {"count": 2},  # filter_dataset_for_organization
            {"results": [sample_package_show_result]},  # second _get_response call
        ]
        with patch.object(client, "_get_response", side_effect=responses):
            result = client._get_packages_from_organization_for_under_1000("department-for-transport")
        assert isinstance(result, dict)
        assert "traffic-speed-data" in result

    def test_over_1000_returns_none(self, client):
        with patch.object(client, "_get_response", return_value={"count": 1500}):
            result = client._get_packages_from_organization_for_under_1000("department-for-transport")
        assert result is None

    def test_zero_count_returns_none(self, client):
        with patch.object(client, "_get_response", return_value={"count": 0}):
            result = client._get_packages_from_organization_for_under_1000("department-for-transport")
        assert result is None


# ── _get_all_packages_and_datasets_for_organization ─────────────────


class TestGetAllPackagesForOrg:
    def test_pagination(self, client, sample_package_show_result):
        org_info = {"package_count": 3}
        page_result = {"results": [sample_package_show_result]}

        with patch.object(client, "_get_response", side_effect=[org_info, page_result]):
            result = client._get_all_packages_and_datasets_for_organization(
                "department-for-transport", n_results_to_fetch_per_request=100
            )
        assert isinstance(result, dict)
        assert "traffic-speed-data" in result
