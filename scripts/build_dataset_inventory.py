from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = PROJECT_ROOT / "docs" / "dataset_inventory.csv"


def read_csv_metadata(path):
    try:
        df = pd.read_csv(
            path,
            low_memory=False
        )

        return (
            len(df),
            len(df.columns),
            ",".join(
                str(col)
                for col in df.columns
            ),
        )

    except Exception:
        return (
            None,
            None,
            None
        )


def main():
    records = []

    for path in RAW_DIR.rglob("*"):
        if not path.is_file():
            continue

        if path.name == (
            "raw_data_manifest.csv"
        ):
            continue

        row_count = None
        column_count = None
        columns = None

        if path.suffix.lower() == ".csv":
            (
                row_count,
                column_count,
                columns
            ) = read_csv_metadata(path)

        records.append({
            "Filename": path.name,
            "RelativePath": str(
                path.relative_to(
                    PROJECT_ROOT
                )
            ),
            "Rows": row_count,
            "Columns": column_count,
            "FileSizeMB": round(
                path.stat().st_size
                / (1024 * 1024),
                2
            ),
            "FileExtension": (
                path.suffix.lower()
            ),
            "CapturedAtUtc": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            "ColumnNames": columns,
            "Notes": "",
        })

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    pd.DataFrame(
        records
    ).to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Dataset inventory created: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
