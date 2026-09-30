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
    / "bivariate"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:

    print("\nLoading EDA snapshot...")

    df = pd.read_csv(INPUT_FILE)

    # Price is our ML target.
    # Rows without a valid target cannot contribute to
    # target-based bivariate analysis.
    df["ListingPrice"] = pd.to_numeric(
        df["ListingPrice"],
        errors="coerce",
    )

    analysis_df = df[
        df["ListingPrice"].notna()
        & (df["ListingPrice"] > 0)
    ].copy()

    print(f"Original rows : {len(df):,}")
    print(
        f"Rows with valid ListingPrice : "
        f"{len(analysis_df):,}"
    )

    return analysis_df


def numeric_target_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:

    numeric_columns = [
        "ModelYear",
        "Kilometres",
        "FuelConsumptionLPer100Km",
        "CylinderCount",
        "Doors",
        "Seats",
    ]

    rows = []

    for column in numeric_columns:

        x = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        valid = (
            x.notna()
            & df["ListingPrice"].notna()
        )

        pearson = x[valid].corr(
            df.loc[
                valid,
                "ListingPrice"
            ],
            method="pearson",
        )

        spearman = None

        rows.append(
            {
                "Variable": column,
                "ValidPairs": int(valid.sum()),
                "PearsonCorrelation": pearson,
                
            }
        )

    result = pd.DataFrame(rows)

    print("\nNUMERIC VARIABLES VS LISTING PRICE")
    print("-" * 80)

    print(result.to_string(index=False))

    result.to_csv(
        REPORT_DIR
        / "numeric_price_correlations.csv",
        index=False,
    )

    return result


def scatter_vs_price(
    df: pd.DataFrame,
    column: str,
) -> None:

    x = pd.to_numeric(
        df[column],
        errors="coerce",
    )

    valid = (
        x.notna()
        & df["ListingPrice"].notna()
    )

    plt.figure(figsize=(10, 6))

    plt.scatter(
        x[valid],
        df.loc[
            valid,
            "ListingPrice"
        ],
        alpha=0.25,
        s=12,
    )

    plt.title(
        f"{column} vs Listing Price"
    )

    plt.xlabel(column)
    plt.ylabel("Listing Price ($)")

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR
        / f"{column}_vs_ListingPrice.png",
        dpi=150,
    )

    plt.close()


def categorical_price_summary(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:

    working = df[
        [column, "ListingPrice"]
    ].copy()

    working[column] = (
        working[column]
        .fillna("Missing")
    )

    summary = (
        working
        .groupby(column)["ListingPrice"]
        .agg(
            ListingCount="count",
            MeanPrice="mean",
            MedianPrice="median",
            MinPrice="min",
            MaxPrice="max",
        )
        .reset_index()
    )

    summary = summary.sort_values(
        by="MedianPrice",
        ascending=False,
    )

    summary.to_csv(
        REPORT_DIR
        / f"{column}_price_summary.csv",
        index=False,
    )

    return summary


def plot_top_category_median_prices(
    df: pd.DataFrame,
    column: str,
    top_n: int = 15,
    minimum_listings: int = 20,
) -> None:

    summary = categorical_price_summary(
        df,
        column,
    )

    eligible = summary[
        summary["ListingCount"]
        >= minimum_listings
    ].copy()

    top = (
        eligible
        .sort_values(
            "MedianPrice",
            ascending=False,
        )
        .head(top_n)
        .sort_values("MedianPrice")
    )

    if top.empty:
        return

    plt.figure(figsize=(10, 7))

    plt.barh(
        top[column].astype(str),
        top["MedianPrice"],
    )

    plt.title(
        f"Median Listing Price by {column}"
    )

    plt.xlabel("Median Listing Price ($)")
    plt.ylabel(column)

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR
        / f"{column}_median_price.png",
        dpi=150,
    )

    plt.close()


def model_year_price_analysis(
    df: pd.DataFrame,
) -> pd.DataFrame:

    summary = (
        df
        .groupby("ModelYear")["ListingPrice"]
        .agg(
            ListingCount="count",
            MeanPrice="mean",
            MedianPrice="median",
        )
        .reset_index()
        .sort_values("ModelYear")
    )

    summary.to_csv(
        REPORT_DIR
        / "model_year_price_summary.csv",
        index=False,
    )

    plt.figure(figsize=(11, 6))

    plt.plot(
        summary["ModelYear"],
        summary["MedianPrice"],
        marker="o",
        markersize=3,
    )

    plt.title(
        "Median Listing Price by Model Year"
    )

    plt.xlabel("Model Year")
    plt.ylabel("Median Listing Price ($)")

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR
        / "model_year_median_price.png",
        dpi=150,
    )

    plt.close()

    return summary


def kilometre_band_analysis(
    df: pd.DataFrame,
) -> pd.DataFrame:

    kilometres = pd.to_numeric(
        df["Kilometres"],
        errors="coerce",
    )

    bins = [
        0,
        25_000,
        50_000,
        75_000,
        100_000,
        150_000,
        200_000,
        300_000,
        float("inf"),
    ]

    labels = [
        "<25k",
        "25k-50k",
        "50k-75k",
        "75k-100k",
        "100k-150k",
        "150k-200k",
        "200k-300k",
        "300k+",
    ]

    working = df[
        ["ListingPrice"]
    ].copy()

    working["KilometreBand"] = pd.cut(
        kilometres,
        bins=bins,
        labels=labels,
        right=False,
    )

    summary = (
        working
        .groupby(
            "KilometreBand",
            observed=True,
        )["ListingPrice"]
        .agg(
            ListingCount="count",
            MeanPrice="mean",
            MedianPrice="median",
        )
        .reset_index()
    )

    summary.to_csv(
        REPORT_DIR
        / "kilometre_band_price_summary.csv",
        index=False,
    )

    print("\nKILOMETRE BAND VS PRICE")
    print("-" * 80)

    print(summary.to_string(index=False))

    plt.figure(figsize=(11, 6))

    plt.bar(
        summary[
            "KilometreBand"
        ].astype(str),
        summary["MedianPrice"],
    )

    plt.title(
        "Median Listing Price by Kilometre Band"
    )

    plt.xlabel("Kilometres")
    plt.ylabel("Median Listing Price ($)")

    plt.xticks(
        rotation=45,
        ha="right",
    )

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR
        / "kilometre_band_median_price.png",
        dpi=150,
    )

    plt.close()

    return summary


def investigate_zero_fuel_consumption(
    df: pd.DataFrame,
) -> pd.DataFrame:

    fuel_consumption = pd.to_numeric(
        df["FuelConsumptionLPer100Km"],
        errors="coerce",
    )

    zero_rows = df[
        fuel_consumption == 0
    ].copy()

    summary = (
        zero_rows["FuelType"]
        .fillna("Missing")
        .value_counts()
        .rename_axis("FuelType")
        .reset_index(name="ZeroConsumptionRows")
    )

    print(
        "\nZERO FUEL CONSUMPTION BY FUEL TYPE"
    )
    print("-" * 80)

    print(summary.to_string(index=False))

    summary.to_csv(
        REPORT_DIR
        / "zero_fuel_consumption_by_fuel_type.csv",
        index=False,
    )

    return summary


def main():

    print("\n" + "=" * 80)
    print("STEP 3.3 - BIVARIATE ANALYSIS")
    print("=" * 80)

    df = load_data()

    numeric_target_summary(df)

    numeric_columns = [
        "ModelYear",
        "Kilometres",
        "FuelConsumptionLPer100Km",
        "CylinderCount",
    ]

    print("\nGenerating scatter plots...")

    for column in numeric_columns:
        scatter_vs_price(
            df,
            column,
        )

    model_year_price_analysis(df)

    kilometre_band_analysis(df)

    categorical_columns = [
        "MakeName",
        "ModelName",
        "BodyType",
        "Transmission",
        "FuelType",
        "DriveType",
    ]

    print(
        "Generating categorical price analysis..."
    )

    for column in categorical_columns:

        plot_top_category_median_prices(
            df,
            column,
        )

    investigate_zero_fuel_consumption(df)

    print("\n" + "=" * 80)
    print("STEP 3.3 BIVARIATE ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()