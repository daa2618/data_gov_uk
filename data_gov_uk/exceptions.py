from __future__ import annotations


class OrganizationNotFound(Exception):
    """Raised when an organization cannot be found on data.gov.uk."""


class PackageNotFound(Exception):
    """Raised when a package/dataset cannot be found on data.gov.uk."""
