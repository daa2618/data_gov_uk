from __future__ import annotations

import contextlib
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import OrganizationNotFound, PackageNotFound
from .utils.response import Response
from .utils.strings_and_lists import ListOperations

_logger = logging.getLogger(__name__)


class DataGovUk:
    """
    This class provides methods for interacting with the Data.gov.uk API.
    """

    def __init__(self, debug: bool = False):
        """
        Initializes the DataGovUk class with the base API URL.

        Attributes:
            url (str): The base URL for the Data.gov.uk API.
            _all_packages (list, optional): Cached list of all available datasets. Defaults to None.
            _all_organizations (list, optional): Cached list of all available organizations. Defaults to None.
        """
        self.url = "https://data.gov.uk/api/3/action"
        _logger.setLevel(logging.DEBUG if debug else logging.WARNING)

        self._session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

        self._all_packages = None
        self._all_organizations = None

    def close(self):
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @staticmethod
    def _validate_string(value, name: str) -> str:
        """Validate that value is a non-empty string."""
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string, got {type(value).__name__}")
        value = value.strip()
        if not value:
            raise ValueError(f"{name} must not be empty")
        return value

    def _get_response(self, url: str, **kwargs) -> dict | None:
        """
        Fetches data from a provided URL and handles error responses.

        Args:
            url (str): The URL to fetch data from.
            **kwargs: Additional arguments to be passed to the request object.

        Returns:
            dict: The parsed JSON response from the API, or None if an error occurs.
        """
        response = Response(url, session=self._session, **kwargs).get_json_from_response()
        if response:
            if response.get("success"):
                return response.get("result")
            else:
                error = response.get("error")
                msg = error.get("__type") + " : " + error.get("message")
                _logger.error(msg)
                return None

    @property
    def all_packages(self) -> list:
        """Retrieves the list of all available datasets on Data.gov.uk.

        Returns:
            list: A list containing information about all datasets.
        """
        if self._all_packages is None:
            dataset_url = f"{self.url}/package_list"
            self._all_packages = self._get_response(dataset_url)
        return self._all_packages

    # Backward-compatible aliases
    ALL_PACKAGES = all_packages

    @property
    def all_organizations(self) -> list:
        """Retrieves a list of all organizations.

        The result is cached for subsequent calls to avoid redundant API requests.

        Returns:
            list: A list of organizations.
        """
        if self._all_organizations is None:
            org_url = f"{self.url}/organization_list"
            self._all_organizations = self._get_response(org_url)
        return self._all_organizations

    # Backward-compatible alias
    ALL_ORGANIZATIONS = all_organizations

    def _assert_organization_exists(self, organization: str):
        if organization not in self.all_organizations:
            raise OrganizationNotFound(f"No organization named '{organization}' was found")

    def _assert_package_exists(self, package_id: str):
        if package_id not in self.all_packages:
            raise PackageNotFound(f"No package with ID '{package_id}' was found")

    def filter_dataset_for_organization(self, organization: str) -> dict:
        """Filters a dataset to include only packages from a specified organization.

        Args:
            organization: The name of the organization to filter by.

        Returns:
            A dictionary containing the search results.  The exact structure of this
            dictionary depends on the API response.  Raises an exception if the
            organization does not exist.

        Raises:
            OrganizationNotFound: If the specified organization does not exist.
        """
        organization = self._validate_string(organization, "organization")
        self._assert_organization_exists(organization)
        return self._get_response(
            f"{self.url}/package_search",
            params={"fq": f"organization:{organization}"},
        )

    def get_organization_info(self, organization: str, show_datasets: bool = False) -> dict:
        """Retrieves information about a specific organization.

        Args:
            organization: The ID or name of the organization.
            show_datasets: If True, includes dataset information in the response. Defaults to False.

        Returns:
            A dictionary containing the organization's information.  The specific keys and values
            will depend on the API response.  Returns an empty dictionary if the organization
            is not found or if an error occurs during the API call.

        Raises:
            OrganizationNotFound: If the organization does not exist.
        """
        organization = self._validate_string(organization, "organization")
        self._assert_organization_exists(organization)
        return self._get_response(
            f"{self.url}/organization_show",
            params={"id": organization, "include_datasets": str(show_datasets)},
        )

    def _search_list_by_string(self, search_list: list[str], search_string: str) -> list[str] | None:
        list_ops = ListOperations(search_list, search_string=search_string)

        filtered = list_ops.search_list_by_snowball()
        if filtered:
            return filtered
        else:
            filtered = list_ops.search_list_by_string_for_metric(0.5)
            if filtered:
                return filtered
            else:
                return None

    def search_available_organizations(self, organization: str) -> list:
        """Searches for organizations matching a given string.

        Args:
            organization: The string to search for within organization names.

        Returns:
            A list of organizations whose names contain the search string.

        Raises:
            OrganizationNotFound: If no organizations match the search string.
        """
        organization = self._validate_string(organization, "organization")
        filtered = self._search_list_by_string(self.all_organizations, organization)
        if filtered:
            return filtered
        else:
            raise OrganizationNotFound("No matching organizations could be found")

    def search_available_packages(self, package_name: str) -> list:
        """Searches for available packages matching a given name.

        Args:
            package_name: The name of the package to search for (case-insensitive).

        Returns:
            A list of packages whose names match the input `package_name`.

        Raises:
            PackageNotFound: If no packages matching the provided name are found in the database.
        """
        package_name = self._validate_string(package_name, "package_name")
        filtered = self._search_list_by_string(self.all_packages, package_name)
        if filtered:
            return filtered
        else:
            raise PackageNotFound("No matching packages could be found")

    def _fetch_packages_and_datasets(self, all_results: list[dict]) -> dict[str, list[dict]]:
        """Fetches and organizes packages and datasets from a list of results.

        Args:
            all_results: A list of dictionaries, where each dictionary represents a
                        package and contains a "resources" key with a list of dataset
                        dictionaries.

        Returns:
            dict: A dictionary where keys are package names and values are lists of
                dictionaries containing dataset metadata, sorted by creation date
                (most recent first).
        """
        data_dict = {
            result.get("name"): [
                dict(
                    description=x.get("description"),
                    file_format=x.get("format"),
                    file_id=x.get("id"),
                    mime_type=x.get("mimetype"),
                    name=x.get("name"),
                    package_id=x.get("package_id"),
                    resource_type=x.get("resource_type"),
                    created_at=x.get("created"),
                    file_url=x.get("url"),
                )
                for x in result.get("resources")
            ]
            for result in all_results
        }
        sorted_out = {}
        for key, files_list in data_dict.items():
            with contextlib.suppress(TypeError, ValueError):
                files_list.sort(key=lambda x: x.get("created_at"), reverse=True)
            sorted_out[key] = files_list
        return sorted_out

    def _get_packages_from_organization_for_under_1000(self, organization: str) -> dict | None:
        """Retrieves packages from a given organization if the number of datasets is less than or equal to 1000.

        Args:
            organization (str): The name of the organization to search for.

        Returns:
            dict: A dictionary containing the fetched packages and datasets, or None if no packages are found or
                if the number of datasets exceeds 1000.
        """
        data = self.filter_dataset_for_organization(organization)
        n_datasets = data.get("count")
        if n_datasets > 0 and n_datasets <= 1000:
            params = {"fq": f"organization:{organization}", "rows": str(n_datasets)}
            results = self._get_response(f"{self.url}/package_search", params=params)
            if results:
                all_results = results.get("results")
                return self._fetch_packages_and_datasets(all_results)
            else:
                return None
        else:
            _logger.warning("More than 1000 datasets found. Returning None.")
            return None

    def _get_all_packages_and_datasets_for_organization(
        self, organization: str, n_results_to_fetch_per_request: int = 100
    ) -> dict:
        """Retrieves all packages and datasets for a given organization.

        Iteratively fetches package information from a remote API,
        handling pagination to retrieve all packages associated with a specified organization.

        Args:
            organization: The name of the organization.
            n_results_to_fetch_per_request: Results per API request. Defaults to 100.

        Returns:
            dict: A dictionary where keys are package names and values are lists of associated datasets.
        """
        org_info = self.get_organization_info(organization)
        n_packages = org_info.get("package_count")
        _logger.info(f"Total Number of Packages(Topics) With the Organization '{organization}' : {n_packages}\n")

        n_requests = n_packages // n_results_to_fetch_per_request
        all_packages_and_datasets = {}

        start = 0

        search_url = f"{self.url}/package_search"
        for a in range(n_requests + 1):
            params = {
                "fq": f"organization:{organization}",
                "start": str(start),
                "rows": str(n_results_to_fetch_per_request),
            }

            result = self._get_response(search_url, params=params)
            _logger.info(f"\tRequest Count: {a}")
            _logger.info(f"\tPackages(Topics) obtained so far: {len(all_packages_and_datasets)}")
            if result:
                datasets = result.get("results")
                res = self._fetch_packages_and_datasets(datasets)
                if res:
                    all_packages_and_datasets.update(res)
                start += n_results_to_fetch_per_request

        _logger.info(f"Total Packages obtained: {len(all_packages_and_datasets)}")
        total_datasets = sum(len(value) for value in all_packages_and_datasets.values())
        _logger.info(f"Total Datasets for Organization: {total_datasets}")
        return all_packages_and_datasets

    def get_info_for_package_id(self, package_id: str) -> dict | None:
        """Retrieves information for a given package ID.

        Args:
            package_id: The ID of the package to retrieve information for.

        Returns:
            A dictionary containing the package information, or None if an error occurs.

        Raises:
            PackageNotFound: If the package with the given ID does not exist.
        """
        package_id = self._validate_string(package_id, "package_id")
        self._assert_package_exists(package_id)
        return self._get_response(
            f"{self.url}/package_show",
            params={"id": package_id},
        )

    def get_resources_for_package_id(self, package_id: str) -> dict[str, list[dict]] | None:
        """Retrieves resources associated with a given package ID.

        Args:
            package_id: The ID of the package for which to retrieve resources.

        Returns:
            A dictionary containing the resources associated with the package ID,
            or None if no resources are found or if the package ID is invalid.
        """
        data = self.get_info_for_package_id(package_id)
        if data:
            all_results = [data]
            result = self._fetch_packages_and_datasets(all_results)
            if result:
                return result
            else:
                return None
        else:
            return None
