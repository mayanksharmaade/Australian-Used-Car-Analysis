from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "locations"
    / "australian_postcodes.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "profiling"
    / "locations"
)


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Add location source here:\n{INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False
    )

    normalized = {
        str(c).lower().strip(): c
        for c in df.columns
    }

    profile = pd.DataFrame({
        "ColumnName": df.columns,
        "DataType": [
            str(df[c].dtype)
            for c in df.columns
        ],
        "NonNullCount": [
            int(df[c].notna().sum())
            for c in df.columns
        ],
        "NullCount": [
            int(df[c].isna().sum())
            for c in df.columns
        ],
        "NullPercentage": [
            round(
                df[c].isna().mean()
                * 100,
                2
            )
            for c in df.columns
        ],
        "UniqueCount": [
            int(
                df[c].nunique(
                    dropna=True
                )
            )
            for c in df.columns
        ],
    })

    profile.to_csv(
        OUTPUT_DIR / "columns.csv",
        index=False
    )

    exact_duplicates = int(
        df.duplicated().sum()
    )

    key_fields = [
        "locality",
        "state",
        "postcode"
    ]

    if all(
        field in normalized
        for field in key_fields
    ):
        key_columns = [
            normalized[field]
            for field in key_fields
        ]

        key_duplicates = int(
            df.duplicated(
                subset=key_columns
            ).sum()
        )
    else:
        key_duplicates = 0

    if "state" in normalized:
        state_col = normalized["state"]

        (
            df[state_col]
            .value_counts(
                dropna=False
            )
            .rename_axis("State")
            .reset_index(
                name="RowCount"
            )
            .to_csv(
                OUTPUT_DIR
                / "state_profile.csv",
                index=False
            )
        )

    invalid_latitude = 0
    invalid_longitude = 0

    if "latitude" in normalized:
        lat = pd.to_numeric(
            df[normalized["latitude"]],
            errors="coerce"
        )

        invalid_latitude = int(
            (
                lat.notna()
                & ~lat.between(
                    -44,
                    -10
                )
            ).sum()
        )

    if "longitude" in normalized:
        lon = pd.to_numeric(
            df[normalized["longitude"]],
            errors="coerce"
        )

        invalid_longitude = int(
            (
                lon.notna()
                & ~lon.between(
                    112,
                    154
                )
            ).sum()
        )

    summary = [
        "Australian Location Data - Phase 1 Profiling",
        "=" * 55,
        f"Rows: {len(df):,}",
        f"Columns: {len(df.columns)}",
        f"Exact duplicate rows: {exact_duplicates:,}",
        (
            "Duplicate locality/state/postcode keys: "
            f"{key_duplicates:,}"
        ),
        (
            "Invalid latitude rows: "
            f"{invalid_latitude:,}"
        ),
        (
            "Invalid longitude rows: "
            f"{invalid_longitude:,}"
        ),
    ]

    for field in [
        "state",
        "postcode",
        "locality"
    ]:
        if field in normalized:
            summary.append(
                f"Unique {field}: "
                f"{df[normalized[field]].nunique(dropna=True):,}"
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
