from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "reports"
    / "eda"
    / "data_quality"
    / "used_car_eda_snapshot.csv"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "eda"
    / "univariate"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    print("\nLoading EDA snapshot...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows loaded    : {len(df):,}")
    print(f"Columns loaded : {len(df.columns):,}")

    return df


def create_numeric_summary(df: pd.DataFrame) -> pd.DataFrame:

    columns = [
        "ListingPrice",
        "Kilometres",
        "ModelYear",
        "FuelConsumptionLPer100Km",
        "CylinderCount",
        "Doors",
        "Seats",
    ]

    rows = []

    for column in columns:

        series = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        rows.append(
            {
                "Variable": column,
                "Count": series.count(),
                "Missing": series.isna().sum(),
                "Mean": series.mean(),
                "Median": series.median(),
                "StdDev": series.std(),
                "Min": series.min(),
                "Q1": series.quantile(0.25),
                "Q3": series.quantile(0.75),
                "Max": series.max(),
                "Skewness": series.skew(),
            }
        )

    result = pd.DataFrame(rows)

    print("\nNUMERIC UNIVARIATE SUMMARY")
    print("-" * 80)
    print(result.to_string(index=False))

    result.to_csv(
        REPORT_DIR / "numeric_univariate_summary.csv",
        index=False,
    )

    return result


def plot_histogram(
    df: pd.DataFrame,
    column: str,
    bins: int = 40,
) -> None:

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()

    plt.figure(figsize=(10, 6))

    plt.hist(
        values,
        bins=bins,
        edgecolor="black",
    )

    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Number of Listings")
    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / f"{column}_histogram.png",
        dpi=150,
    )

    plt.close()


def plot_boxplot(
    df: pd.DataFrame,
    column: str,
) -> None:

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()

    plt.figure(figsize=(10, 4))

    plt.boxplot(
        values,
        vert=False,
    )

    plt.title(f"Boxplot of {column}")
    plt.xlabel(column)
    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / f"{column}_boxplot.png",
        dpi=150,
    )

    plt.close()


def analyse_model_year(df: pd.DataFrame) -> None:

    counts = (
        df["ModelYear"]
        .value_counts()
        .sort_index()
    )

    counts.rename(
        "ListingCount"
    ).to_csv(
        REPORT_DIR / "model_year_counts.csv"
    )

    plt.figure(figsize=(12, 6))

    plt.bar(
        counts.index.astype(str),
        counts.values,
    )

    plt.title("Used Car Listings by Model Year")
    plt.xlabel("Model Year")
    plt.ylabel("Number of Listings")

    plt.xticks(
        rotation=90,
        fontsize=7,
    )

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "model_year_distribution.png",
        dpi=150,
    )

    plt.close()


def analyse_categorical_variable(
    df: pd.DataFrame,
    column: str,
    top_n: int = 20,
) -> None:

    counts = (
        df[column]
        .fillna("Missing")
        .value_counts()
        .rename_axis(column)
        .reset_index(name="ListingCount")
    )

    counts["Percentage"] = (
        counts["ListingCount"]
        / len(df)
        * 100
    ).round(2)

    counts.to_csv(
        REPORT_DIR / f"{column}_frequency.csv",
        index=False,
    )

    top = counts.head(top_n)

    plt.figure(figsize=(11, 6))

    plt.bar(
        top[column].astype(str),
        top["ListingCount"],
    )

    plt.title(
        f"Top {min(top_n, len(top))} {column} Categories"
    )

    plt.xlabel(column)
    plt.ylabel("Number of Listings")

    plt.xticks(
        rotation=45,
        ha="right",
    )

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / f"{column}_frequency.png",
        dpi=150,
    )

    plt.close()


def analyse_price_bands(df: pd.DataFrame) -> None:

    price = pd.to_numeric(
        df["ListingPrice"],
        errors="coerce",
    )

    bins = [
        0,
        10_000,
        20_000,
        30_000,
        40_000,
        50_000,
        75_000,
        100_000,
        200_000,
        float("inf"),
    ]

    labels = [
        "<10k",
        "10k-20k",
        "20k-30k",
        "30k-40k",
        "40k-50k",
        "50k-75k",
        "75k-100k",
        "100k-200k",
        "200k+",
    ]

    price_band = pd.cut(
        price,
        bins=bins,
        labels=labels,
        right=False,
    )

    counts = (
        price_band
        .value_counts(sort=False)
        .rename_axis("PriceBand")
        .reset_index(name="ListingCount")
    )

    counts.to_csv(
        REPORT_DIR / "price_band_distribution.csv",
        index=False,
    )

    print("\nPRICE BANDS")
    print("-" * 80)
    print(counts.to_string(index=False))


def main():

    print("\n" + "=" * 80)
    print("STEP 3.2 - UNIVARIATE ANALYSIS")
    print("=" * 80)

    df = load_data()

    create_numeric_summary(df)

    numeric_columns = [
        "ListingPrice",
        "Kilometres",
        "FuelConsumptionLPer100Km",
        "CylinderCount",
        "Doors",
        "Seats",
    ]

    print("\nGenerating numeric plots...")

    for column in numeric_columns:
        plot_histogram(df, column)
        plot_boxplot(df, column)

    analyse_model_year(df)

    categorical_columns = [
        "MakeName",
        "ModelName",
        "BodyType",
        "Transmission",
        "FuelType",
        "DriveType",
    ]

    print("Generating categorical plots...")

    for column in categorical_columns:
        analyse_categorical_variable(
            df,
            column,
        )

    analyse_price_bands(df)

    print("\n" + "=" * 80)
    print("STEP 3.2 UNIVARIATE ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()