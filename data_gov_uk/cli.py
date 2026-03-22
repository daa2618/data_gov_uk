from __future__ import annotations

import argparse
import json
import sys

from .api import DataGovUk
from .exceptions import OrganizationNotFound, PackageNotFound


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="data-gov-uk",
        description="Query the data.gov.uk CKAN API from the command line.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # search-orgs
    p_so = sub.add_parser("search-orgs", help="Search for organisations by name")
    p_so.add_argument("query", help="Search string")

    # search-packages
    p_sp = sub.add_parser("search-packages", help="Search for packages by name")
    p_sp.add_argument("query", help="Search string")

    # get-org
    p_go = sub.add_parser("get-org", help="Get organisation info")
    p_go.add_argument("name", help="Organisation slug")
    p_go.add_argument("--datasets", action="store_true", help="Include datasets")

    # get-package
    p_gp = sub.add_parser("get-package", help="Get package info")
    p_gp.add_argument("id", help="Package ID")

    # get-resources
    p_gr = sub.add_parser("get-resources", help="Get resources for a package")
    p_gr.add_argument("id", help="Package ID")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        with DataGovUk() as client:
            if args.command == "search-orgs":
                results = client.search_available_organizations(args.query)
                for org in results:
                    print(org)

            elif args.command == "search-packages":
                results = client.search_available_packages(args.query)
                for pkg in results:
                    print(pkg)

            elif args.command == "get-org":
                info = client.get_organization_info(args.name, show_datasets=args.datasets)
                print(json.dumps(info, indent=2))

            elif args.command == "get-package":
                info = client.get_info_for_package_id(args.id)
                print(json.dumps(info, indent=2))

            elif args.command == "get-resources":
                resources = client.get_resources_for_package_id(args.id)
                print(json.dumps(resources, indent=2))

    except (OrganizationNotFound, PackageNotFound) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
