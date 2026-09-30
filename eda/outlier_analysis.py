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
    / "outliers"
)

REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    print("\nLoading EDA snapshot...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows loaded : {len(df):,}")

    return df


def calculate_iqr_outliers(
    df: pd.DataFrame,
    column: str,
) -> dict:

    values = pd.to_numeric(
        df[column],
        errors="coerce",
    )

    valid = values.dropna()

    q1 = valid.quantile(0.25)
    q3 = valid.quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    outlier_mask = (
        (values < lower_bound)
        | (values > upper_bound)
    )

    outlier_count = int(
        outlier_mask.sum()
    )

    return {
        "Variable": column,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "LowerBound": lower_bound,
        "UpperBound": upper_bound,
        "OutlierCount": outlier_count,
        "OutlierPercentage": round(
            outlier_count / len(df) * 100,
            2,
        ),
    }


def create_iqr_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:

    columns = [
        "ListingPrice",
        "Kilometres",
        "FuelConsumptionLPer100Km",
        "CylinderCount",
        "Doors",
        "Seats",
    ]

    rows = []

    for column in columns:
        rows.append(
            calculate_iqr_outliers(
                df,
                column,
            )
        )

    result = pd.DataFrame(rows)

    print("\nIQR OUTLIER SUMMARY")
    print("-" * 100)

    print(result.to_string(index=False))

    result.to_csv(
        REPORT_DIR / "iqr_outlier_summary.csv",
        index=False,
    )

    return result


def inspect_price_extremes(
    df: pd.DataFrame,
) -> None:

    columns = [
        "CarListingId",
        "MakeName",
        "ModelName",
        "ModelYear",
        "BodyType",
        "FuelType",
        "Kilometres",
        "ListingPrice",
    ]

    valid = df[
        df["ListingPrice"].notna()
    ].copy()

    lowest = (
        valid
        .nsmallest(
            25,
            "ListingPrice",
        )[columns]
    )

    highest = (
        valid
        .nlargest(
            25,
            "ListingPrice",
        )[columns]
    )

    print("\nLOWEST 10 LISTING PRICES")
    print("-" * 100)
    print(lowest.head(10).to_string(index=False))

    print("\nHIGHEST 10 LISTING PRICES")
    print("-" * 100)
    print(highest.head(10).to_string(index=False))

    lowest.to_csv(
        REPORT_DIR / "lowest_25_prices.csv",
        index=False,
    )

    highest.to_csv(
        REPORT_DIR / "highest_25_prices.csv",
        index=False,
    )


def inspect_old_vehicles(
    df: pd.DataFrame,
) -> None:

    old = (
        df[df["ModelYear"] < 1980]
        .sort_values("ModelYear")
    )

    columns = [
        "CarListingId",
        "MakeName",
        "ModelName",
        "ModelYear",
        "Kilometres",
        "ListingPrice",
    ]

    old[columns].to_csv(
        REPORT_DIR / "vehicles_before_1980.csv",
        index=False,
    )

    print(
        f"\nVehicles before 1980 : "
        f"{len(old):,}"
    )


def inspect_zero_fuel_consumption(
    df: pd.DataFrame,
) -> None:

    fuel = pd.to_numeric(
        df["FuelConsumptionLPer100Km"],
        errors="coerce",
    )

    zero = df[
        fuel == 0
    ].copy()

    summary = (
        zero["FuelType"]
        .fillna("Missing")
        .value_counts()
        .rename_axis("FuelType")
        .reset_index(name="Rows")
    )

    summary.to_csv(
        REPORT_DIR
        / "zero_fuel_consumption_summary.csv",
        index=False,
    )

    # Non-electric zero consumption deserves
    # separate investigation.
    suspicious = zero[
        zero["FuelType"]
        .fillna("")
        .str.lower()
        .str.strip()
        != "electric"
    ]

    suspicious.to_csv(
        REPORT_DIR
        / "zero_consumption_non_electric.csv",
        index=False,
    )

    print(
        "\nZERO FUEL CONSUMPTION"
    )
    print("-" * 100)

    print(summary.to_string(index=False))

    print(
        f"\nNon-electric zero-consumption rows: "
        f"{len(suspicious):,}"
    )


def inspect_structural_anomalies(
    df: pd.DataFrame,
) -> None:

    cylinder = pd.to_numeric(
        df["CylinderCount"],
        errors="coerce",
    )

    doors = pd.to_numeric(
        df["Doors"],
        errors="coerce",
    )

    seats = pd.to_numeric(
        df["Seats"],
        errors="coerce",
    )

    suspicious = df[
        (cylinder <= 0)
        | (doors > 6)
        | (seats > 20)
    ].copy()

    suspicious.to_csv(
        REPORT_DIR
        / "structural_anomalies.csv",
        index=False,
    )

    print(
        f"\nStructural anomaly rows : "
        f"{len(suspicious):,}"
    )


def create_outlier_flags(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    # Price IQR flag
    price = pd.to_numeric(
        result["ListingPrice"],
        errors="coerce",
    )

    q1 = price.quantile(0.25)
    q3 = price.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - (1.5 * iqr)
    upper = q3 + (1.5 * iqr)

    result["PriceIqrOutlierFlag"] = (
        (price < lower)
        | (price > upper)
    ).astype(int)

    # Extreme kilometre flag
    kilometres = pd.to_numeric(
        result["Kilometres"],
        errors="coerce",
    )

    result["HighKilometreFlag"] = (
        kilometres > 300_000
    ).astype(int)

    # Suspicious fuel consumption flag
    fuel_consumption = pd.to_numeric(
        result["FuelConsumptionLPer100Km"],
        errors="coerce",
    )

    fuel_type = (
        result["FuelType"]
        .fillna("")
        .str.lower()
        .str.strip()
    )

    result["SuspiciousFuelConsumptionFlag"] = (
        (fuel_consumption == 0)
        & (fuel_type != "electric")
    ).astype(int)

    # Structural anomaly
    cylinder = pd.to_numeric(
        result["CylinderCount"],
        errors="coerce",
    )

    doors = pd.to_numeric(
        result["Doors"],
        errors="coerce",
    )

    seats = pd.to_numeric(
        result["Seats"],
        errors="coerce",
    )

    result["StructuralAnomalyFlag"] = (
        (cylinder <= 0)
        | (doors > 6)
        | (seats > 20)
    ).astype(int)

    result.to_csv(
        REPORT_DIR
        / "used_car_outlier_flagged.csv",
        index=False,
    )

    return result


def plot_price_boxplot(
    df: pd.DataFrame,
) -> None:

    price = pd.to_numeric(
        df["ListingPrice"],
        errors="coerce",
    ).dropna()

    plt.figure(figsize=(11, 4))

    plt.boxplot(
        price,
        vert=False,
    )

    plt.title(
        "Listing Price - Outlier Investigation"
    )

    plt.xlabel("Listing Price ($)")

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "listing_price_boxplot.png",
        dpi=150,
    )

    plt.close()


def main():

    print("\n" + "=" * 100)
    print("STEP 3.4 - OUTLIER ANALYSIS")
    print("=" * 100)

    df = load_data()

    create_iqr_summary(df)

    inspect_price_extremes(df)

    inspect_old_vehicles(df)

    inspect_zero_fuel_consumption(df)

    inspect_structural_anomalies(df)

    flagged = create_outlier_flags(df)

    plot_price_boxplot(df)

    print("\nOUTLIER FLAGS")
    print("-" * 100)

    flag_columns = [
        "PriceIqrOutlierFlag",
        "HighKilometreFlag",
        "SuspiciousFuelConsumptionFlag",
        "StructuralAnomalyFlag",
    ]

    print(
        flagged[flag_columns]
        .sum()
        .to_string()
    )

    print("\n" + "=" * 100)
    print("STEP 3.4 OUTLIER ANALYSIS COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()