from __future__ import annotations

from data_gov_uk.models import Package, Resource


class TestResource:
    def test_create(self):
        r = Resource(
            description="test",
            file_format="CSV",
            file_id="abc-123",
            mime_type="text/csv",
            name="data.csv",
            package_id="pkg-1",
            resource_type="file",
            created_at="2024-01-01",
            file_url="https://example.com/data.csv",
        )
        assert r.file_id == "abc-123"
        assert r.file_format == "CSV"

    def test_to_dict(self):
        r = Resource(
            description=None,
            file_format="JSON",
            file_id="xyz",
            mime_type=None,
            name="api.json",
            package_id="pkg-2",
            resource_type=None,
            created_at=None,
            file_url="https://example.com/api.json",
        )
        d = r.to_dict()
        assert isinstance(d, dict)
        assert d["file_id"] == "xyz"
        assert d["description"] is None

    def test_optional_fields_none(self):
        r = Resource(
            description=None,
            file_format=None,
            file_id="id",
            mime_type=None,
            name=None,
            package_id="pkg",
            resource_type=None,
            created_at=None,
            file_url=None,
        )
        assert r.file_id == "id"


class TestPackage:
    def test_create_minimal(self):
        p = Package(name="my-package")
        assert p.name == "my-package"
        assert p.title is None
        assert p.resources is None

    def test_create_with_resources(self):
        r = Resource(
            description="d",
            file_format="CSV",
            file_id="1",
            mime_type="text/csv",
            name="f.csv",
            package_id="pkg",
            resource_type="file",
            created_at="2024-01-01",
            file_url="https://example.com/f.csv",
        )
        p = Package(name="pkg", title="My Package", resources=[r])
        assert len(p.resources) == 1

    def test_to_dict(self):
        p = Package(name="pkg", title="Title")
        d = p.to_dict()
        assert d["name"] == "pkg"
        assert d["title"] == "Title"
