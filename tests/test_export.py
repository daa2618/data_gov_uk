from __future__ import annotations

import csv
import json

import pytest

from data_gov_uk.export import export_resources_to_csv, export_resources_to_json


@pytest.fixture
def sample_resources():
    return {
        "traffic-data": [
            {
                "description": "2024 data",
                "file_format": "CSV",
                "file_id": "1",
                "mime_type": "text/csv",
                "name": "traffic.csv",
                "package_id": "traffic-data",
                "resource_type": "file",
                "created_at": "2024-01-01",
                "file_url": "https://example.com/traffic.csv",
            },
        ],
        "air-quality": [
            {
                "description": "AQ index",
                "file_format": "JSON",
                "file_id": "2",
                "mime_type": "application/json",
                "name": "aq.json",
                "package_id": "air-quality",
                "resource_type": "api",
                "created_at": "2024-06-01",
                "file_url": "https://example.com/aq.json",
            },
        ],
    }


class TestExportJson:
    def test_writes_valid_json(self, tmp_path, sample_resources):
        out = tmp_path / "out.json"
        result = export_resources_to_json(sample_resources, out)
        assert result.exists()
        data = json.loads(out.read_text())
        assert "traffic-data" in data
        assert len(data["air-quality"]) == 1

    def test_empty_resources(self, tmp_path):
        out = tmp_path / "empty.json"
        export_resources_to_json({}, out)
        assert json.loads(out.read_text()) == {}


class TestExportCsv:
    def test_writes_valid_csv(self, tmp_path, sample_resources):
        out = tmp_path / "out.csv"
        result = export_resources_to_csv(sample_resources, out)
        assert result.exists()
        with open(out) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["package_name"] == "traffic-data"
        assert rows[1]["package_name"] == "air-quality"

    def test_empty_resources(self, tmp_path):
        out = tmp_path / "empty.csv"
        export_resources_to_csv({}, out)
        assert out.read_text() == ""

    def test_has_header_row(self, tmp_path, sample_resources):
        out = tmp_path / "header.csv"
        export_resources_to_csv(sample_resources, out)
        first_line = out.read_text().splitlines()[0]
        assert "package_name" in first_line
        assert "file_format" in first_line
