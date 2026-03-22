from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Resource:
    """A single downloadable resource within a package."""

    description: str | None
    file_format: str | None
    file_id: str
    mime_type: str | None
    name: str | None
    package_id: str
    resource_type: str | None
    created_at: str | None
    file_url: str | None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Package:
    """Metadata for a CKAN dataset package."""

    name: str
    title: str | None = None
    resources: list[Resource] | None = None

    def to_dict(self) -> dict:
        return asdict(self)
