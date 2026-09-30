from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "raw_data_manifest.csv"

SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".json",
    ".zip",
    ".txt",
    ".psv",
}


def count_csv_rows(path):
    try:
        with path.open(
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:
            count = sum(
                1
                for _ in file
            )

        return max(
            count - 1,
            0
        )

    except Exception:
        return None


def classify(path):
    parts = {
        part.lower()
        for part in path.parts
    }

    if "car_listings" in parts:
        return "Car Listings"

    if "vehicle_specs" in parts:
        return "Vehicle Specifications"

    if "locations" in parts:
        return "Location Reference"

    if "economic" in parts:
        return "Economic"

    return "Other"


def main():
    records = []

    for path in RAW_DIR.rglob("*"):
        if not path.is_file():
            continue

        if path.name == OUTPUT_FILE.name:
            continue

        if (
            path.suffix.lower()
            not in SUPPORTED_EXTENSIONS
        ):
            continue

        stat = path.stat()

        records.append({
            "DatasetType": classify(path),
            "Filename": path.name,
            "RelativePath": str(
                path.relative_to(
                    PROJECT_ROOT
                )
            ),
            "FileExtension": (
                path.suffix.lower()
            ),
            "FileSizeMB": round(
                stat.st_size
                / (1024 * 1024),
                2
            ),
            "RowCount": (
                count_csv_rows(path)
                if path.suffix.lower()
                == ".csv"
                else None
            ),
            "ModifiedAtUtc": (
                datetime.fromtimestamp(
                    stat.st_mtime,
                    tz=timezone.utc
                ).isoformat()
            ),
            "Status": "Received",
        })

    manifest = pd.DataFrame(
        records
    )

    if not manifest.empty:
        manifest = manifest.sort_values(
            [
                "DatasetType",
                "Filename"
            ]
        )

    manifest.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Manifest created: {OUTPUT_FILE}"
    )

    print(
        f"Datasets recorded: "
        f"{len(manifest)}"
    )


if __name__ == "__main__":
    main()
