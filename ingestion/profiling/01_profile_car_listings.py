from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "car_listings"
    / "Australian Vehicle Prices.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "profiling"
    / "car_listings"
)


def clean_currency_for_profile(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip(),
        errors="coerce"
    )


def clean_km_for_profile(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("km", "", regex=False)
        .str.strip(),
        errors="coerce"
    )


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Add the primary dataset here:\n{INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df = pd.read_csv(
        INPUT_FILE,
        low_memory=False
    )

    rows, columns = df.shape

    duplicate_count = int(
        df.duplicated().sum()
    )

    duplicate_pct = (
        duplicate_count / rows * 100
        if rows
        else 0
    )

    column_profile = pd.DataFrame({
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
                df[c].isna().mean() * 100,
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

    column_profile.to_csv(
        OUTPUT_DIR / "columns.csv",
        index=False
    )

    column_profile[
        [
            "ColumnName",
            "NullCount",
            "NullPercentage"
        ]
    ].rename(
        columns={
            "NullCount": "MissingCount",
            "NullPercentage": "MissingPercentage",
        }
    ).sort_values(
        "MissingPercentage",
        ascending=False
    ).to_csv(
        OUTPUT_DIR / "missing_values.csv",
        index=False
    )

    numeric_columns = (
        df.select_dtypes(
            include="number"
        ).columns
    )

    if len(numeric_columns):
        (
            df[numeric_columns]
            .describe()
            .transpose()
            .to_csv(
                OUTPUT_DIR
                / "numeric_profile.csv"
            )
        )

    categorical_rows = []

    for col in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        counts = df[col].value_counts(
            dropna=True
        )

        categorical_rows.append({
            "ColumnName": col,
            "UniqueCount": int(
                df[col].nunique(
                    dropna=True
                )
            ),
            "MostCommonValue": (
                str(counts.index[0])
                if len(counts)
                else None
            ),
            "MostCommonCount": (
                int(counts.iloc[0])
                if len(counts)
                else 0
            ),
        })

    pd.DataFrame(
        categorical_rows
    ).to_csv(
        OUTPUT_DIR
        / "categorical_profile.csv",
        index=False
    )

    summary = [
        "Australian Vehicle Prices - Phase 1 Profiling",
        "=" * 55,
        f"Rows: {rows:,}",
        f"Columns: {columns}",
        f"Duplicate rows: {duplicate_count:,}",
        f"Duplicate percentage: {duplicate_pct:.2f}%",
    ]

    domain_checks = {
        "Brand": "Unique brands",
        "Model": "Unique models",
        "Location": "Unique locations",
        "FuelType": "Unique fuel types",
        "Transmission": "Unique transmissions",
        "BodyType": "Unique body types",
    }

    for col, label in domain_checks.items():
        if col in df.columns:
            summary.append(
                f"{label}: "
                f"{df[col].nunique(dropna=True):,}"
            )

    if "Year" in df.columns:
        year = pd.to_numeric(
            df["Year"],
            errors="coerce"
        )

        summary.extend([
            f"Year minimum: {year.min()}",
            f"Year maximum: {year.max()}",
        ])

    if "Price" in df.columns:
        price = clean_currency_for_profile(
            df["Price"]
        )

        summary.extend([
            f"Valid numeric prices: {price.notna().sum():,}",
            f"Price minimum: {price.min()}",
            f"Price median: {price.median()}",
            f"Price maximum: {price.max()}",
        ])

    if "Kilometres" in df.columns:
        km = clean_km_for_profile(
            df["Kilometres"]
        )

        summary.extend([
            f"Valid numeric kilometres: {km.notna().sum():,}",
            f"Kilometres minimum: {km.min()}",
            f"Kilometres median: {km.median()}",
            f"Kilometres maximum: {km.max()}",
        ])

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
