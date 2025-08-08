import pandas as pd
from pathlib import Path
pardir = Path(__file__).resolve().parent
import sys
if str(pardir) not in sys.path:
    sys.path.insert(0, str(pardir))
    
from utils.response import Response 
from utils.logging_helper import BasicLogger 
_bl = BasicLogger(verbose = False, log_directory=None,logger_name="DATA_GOV_UK")
from utils.strings_and_lists import ListOperations 
from exceptions import OrganizationNotFound, PackageNotFound



class DataGovUk:
    """
    This class provides methods for interacting with the Data.gov.uk API.
    """
    def __init__(self):
        """
        Initializes the DataGovUk class with the base API URL.

        Attributes:
            url (str): The base URL for the Data.gov.uk API.
            _all_packages (list, optional): Cached list of all available datasets. Defaults to None.
            _all_organizations (list, optional): Cached list of all available organizations. Defaults to None.
        """
        self.url = "https://data.gov.uk/api/3/action"
        self._all_packages = None
        self._all_organizations = None
    
    def _get_response(self, url, **kwargs):
        """
        Fetches data from a provided URL and handles error responses.

        Args:
            url (str): The URL to fetch data from.
        **kwargs: Additional arguments to be passed to the request object.

        Returns:
            dict: The parsed JSON response from the API, or None if an error occurs.
        """
        response=Response(url, **kwargs).get_json_from_response()
        if response:
            if response.get("success"):
                return response.get("result")
            else:
                error = response.get("error")
                msg = error.get("__type") + " : " + error.get("message")
                _bl.error(msg)
                return None
            
    
    @property
    def ALL_PACKAGES(self) -> list:
        """
        Retrieves the list of all available datasets on Data.gov.uk.

        Returns:
            list: A list containing information about all datasets.
        """

        if self._all_packages is None:
            dataset_url = f"{self.url}/package_list"
            self._all_packages=self._get_response(dataset_url)
        return self._all_packages
    
    @property
    def ALL_ORGANIZATIONS(self) -> list:
        """Retrieves a list of all organizations.

        This method retrieves a list of all organizations from the API.  The result is cached 
        for subsequent calls to avoid redundant API requests.

        Returns:
            list: A list of organizations. Returns the cached result if it exists, otherwise fetches 
                it from the API using the URL constructed from `self.url`.  Returns an empty list if the API call fails (or other errors occur).

        """
        if self._all_organizations is None:
            orgUrl = f"{self.url}/organization_list"
            self._all_organizations=self._get_response(orgUrl)
        return self._all_organizations
    
    def _assert_organization_exists(self, organization:str):
        if organization not in self.ALL_ORGANIZATIONS:
            raise OrganizationNotFound(f"No organization named '{organization}' was found")
    
    def _assert_package_exists(self, package_id:str):
        if package_id not in self.ALL_PACKAGES:
            raise PackageNotFound(f"No package with ID '{package_id}' was found")

        
    def filter_dataset_for_organization(self, organization:str) -> dict:
        """Filters a dataset to include only packages from a specified organization.

        Args:
            organization: The name of the organization to filter by.

        Returns:
            A dictionary containing the search results.  The exact structure of this 
            dictionary depends on the API response.  Raises an exception if the 
            organization does not exist.

        Raises:
            Exception: If the specified organization does not exist.  The specific 
                    exception type may vary depending on the underlying error.
        """
        self._assert_organization_exists(organization)
        search_url = f"{self.url}/package_search?fq=organization:{organization}"
        return self._get_response(search_url)
    
    def get_organization_info(self, organization:str, show_datasets:bool=False) -> dict:
        """Retrieves information about a specific organization.

        Args:
            organization: The ID or name of the organization.
            show_datasets: If True, includes dataset information in the response. Defaults to False.

        Returns:
            A dictionary containing the organization's information.  The specific keys and values 
            will depend on the API response.  Returns an empty dictionary if the organization 
            is not found or if an error occurs during the API call.

        Raises:
            Exception: If the organization does not exist (based on internal assertion).  
                    The specific exception type will depend on how `_assert_organization_exists` is implemented.

        """
        self._assert_organization_exists(organization)
        search_url = f"{self.url}/organization_show?id={organization}&include_datasets={show_datasets}"
        return self._get_response(search_url)
    
    def _search_list_by_string(self, search_list:list, search_string:str):
        list_ops = ListOperations(search_list, search_string = search_string)
                                  
        filtered=list_ops.search_list_by_snowball()
        if filtered:
            return filtered
        else:
            filtered = list_ops.search_list_by_string_for_metric(0.5)
            if filtered:
                return filtered
            else:
                return None
            
    def search_available_organizations(self, organization:str) ->list:
        """Searches for organizations matching a given string.

        Args:
            organization: The string to search for within organization names.

        Returns:
            A list of organizations whose names contain the search string.  Returns an empty list if no matches are found.

        Raises:
            OrganizationNotFound: If no organizations match the search string.
        """
        filtered=self._search_list_by_string(self.ALL_ORGANIZATIONS, organization)
        if filtered:
            return filtered
        else:
            raise OrganizationNotFound("No matching organizations could be found")
    
    def search_available_packages(self, package_name:str) -> list:
        """Searches for available packages matching a given name.

        Args:
            package_name: The name of the package to search for (case-insensitive).

        Returns:
            A list of packages whose names match the input `package_name`.  Returns an empty list if no matches are found.

        Raises:
            PackageNotFound: If no packages matching the provided name are found in the database.
        """

        filtered=self._search_list_by_string(self.ALL_PACKAGES, package_name)
        if filtered:
            return filtered
        else:
            raise PackageNotFound("No matching packages could be found")

    
    
    def _fetch_packages_and_datasets(self, all_results:list):
        """Fetches and organizes packages and datasets from a list of results.

        This function processes a list of results from the API call 
        to extract package and dataset information. It organizes the data into a 
        dictionary where keys are package names and values are lists of dataset 
        details.  The dataset details are sorted by creation date (descending).

        Args:
            all_results: A list of dictionaries, where each dictionary represents a 
                        package and contains a "resources" key with a list of dataset
                        dictionaries. Each dataset dictionary should contain keys like
                        "description", "format", "id", "mimetype", "name", "package_id",
                        "resource_type", "created", and "url".

        Yields:
            dict: A dictionary where keys are package names and values are lists of 
                dictionaries. Each inner dictionary represents a dataset and contains 
                its metadata.  The datasets within each package list are sorted by 
                their creation date (most recent first).  Handles potential errors 
                during sorting gracefully.
        """
        data_dict={result.get("name") : [
                            dict(
                                description=x.get("description"),
                                file_format=x.get("format"),
                                file_id = x.get("id"),
                                mime_type=x.get("mimetype"),
                                name=x.get("name"),
                                package_id=x.get("package_id"),
                                resource_type=x.get("resource_type"),
                                created_at=x.get("created"),
                                file_url = x.get("url")
                                ) for x in result.get("resources")
                        ] for result in all_results}
        sorted_out = {}
        for key,files_list in data_dict.items():
            try:
                files_list.sort(key=lambda x: x.get("created_at"),
                                reverse=True)
            except:
                pass
            sorted_out[key]=files_list
        yield sorted_out
        
    def _get_packages_from_organization_for_under_1000(self, organization:str) -> dict:
        """Retrieves packages from a given organization if the number of datasets is less than or equal to 1000.

        This function filters the dataset for a specific organization and retrieves package information only if 
        the number of datasets associated with that organization is between 1 and 1000 (inclusive).  It uses a 
        search URL to fetch the relevant package data.  If the number of datasets exceeds 1000, a message is printed 
        and None is returned.

        Args:
            organization (str): The name of the organization to search for.

        Returns:
            dict: A dictionary containing the fetched packages and datasets, or None if no packages are found or 
                if the number of datasets exceeds 1000.  The structure of the dictionary is determined by 
                the `_fetch_packages_and_datasets` method.

        """
        data = self.filter_dataset_for_organization(organization)
        search_url = f"{self.url}/package_search?fq=organization:{organization}"
        n_datasets = data.get("count")
        if n_datasets > 0 and n_datasets <=1000:
            params = dict(rows=str(n_datasets))
            results = self._get_response(search_url, params=params)
            if results:
                all_results = results.get("results")
                return self._fetch_packages_and_datasets(all_results)
            else:
                return None
        else:
            _bl.warning("More than 1000 datasets are found.Returning None")
            return None
    
    def _get_all_packages_and_datasets_for_organization(self, organization:str, n_results_to_fetch_per_request:int = 100):
        """Retrieves all packages and datasets for a given organization.

        This function iteratively fetches package information from a remote API,
        handling pagination to retrieve all packages associated with a specified organization.
        It then retrieves the datasets associated with each package.

        Args:
            organization (str): The name of the organization.
            n_results_to_fetch_per_request (int, optional): The number of results to fetch per API request. Defaults to 100.

        Yields:
            dict: A dictionary where keys are package names and values are lists of associated datasets.  Yields a single dictionary containing all data at the end of iteration.

        Notes:
            - This function uses pagination to handle large numbers of packages.
            - It prints progress updates during the retrieval process.
            - The underlying API calls are handled by `self.get_organization_info` and `self._get_response`.
            - `self._fetch_packages_and_datasets` processes individual package results to extract dataset information.

        """
        org_info = self.get_organization_info(organization)
        n_packages = org_info.get("package_count")
        _bl.info(f"Total Number of Packages(Topics) With the Organization '{organization}' : {n_packages}\n")
        
        
        n_requests = n_packages // n_results_to_fetch_per_request
        all_packages_and_datasets = {}

        start = 0

        search_url = f"{self.url}/package_search?fq=organization:{organization}"
        _bl.info("-"*100)
        for a in range(n_requests+1):
            params = dict(start=str(start),
                    rows=str(n_results_to_fetch_per_request))
            
            result = self._get_response(search_url, params=params)
            _bl.info(f"\tRequest Count: {a}")
            _bl.info(f"\tPackages(Topics) obtained so far: {len(all_packages_and_datasets)}")
            #_bl.info(params)
            if result:
                datasets = result.get("results")
                res = list(self._fetch_packages_and_datasets(datasets))
                if res:
                    all_packages_and_datasets.update(res[0])
                start += n_results_to_fetch_per_request
        
        _bl.info("-"*100)
        _bl.info(f"Total Packages obtained: {len(all_packages_and_datasets)}")
        _bl.info(f"Total Datasets for Organization: {sum([len(value) for key,value in all_packages_and_datasets.items()])}")
        _bl.info("-"*100)
        yield all_packages_and_datasets

    
    def get_info_for_package_id(self, package_id:str):
        """Retrieves information for a given package ID.

        Args:
            package_id: The ID of the package to retrieve information for.

        Returns:
            A response object containing the package information.  The specific format 
            of this object depends on the underlying `_get_response` method.  
            Raises an exception if the package does not exist.

        Raises:
            Exception: If the package with the given ID does not exist.  The specific 
                    exception type depends on the implementation of `_assert_package_exists`.
        """
        self._assert_package_exists(package_id)
        search_url = f"{self.url}/package_show?id={package_id}"
        return self._get_response(search_url)
    
    def get_resources_for_package_id(self, package_id:str):
        """Retrieves resources associated with a given package ID.

        Args:
            package_id: The ID of the package for which to retrieve resources.

        Returns:
            A dictionary containing the resources associated with the package ID, 
            or None if no resources are found or if the package ID is invalid.  
            The exact structure of the returned dictionary depends on the 
            `_fetch_packages_and_datasets` method.
        """
        data = self.get_info_for_package_id(package_id)
        if data:
            all_results = [data]
            result=list(self._fetch_packages_and_datasets(all_results))
            if result:
                return result[0]
            else:
                return None
        else:
            return None
        
    


    
    
                
    
    
    
    
        
    
    
    
    