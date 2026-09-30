from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "vehicle_specs"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "profiling"
    / "vehicle_specs"
)


def normalize_header(value):
    return (
        str(value)
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


def main():
    files = sorted(
        INPUT_DIR.glob("*.csv")
    )

    if not files:
        raise FileNotFoundError(
            "No vehicle specification CSV files "
            f"found under:\n{INPUT_DIR}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    frames = []
    source_files = []

    for file in files:
        df = pd.read_csv(
            file,
            low_memory=False
        )

        df["_SourceFile"] = file.name

        frames.append(df)

        source_files.append({
            "Filename": file.name,
            "Rows": len(df),
            "Columns": len(df.columns),
        })

    combined = pd.concat(
        frames,
        ignore_index=True,
        sort=False
    )

    pd.DataFrame(
        source_files
    ).to_csv(
        OUTPUT_DIR / "source_files.csv",
        index=False
    )

    profile = pd.DataFrame({
        "ColumnName": combined.columns,
        "DataType": [
            str(combined[c].dtype)
            for c in combined.columns
        ],
        "NullCount": [
            int(combined[c].isna().sum())
            for c in combined.columns
        ],
        "NullPercentage": [
            round(
                combined[c].isna().mean()
                * 100,
                2
            )
            for c in combined.columns
        ],
        "UniqueCount": [
            int(
                combined[c].nunique(
                    dropna=True
                )
            )
            for c in combined.columns
        ],
    })

    profile.to_csv(
        OUTPUT_DIR / "columns.csv",
        index=False
    )

    normalized_headers = {
        normalize_header(c): c
        for c in combined.columns
    }

    candidate_groups = {
        "make": [
            "make",
            "manufacturer",
            "brand"
        ],
        "model": ["model"],
        "year": [
            "year",
            "modelyear"
        ],
        "variant": [
            "variant",
            "badge"
        ],
    }

    resolved = {}

    for target, candidates in (
        candidate_groups.items()
    ):
        for candidate in candidates:
            key = normalize_header(
                candidate
            )

            if key in normalized_headers:
                resolved[target] = (
                    normalized_headers[key]
                )
                break

    summary = [
        "Vehicle Specifications - Phase 1 Profiling",
        "=" * 55,
        f"Files: {len(files)}",
        f"Combined rows: {len(combined):,}",
        f"Combined columns: {len(combined.columns)}",
        (
            "Exact duplicate rows: "
            f"{combined.duplicated().sum():,}"
        ),
        (
            "Resolved candidate join fields: "
            f"{resolved}"
        ),
    ]

    key_columns = [
        resolved[k]
        for k in [
            "make",
            "model",
            "year",
            "variant"
        ]
        if k in resolved
    ]

    if len(key_columns) >= 3:
        duplicate_key_rows = int(
            combined.duplicated(
                subset=key_columns,
                keep=False
            ).sum()
        )

        summary.append(
            "Rows involved in duplicated "
            f"candidate keys {key_columns}: "
            f"{duplicate_key_rows:,}"
        )

    (
        OUTPUT_DIR
        / "summary.txt"
    ).write_text(
        "\n".join(summary),
        encoding="utf-8"
    )

    print("\n".join(summary))
    print(
        f"\nReports written to: "
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
