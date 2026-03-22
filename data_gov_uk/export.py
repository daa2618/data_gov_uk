from __future__ import annotations

import csv
import json
from pathlib import Path


def export_resources_to_json(
    resources: dict[str, list[dict]],
    path: str | Path,
) -> Path:
    """Write resources dict to a JSON file.

    Args:
        resources: Dict mapping package names to lists of resource dicts.
        path: Output file path.

    Returns:
        The resolved output path.
    """
    path = Path(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(resources, f, indent=2, ensure_ascii=False)
    return path.resolve()


def export_resources_to_csv(
    resources: dict[str, list[dict]],
    path: str | Path,
) -> Path:
    """Flatten resources dict and write to a CSV file.

    Each row is one resource, with an extra ``package_name`` column derived
    from the dict key.

    Args:
        resources: Dict mapping package names to lists of resource dicts.
        path: Output file path.

    Returns:
        The resolved output path.
    """
    path = Path(path)
    rows: list[dict] = []
    for package_name, resource_list in resources.items():
        for res in resource_list:
            row = {"package_name": package_name, **res}
            rows.append(row)

    if not rows:
        path.write_text("", encoding="utf-8")
        return path.resolve()

    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path.resolve()
