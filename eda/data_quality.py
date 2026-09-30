from pathlib import Path

import pandas as pd
import pyodbc


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "eda"
    / "data_quality"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Database configuration
# ---------------------------------------------------------

# IMPORTANT:
# Keep the same server value that worked for you.
SERVER = r"DESKTOP-NEE3MSU\SQLEXPRESS"

DATABASE = "AustralianUsedCarAnalytics"

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


# ---------------------------------------------------------
# Load warehouse dataset
# ---------------------------------------------------------

def load_car_listing_dataset() -> pd.DataFrame:
    """
    Load the analytical used-car dataset from the SQL Server
    dimensional warehouse.

    Warehouse relationships:

    FactCarListing
        -> DimVehicle
        -> DimModel
        -> DimMake

    FactCarListing
        -> DimLocation
    """

    query = """
    SELECT
        -- Fact identifiers
        f.FactCarListingKey,
        f.CarListingId,

        -- Make / Model
        mk.MakeName,
        md.ModelName,

        -- Vehicle attributes
        v.ModelYear,
        v.BodyType,
        v.Transmission,
        v.FuelType,
        v.DriveType,
        v.CylinderCount,
        v.Doors,
        v.Seats,

        -- Location
        l.Suburb,
        l.StateCode,
        l.Postcode,
        l.Latitude,
        l.Longitude,

        -- Listing measures
        f.ListingPrice,
        f.Kilometres,
        f.FuelConsumptionLPer100Km,

        -- Matching information
        f.VehicleSpecificationId,
        f.VehicleMatchScore,
        f.LocationMatchScore,

        -- Audit information
        f.SourceFileName,
        f.LoadedAtUtc

    FROM dw.FactCarListing AS f

    LEFT JOIN dw.DimVehicle AS v
        ON f.VehicleKey = v.VehicleKey

    LEFT JOIN dw.DimModel AS md
        ON v.ModelKey = md.ModelKey

    LEFT JOIN dw.DimMake AS mk
        ON md.MakeKey = mk.MakeKey

    LEFT JOIN dw.DimLocation AS l
        ON f.LocationKey = l.LocationKey;
    """

    with pyodbc.connect(CONNECTION_STRING) as connection:
        df = pd.read_sql_query(query, connection)

    return df


# ---------------------------------------------------------
# Basic dataset profile
# ---------------------------------------------------------

def profile_dataset(df: pd.DataFrame) -> None:

    print("\n" + "=" * 75)
    print("AUSTRALIAN USED CAR ANALYTICS")
    print("STEP 3.1 - DATA QUALITY & PROFILING")
    print("=" * 75)

    print(f"\nRows    : {len(df):,}")
    print(f"Columns : {len(df.columns):,}")

    print("\nCOLUMN NAMES")
    print("-" * 75)

    for column in df.columns:
        print(column)

    print("\nDATA TYPES")
    print("-" * 75)

    print(df.dtypes)


# ---------------------------------------------------------
# Missing value analysis
# ---------------------------------------------------------

def analyse_missing_values(df: pd.DataFrame) -> pd.DataFrame:

    missing_count = df.isna().sum()

    missing_percentage = (
        missing_count / len(df) * 100
    ).round(2)

    missing_report = pd.DataFrame(
        {
            "MissingCount": missing_count,
            "MissingPercentage": missing_percentage,
        }
    )

    missing_report = missing_report.sort_values(
        by="MissingPercentage",
        ascending=False,
    )

    print("\nMISSING VALUE ANALYSIS")
    print("-" * 75)

    print(missing_report.to_string())

    missing_report.to_csv(
        REPORT_DIR / "missing_values.csv",
        index=True,
    )

    return missing_report


# ---------------------------------------------------------
# Duplicate analysis
# ---------------------------------------------------------

def analyse_duplicates(df: pd.DataFrame) -> pd.DataFrame:

    print("\nDUPLICATE ANALYSIS")
    print("-" * 75)

    exact_duplicate_rows = int(
        df.duplicated().sum()
    )

    duplicate_listing_rows = int(
        df["CarListingId"]
        .duplicated(keep=False)
        .sum()
    )

    unique_listing_ids = int(
        df["CarListingId"].nunique()
    )

    result = pd.DataFrame(
        [
            {
                "Metric": "Exact duplicate rows",
                "Value": exact_duplicate_rows,
            },
            {
                "Metric": "Rows belonging to duplicated CarListingId",
                "Value": duplicate_listing_rows,
            },
            {
                "Metric": "Unique CarListingId values",
                "Value": unique_listing_ids,
            },
        ]
    )

    print(result.to_string(index=False))

    result.to_csv(
        REPORT_DIR / "duplicate_summary.csv",
        index=False,
    )

    return result


# ---------------------------------------------------------
# Numeric summary
# ---------------------------------------------------------

def analyse_numeric_quality(df: pd.DataFrame) -> pd.DataFrame:

    numeric_columns = [
        "ModelYear",
        "ListingPrice",
        "Kilometres",
        "FuelConsumptionLPer100Km",
        "CylinderCount",
        "Doors",
        "Seats",
        "Latitude",
        "Longitude",
        "VehicleMatchScore",
        "LocationMatchScore",
    ]

    available_columns = [
        column
        for column in numeric_columns
        if column in df.columns
    ]

    numeric_summary = (
        df[available_columns]
        .describe()
        .transpose()
    )

    print("\nNUMERIC SUMMARY")
    print("-" * 75)

    print(numeric_summary.to_string())

    numeric_summary.to_csv(
        REPORT_DIR / "numeric_summary.csv"
    )

    return numeric_summary


# ---------------------------------------------------------
# Business rule checks
# ---------------------------------------------------------

def analyse_business_rules(df: pd.DataFrame) -> pd.DataFrame:

    checks = []

    # Price checks
    checks.append(
        {
            "Check": "ListingPrice <= 0",
            "Rows": int(
                (df["ListingPrice"] <= 0).sum()
            ),
        }
    )

    checks.append(
        {
            "Check": "ListingPrice missing",
            "Rows": int(
                df["ListingPrice"].isna().sum()
            ),
        }
    )

    # Kilometres checks
    checks.append(
        {
            "Check": "Kilometres < 0",
            "Rows": int(
                (df["Kilometres"] < 0).sum()
            ),
        }
    )

    checks.append(
        {
            "Check": "Kilometres > 1,000,000",
            "Rows": int(
                (df["Kilometres"] > 1_000_000).sum()
            ),
        }
    )

    # Year checks
    checks.append(
        {
            "Check": "ModelYear < 1950",
            "Rows": int(
                (df["ModelYear"] < 1950).sum()
            ),
        }
    )

    checks.append(
        {
            "Check": "ModelYear > 2026",
            "Rows": int(
                (df["ModelYear"] > 2026).sum()
            ),
        }
    )

    # Fuel consumption
    checks.append(
        {
            "Check": "FuelConsumptionLPer100Km <= 0",
            "Rows": int(
                (
                    df["FuelConsumptionLPer100Km"]
                    <= 0
                ).sum()
            ),
        }
    )

    checks.append(
        {
            "Check": "FuelConsumptionLPer100Km > 50",
            "Rows": int(
                (
                    df["FuelConsumptionLPer100Km"]
                    > 50
                ).sum()
            ),
        }
    )

    # Cylinder checks
    checks.append(
        {
            "Check": "CylinderCount <= 0",
            "Rows": int(
                (df["CylinderCount"] <= 0).sum()
            ),
        }
    )

    checks.append(
        {
            "Check": "CylinderCount > 16",
            "Rows": int(
                (df["CylinderCount"] > 16).sum()
            ),
        }
    )

    # Door checks
    checks.append(
        {
            "Check": "Doors <= 0",
            "Rows": int(
                (df["Doors"] <= 0).sum()
            ),
        }
    )

    checks.append(
        {
            "Check": "Doors > 6",
            "Rows": int(
                (df["Doors"] > 6).sum()
            ),
        }
    )

    # Seat checks
    checks.append(
        {
            "Check": "Seats <= 0",
            "Rows": int(
                (df["Seats"] <= 0).sum()
            ),
        }
    )

    checks.append(
        {
            "Check": "Seats > 20",
            "Rows": int(
                (df["Seats"] > 20).sum()
            ),
        }
    )

    result = pd.DataFrame(checks)

    print("\nBUSINESS RULE CHECKS")
    print("-" * 75)

    print(result.to_string(index=False))

    result.to_csv(
        REPORT_DIR / "business_rule_checks.csv",
        index=False,
    )

    return result


# ---------------------------------------------------------
# Categorical coverage
# ---------------------------------------------------------

def analyse_categories(df: pd.DataFrame) -> pd.DataFrame:

    categorical_columns = [
        "MakeName",
        "ModelName",
        "BodyType",
        "Transmission",
        "FuelType",
        "DriveType",
        "Suburb",
        "StateCode",
        "Postcode",
        "SourceFileName",
    ]

    rows = []

    print("\nCATEGORICAL COVERAGE")
    print("-" * 75)

    for column in categorical_columns:

        if column not in df.columns:
            continue

        unique_count = int(
            df[column].nunique(dropna=True)
        )

        missing_count = int(
            df[column].isna().sum()
        )

        missing_percentage = (
            missing_count / len(df) * 100
            if len(df)
            else 0
        )

        rows.append(
            {
                "Column": column,
                "UniqueValues": unique_count,
                "MissingValues": missing_count,
                "MissingPercentage": round(
                    missing_percentage,
                    2
                ),
            }
        )

        print(
            f"{column:<25}"
            f"Unique={unique_count:<8}"
            f"Missing={missing_count:<8}"
            f"Missing%={missing_percentage:.2f}"
        )

    result = pd.DataFrame(rows)

    result.to_csv(
        REPORT_DIR / "categorical_summary.csv",
        index=False,
    )

    return result


# ---------------------------------------------------------
# Make distribution
# ---------------------------------------------------------

def analyse_make_distribution(df: pd.DataFrame) -> pd.DataFrame:

    make_counts = (
        df["MakeName"]
        .value_counts(dropna=False)
        .rename_axis("MakeName")
        .reset_index(name="ListingCount")
    )

    make_counts["ListingPercentage"] = (
        make_counts["ListingCount"]
        / len(df)
        * 100
    ).round(2)

    print("\nTOP 20 MAKES")
    print("-" * 75)

    print(
        make_counts
        .head(20)
        .to_string(index=False)
    )

    make_counts.to_csv(
        REPORT_DIR / "make_distribution.csv",
        index=False,
    )

    return make_counts


# ---------------------------------------------------------
# State distribution
# ---------------------------------------------------------

def analyse_state_distribution(df: pd.DataFrame) -> pd.DataFrame:

    state_counts = (
        df["StateCode"]
        .value_counts(dropna=False)
        .rename_axis("StateCode")
        .reset_index(name="ListingCount")
    )

    state_counts["ListingPercentage"] = (
        state_counts["ListingCount"]
        / len(df)
        * 100
    ).round(2)

    print("\nSTATE DISTRIBUTION")
    print("-" * 75)

    print(
        state_counts.to_string(index=False)
    )

    state_counts.to_csv(
        REPORT_DIR / "state_distribution.csv",
        index=False,
    )

    return state_counts


# ---------------------------------------------------------
# Vehicle specification matching
# ---------------------------------------------------------

def analyse_vehicle_spec_matching(
    df: pd.DataFrame,
) -> pd.DataFrame:

    total_rows = len(df)

    matched_mask = (
        df["VehicleSpecificationId"]
        .notna()
    )

    matched_rows = int(
        matched_mask.sum()
    )

    unmatched_rows = (
        total_rows - matched_rows
    )

    match_percentage = (
        matched_rows / total_rows * 100
        if total_rows
        else 0
    )

    result = pd.DataFrame(
        [
            {
                "Metric": "Total listings",
                "Value": total_rows,
            },
            {
                "Metric": "Vehicle specification matched",
                "Value": matched_rows,
            },
            {
                "Metric": "Vehicle specification unmatched",
                "Value": unmatched_rows,
            },
            {
                "Metric": "Vehicle specification match %",
                "Value": round(
                    match_percentage,
                    2
                ),
            },
        ]
    )

    print("\nVEHICLE SPECIFICATION MATCHING")
    print("-" * 75)

    print(result.to_string(index=False))

    if matched_rows > 0:

        score_summary = (
            df.loc[
                matched_mask,
                "VehicleMatchScore"
            ]
            .describe()
        )

        print(
            "\nVEHICLE MATCH SCORE SUMMARY"
        )

        print(score_summary)

    result.to_csv(
        REPORT_DIR
        / "vehicle_spec_matching.csv",
        index=False,
    )

    return result


# ---------------------------------------------------------
# Location matching analysis
# ---------------------------------------------------------

def analyse_location_matching(
    df: pd.DataFrame,
) -> pd.DataFrame:

    total_rows = len(df)

    location_present_mask = (
        df["StateCode"].notna()
        | df["Suburb"].notna()
        | df["Postcode"].notna()
    )

    matched_rows = int(
        location_present_mask.sum()
    )

    unmatched_rows = (
        total_rows - matched_rows
    )

    match_percentage = (
        matched_rows / total_rows * 100
        if total_rows
        else 0
    )

    result = pd.DataFrame(
        [
            {
                "Metric": "Total listings",
                "Value": total_rows,
            },
            {
                "Metric": "Listings with location dimension",
                "Value": matched_rows,
            },
            {
                "Metric": "Listings without location dimension",
                "Value": unmatched_rows,
            },
            {
                "Metric": "Location dimension coverage %",
                "Value": round(
                    match_percentage,
                    2
                ),
            },
        ]
    )

    print("\nLOCATION MATCHING")
    print("-" * 75)

    print(result.to_string(index=False))

    if df["LocationMatchScore"].notna().any():

        print(
            "\nLOCATION MATCH SCORE SUMMARY"
        )

        print(
            df["LocationMatchScore"]
            .dropna()
            .describe()
        )

    result.to_csv(
        REPORT_DIR / "location_matching.csv",
        index=False,
    )

    return result


# ---------------------------------------------------------
# Model year distribution
# ---------------------------------------------------------

def analyse_model_year_distribution(
    df: pd.DataFrame,
) -> pd.DataFrame:

    year_counts = (
        df["ModelYear"]
        .value_counts(dropna=False)
        .rename_axis("ModelYear")
        .reset_index(name="ListingCount")
        .sort_values(
            by="ModelYear",
            na_position="last",
        )
    )

    print("\nMODEL YEAR COVERAGE")
    print("-" * 75)

    print(
        year_counts
        .tail(20)
        .to_string(index=False)
    )

    year_counts.to_csv(
        REPORT_DIR / "model_year_distribution.csv",
        index=False,
    )

    return year_counts


# ---------------------------------------------------------
# Important ML target quality
# ---------------------------------------------------------

def analyse_target_quality(
    df: pd.DataFrame,
) -> pd.DataFrame:

    price = df["ListingPrice"]

    valid_price_mask = (
        price.notna()
        & (price > 0)
    )

    valid_rows = int(
        valid_price_mask.sum()
    )

    invalid_rows = int(
        len(df) - valid_rows
    )

    result = pd.DataFrame(
        [
            {
                "Metric": "Total listings",
                "Value": len(df),
            },
            {
                "Metric": "Valid target rows",
                "Value": valid_rows,
            },
            {
                "Metric": "Missing/invalid target rows",
                "Value": invalid_rows,
            },
        ]
    )

    print("\nML TARGET QUALITY - LISTING PRICE")
    print("-" * 75)

    print(result.to_string(index=False))

    if valid_rows > 0:

        print("\nLISTING PRICE SUMMARY")
        print("-" * 75)

        print(
            price.loc[
                valid_price_mask
            ].describe()
        )

    result.to_csv(
        REPORT_DIR / "target_quality.csv",
        index=False,
    )

    return result


# ---------------------------------------------------------
# Export analytical snapshot
# ---------------------------------------------------------

def export_eda_snapshot(
    df: pd.DataFrame,
) -> None:

    output_file = (
        REPORT_DIR
        / "used_car_eda_snapshot.csv"
    )

    df.to_csv(
        output_file,
        index=False,
    )

    print("\nEDA SNAPSHOT")
    print("-" * 75)

    print(
        f"Written to:\n{output_file}"
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("\nLoading warehouse data...")

    df = load_car_listing_dataset()

    profile_dataset(df)

    analyse_missing_values(df)

    analyse_duplicates(df)

    analyse_numeric_quality(df)

    analyse_business_rules(df)

    analyse_categories(df)

    analyse_make_distribution(df)

    analyse_state_distribution(df)

    analyse_vehicle_spec_matching(df)

    analyse_location_matching(df)

    analyse_model_year_distribution(df)

    analyse_target_quality(df)

    export_eda_snapshot(df)

    print("\n" + "=" * 75)
    print("STEP 3.1 DATA QUALITY & PROFILING COMPLETE")
    print("=" * 75)


if __name__ == "__main__":
    main()