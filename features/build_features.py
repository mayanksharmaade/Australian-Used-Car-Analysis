from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "reports"
    / "eda"
    / "outliers"
    / "used_car_outlier_flagged.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "features"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


REFERENCE_YEAR = 2026


def load_data() -> pd.DataFrame:

    print("\nLoading outlier-flagged dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows loaded : {len(df):,}")
    print(f"Columns     : {len(df.columns):,}")

    return df


def create_vehicle_age(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    year = pd.to_numeric(
        result["ModelYear"],
        errors="coerce",
    )

    result["VehicleAge"] = (
        REFERENCE_YEAR - year
    )

    result.loc[
        result["VehicleAge"] < 0,
        "VehicleAge",
    ] = np.nan

    return result


def create_kilometres_per_year(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    kilometres = pd.to_numeric(
        result["Kilometres"],
        errors="coerce",
    )

    age = pd.to_numeric(
        result["VehicleAge"],
        errors="coerce",
    )

    # For a current-year vehicle, division by zero
    # would be invalid. Treat it as approximately
    # one year of exposure for this derived feature.
    denominator = age.clip(lower=1)

    result["KilometresPerYear"] = (
        kilometres / denominator
    )

    return result


def create_vehicle_age_band(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    bins = [
        -1,
        2,
        5,
        10,
        15,
        20,
        30,
        float("inf"),
    ]

    labels = [
        "0-2 years",
        "3-5 years",
        "6-10 years",
        "11-15 years",
        "16-20 years",
        "21-30 years",
        "30+ years",
    ]

    result["VehicleAgeBand"] = pd.cut(
        result["VehicleAge"],
        bins=bins,
        labels=labels,
    )

    return result


def create_kilometre_band(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    kilometres = pd.to_numeric(
        result["Kilometres"],
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

    result["KilometreBand"] = pd.cut(
        kilometres,
        bins=bins,
        labels=labels,
        right=False,
    )

    return result


def create_price_band(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    price = pd.to_numeric(
        result["ListingPrice"],
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

    # NOTE:
    # PriceBand is useful for reporting/Power BI,
    # but must NOT be used to predict ListingPrice.
    result["PriceBand"] = pd.cut(
        price,
        bins=bins,
        labels=labels,
        right=False,
    )

    return result


def create_missingness_features(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    useful_columns = [
        "Kilometres",
        "BodyType",
        "Transmission",
        "FuelType",
        "FuelConsumptionLPer100Km",
        "CylinderCount",
        "Doors",
        "Seats",
    ]

    result["MissingFeatureCount"] = (
        result[useful_columns]
        .isna()
        .sum(axis=1)
    )

    result["HasMissingVehicleData"] = (
        result["MissingFeatureCount"] > 0
    ).astype(int)

    return result


def create_spec_match_feature(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    result["HasVehicleSpecMatch"] = (
        result["VehicleSpecificationId"]
        .notna()
        .astype(int)
    )

    return result


def create_fuel_features(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    fuel = (
        result["FuelType"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
    )

    result["IsElectric"] = (
        fuel == "electric"
    ).astype(int)

    result["IsHybrid"] = (
        fuel.str.contains(
            "hybrid",
            regex=False,
        )
    ).astype(int)

    result["IsDiesel"] = (
        fuel == "diesel"
    ).astype(int)

    return result


def create_log_features(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    kilometres = pd.to_numeric(
        result["Kilometres"],
        errors="coerce",
    )

    # log1p handles zero safely.
    result["LogKilometres"] = np.log1p(
        kilometres.clip(lower=0)
    )

    # Target transformation candidate.
    # Keep for modelling experiments but don't
    # treat it as an independent predictor.
    price = pd.to_numeric(
        result["ListingPrice"],
        errors="coerce",
    )

    result["LogListingPrice"] = np.where(
        price > 0,
        np.log1p(price),
        np.nan,
    )

    return result


def create_feature_summary(
    df: pd.DataFrame,
) -> None:

    engineered = [
        "VehicleAge",
        "KilometresPerYear",
        "VehicleAgeBand",
        "KilometreBand",
        "PriceBand",
        "MissingFeatureCount",
        "HasMissingVehicleData",
        "HasVehicleSpecMatch",
        "IsElectric",
        "IsHybrid",
        "IsDiesel",
        "LogKilometres",
        "LogListingPrice",
    ]

    rows = []

    for column in engineered:

        rows.append(
            {
                "Feature": column,
                "DataType": str(
                    df[column].dtype
                ),
                "MissingCount": int(
                    df[column]
                    .isna()
                    .sum()
                ),
                "UniqueValues": int(
                    df[column]
                    .nunique(
                        dropna=True
                    )
                ),
            }
        )

    summary = pd.DataFrame(rows)

    print("\nENGINEERED FEATURE SUMMARY")
    print("-" * 90)

    print(
        summary.to_string(
            index=False
        )
    )

    summary.to_csv(
        REPORT_DIR
        / "engineered_feature_summary.csv",
        index=False,
    )


def export_dataset(
    df: pd.DataFrame,
) -> None:

    output_file = (
        OUTPUT_DIR
        / "used_car_ml_features.csv"
    )

    df.to_csv(
        output_file,
        index=False,
    )

    print("\nFEATURE DATASET")
    print("-" * 90)

    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns):,}")

    print(
        f"\nWritten to:\n"
        f"{output_file}"
    )


def main():

    print("\n" + "=" * 90)
    print("STEP 3.5 - FEATURE ENGINEERING")
    print("=" * 90)

    df = load_data()

    df = create_vehicle_age(df)

    df = create_kilometres_per_year(df)

    df = create_vehicle_age_band(df)

    df = create_kilometre_band(df)

    df = create_price_band(df)

    df = create_missingness_features(df)

    df = create_spec_match_feature(df)

    df = create_fuel_features(df)

    df = create_log_features(df)

    create_feature_summary(df)

    export_dataset(df)

    print("\n" + "=" * 90)
    print("STEP 3.5 FEATURE ENGINEERING COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    main()