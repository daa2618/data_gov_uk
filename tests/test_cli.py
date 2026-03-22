from __future__ import annotations

from unittest.mock import patch

import pytest

from data_gov_uk.cli import _build_parser, main


class TestParser:
    def test_search_orgs(self):
        parser = _build_parser()
        args = parser.parse_args(["search-orgs", "transport"])
        assert args.command == "search-orgs"
        assert args.query == "transport"

    def test_search_packages(self):
        parser = _build_parser()
        args = parser.parse_args(["search-packages", "traffic"])
        assert args.command == "search-packages"
        assert args.query == "traffic"

    def test_get_org(self):
        parser = _build_parser()
        args = parser.parse_args(["get-org", "nhs", "--datasets"])
        assert args.command == "get-org"
        assert args.name == "nhs"
        assert args.datasets is True

    def test_get_package(self):
        parser = _build_parser()
        args = parser.parse_args(["get-package", "air-quality"])
        assert args.command == "get-package"
        assert args.id == "air-quality"

    def test_get_resources(self):
        parser = _build_parser()
        args = parser.parse_args(["get-resources", "pkg-1"])
        assert args.command == "get-resources"
        assert args.id == "pkg-1"

    def test_no_command_exits(self):
        parser = _build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])


class TestMain:
    @patch("data_gov_uk.cli.DataGovUk")
    def test_search_orgs(self, MockClient, capsys):
        mock_client = MockClient.return_value.__enter__.return_value
        mock_client.search_available_organizations.return_value = ["org-a", "org-b"]
        ret = main(["search-orgs", "test"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "org-a" in out
        assert "org-b" in out

    @patch("data_gov_uk.cli.DataGovUk")
    def test_search_packages(self, MockClient, capsys):
        mock_client = MockClient.return_value.__enter__.return_value
        mock_client.search_available_packages.return_value = ["pkg-1"]
        ret = main(["search-packages", "data"])
        assert ret == 0
        assert "pkg-1" in capsys.readouterr().out

    @patch("data_gov_uk.cli.DataGovUk")
    def test_get_org(self, MockClient, capsys):
        mock_client = MockClient.return_value.__enter__.return_value
        mock_client.get_organization_info.return_value = {"title": "NHS"}
        ret = main(["get-org", "nhs"])
        assert ret == 0
        assert "NHS" in capsys.readouterr().out

    @patch("data_gov_uk.cli.DataGovUk")
    def test_get_package(self, MockClient, capsys):
        mock_client = MockClient.return_value.__enter__.return_value
        mock_client.get_info_for_package_id.return_value = {"name": "pkg"}
        ret = main(["get-package", "pkg"])
        assert ret == 0
        assert "pkg" in capsys.readouterr().out

    @patch("data_gov_uk.cli.DataGovUk")
    def test_get_resources(self, MockClient, capsys):
        mock_client = MockClient.return_value.__enter__.return_value
        mock_client.get_resources_for_package_id.return_value = {"pkg": []}
        ret = main(["get-resources", "pkg"])
        assert ret == 0

    @patch("data_gov_uk.cli.DataGovUk")
    def test_not_found_returns_1(self, MockClient, capsys):
        from data_gov_uk.exceptions import OrganizationNotFound

        mock_client = MockClient.return_value.__enter__.return_value
        mock_client.search_available_organizations.side_effect = OrganizationNotFound("nope")
        ret = main(["search-orgs", "zzz"])
        assert ret == 1
        assert "nope" in capsys.readouterr().err
