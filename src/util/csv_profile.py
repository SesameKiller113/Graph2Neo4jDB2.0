"""Pre-import CSV profiling for Graph2Neo4jDB.

This module gives users a quick readiness report before they map CSV files into
Neo4j nodes. It is intentionally dependency-light so it can run in CI, in a
terminal, or before the PyQt import flow.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class CsvFileProfile:
    path: str
    row_count: int
    columns: list[str]
    empty_cells: dict[str, int]


@dataclass
class CsvFolderProfile:
    folder: str
    file_count: int
    total_rows: int
    common_columns: list[str]
    all_columns: list[str]
    missing_columns_by_file: dict[str, list[str]]
    extra_columns_by_file: dict[str, list[str]]
    duplicate_keys: dict[str, int]
    files: list[CsvFileProfile]
    warnings: list[str]

    @property
    def is_ready(self) -> bool:
        return not self.warnings


def find_csv_files(folder: Path) -> list[Path]:
    return sorted(path for path in folder.rglob("*.csv") if path.is_file())


def _normalize_cell(value: str | None) -> str:
    return "" if value is None else value.strip()


def _profile_file(path: Path) -> CsvFileProfile:
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = list(reader.fieldnames or [])
        empty_cells: dict[str, int] = defaultdict(int)
        row_count = 0

        for row in reader:
            row_count += 1
            for column in columns:
                if _normalize_cell(row.get(column)) == "":
                    empty_cells[column] += 1

    return CsvFileProfile(
        path=str(path),
        row_count=row_count,
        columns=columns,
        empty_cells=dict(sorted(empty_cells.items())),
    )


def _iter_key_values(csv_files: Iterable[Path], key_columns: list[str]) -> Iterable[str]:
    for path in csv_files:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                yield "|".join(_normalize_cell(row.get(column)) for column in key_columns)


def profile_csv_folder(folder: str | Path, key_columns: list[str] | None = None) -> CsvFolderProfile:
    folder_path = Path(folder).expanduser().resolve()
    csv_files = find_csv_files(folder_path)
    key_columns = key_columns or []
    warnings: list[str] = []

    if not folder_path.exists():
        warnings.append(f"Folder does not exist: {folder_path}")
        return CsvFolderProfile(str(folder_path), 0, 0, [], [], {}, {}, {}, [], warnings)

    if not csv_files:
        warnings.append(f"No CSV files found under: {folder_path}")
        return CsvFolderProfile(str(folder_path), 0, 0, [], [], {}, {}, {}, [], warnings)

    file_profiles = [_profile_file(path) for path in csv_files]
    column_sets = [set(profile.columns) for profile in file_profiles]
    common_columns = sorted(set.intersection(*column_sets)) if column_sets else []
    all_columns = sorted(set.union(*column_sets)) if column_sets else []

    missing_columns_by_file = {
        profile.path: sorted(set(all_columns) - set(profile.columns))
        for profile in file_profiles
        if set(profile.columns) != set(all_columns)
    }
    extra_columns_by_file = {
        profile.path: sorted(set(profile.columns) - set(common_columns))
        for profile in file_profiles
        if set(profile.columns) != set(common_columns)
    }

    if missing_columns_by_file:
        warnings.append("CSV files do not share the same schema.")

    missing_key_columns = [column for column in key_columns if column not in common_columns]
    if missing_key_columns:
        warnings.append(f"Key columns missing from at least one file: {', '.join(missing_key_columns)}")

    duplicate_keys: dict[str, int] = {}
    if key_columns and not missing_key_columns:
        key_counts = Counter(_iter_key_values(csv_files, key_columns))
        duplicate_keys = {
            key: count
            for key, count in sorted(key_counts.items())
            if key and count > 1
        }
        if duplicate_keys:
            warnings.append("Duplicate merge keys detected across the CSV folder.")

    empty_files = [profile.path for profile in file_profiles if profile.row_count == 0]
    if empty_files:
        warnings.append(f"Empty CSV files detected: {len(empty_files)}")

    return CsvFolderProfile(
        folder=str(folder_path),
        file_count=len(csv_files),
        total_rows=sum(profile.row_count for profile in file_profiles),
        common_columns=common_columns,
        all_columns=all_columns,
        missing_columns_by_file=missing_columns_by_file,
        extra_columns_by_file=extra_columns_by_file,
        duplicate_keys=duplicate_keys,
        files=file_profiles,
        warnings=warnings,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Profile CSV readiness before importing into Neo4j.")
    parser.add_argument("folder", help="Folder containing CSV files for one Neo4j node label.")
    parser.add_argument(
        "--key",
        action="append",
        default=[],
        help="Column used as a merge key. Pass multiple --key values for composite keys.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 when schema, empty-file, or duplicate-key warnings are found.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    profile = profile_csv_folder(args.folder, args.key)
    print(json.dumps(asdict(profile), indent=2, ensure_ascii=False))
    return 1 if args.strict and not profile.is_ready else 0


if __name__ == "__main__":
    raise SystemExit(main())
