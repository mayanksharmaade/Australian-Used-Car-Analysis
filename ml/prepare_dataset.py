from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "used_car_ml_features.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "model"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "ml"
    / "dataset_preparation"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


RANDOM_STATE = 42

TARGET = "ListingPrice"


# ---------------------------------------------------------
# Feature configuration
# ---------------------------------------------------------

NUMERIC_FEATURES = [
    "ModelYear",
    "Kilometres",
    "FuelConsumptionLPer100Km",
    "CylinderCount",
    "Doors",
    "Seats",
    "VehicleAge",
    "KilometresPerYear",
    "MissingFeatureCount",
    "HasMissingVehicleData",
    "HasVehicleSpecMatch",
    "IsElectric",
    "IsHybrid",
    "IsDiesel",
    "LogKilometres",
]


CATEGORICAL_FEATURES = [
    "MakeName",
    "ModelName",
    "BodyType",
    "Transmission",
    "FuelType",
    "DriveType",
]


EXCLUDED_COLUMNS = [
    # Identifiers
    "FactCarListingKey",
    "CarListingId",

    # Target-derived / leakage
    "PriceBand",
    "LogListingPrice",

    # Reporting bands
    "VehicleAgeBand",
    "KilometreBand",

    # Location unavailable in current pipeline
    "Suburb",
    "StateCode",
    "Postcode",
    "Latitude",
    "Longitude",
    "LocationMatchScore",

    # Matching internals
    "VehicleSpecificationId",
    "VehicleMatchScore",

    # Audit
    "SourceFileName",
    "LoadedAtUtc",

    # EDA anomaly flags
    "PriceIqrOutlierFlag",
    "HighKilometreFlag",
    "SuspiciousFuelConsumptionFlag",
    "StructuralAnomalyFlag",
]


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

def load_data() -> pd.DataFrame:

    print("\nLoading engineered feature dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows loaded    : {len(df):,}")
    print(f"Columns loaded : {len(df.columns):,}")

    return df


# ---------------------------------------------------------
# Target filtering
# ---------------------------------------------------------

def filter_target(
    df: pd.DataFrame,
) -> pd.DataFrame:

    result = df.copy()

    result[TARGET] = pd.to_numeric(
        result[TARGET],
        errors="coerce",
    )

    before = len(result)

    result = result[
        result[TARGET].notna()
        & (result[TARGET] > 0)
    ].copy()

    removed = before - len(result)

    print("\nTARGET FILTERING")
    print("-" * 80)

    print(f"Original rows     : {before:,}")
    print(f"Valid target rows : {len(result):,}")
    print(f"Rows removed      : {removed:,}")

    return result


# ---------------------------------------------------------
# Validate feature contract
# ---------------------------------------------------------

def validate_features(
    df: pd.DataFrame,
) -> None:

    required = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
        + [TARGET]
    )

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Required ML columns are missing: "
            + ", ".join(missing)
        )


# ---------------------------------------------------------
# Build X and y
# ---------------------------------------------------------

def build_xy(
    df: pd.DataFrame,
):

    feature_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    )

    X = df[feature_columns].copy()

    y = df[TARGET].copy()

    return X, y


# ---------------------------------------------------------
# Train / validation / test split
# ---------------------------------------------------------

def split_dataset(
    X: pd.DataFrame,
    y: pd.Series,
):

    # First reserve 20% for final testing.
    X_train_val, X_test, y_train_val, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=RANDOM_STATE,
        )
    )

    # 25% of remaining 80% = 20% of complete dataset.
    X_train, X_val, y_train, y_val = (
        train_test_split(
            X_train_val,
            y_train_val,
            test_size=0.25,
            random_state=RANDOM_STATE,
        )
    )

    return (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    )


# ---------------------------------------------------------
# Dataset profiling
# ---------------------------------------------------------

def create_split_summary(
    X_train,
    X_val,
    X_test,
    y_train,
    y_val,
    y_test,
) -> None:

    total = (
        len(X_train)
        + len(X_val)
        + len(X_test)
    )

    rows = []

    for name, X_part, y_part in [
        ("Train", X_train, y_train),
        ("Validation", X_val, y_val),
        ("Test", X_test, y_test),
    ]:

        rows.append(
            {
                "Split": name,
                "Rows": len(X_part),
                "Percentage": round(
                    len(X_part) / total * 100,
                    2,
                ),
                "TargetMean": y_part.mean(),
                "TargetMedian": y_part.median(),
                "TargetMin": y_part.min(),
                "TargetMax": y_part.max(),
            }
        )

    summary = pd.DataFrame(rows)

    print("\nDATASET SPLIT")
    print("-" * 80)

    print(summary.to_string(index=False))

    summary.to_csv(
        REPORT_DIR / "split_summary.csv",
        index=False,
    )


# ---------------------------------------------------------
# Missingness report
# ---------------------------------------------------------

def create_feature_missingness_report(
    X_train: pd.DataFrame,
) -> None:

    report = pd.DataFrame(
        {
            "MissingCount":
                X_train.isna().sum(),
            "MissingPercentage":
                (
                    X_train.isna().mean()
                    * 100
                ).round(2),
            "UniqueValues":
                X_train.nunique(
                    dropna=True
                ),
        }
    )

    report = report.sort_values(
        "MissingPercentage",
        ascending=False,
    )

    print("\nTRAINING FEATURE MISSINGNESS")
    print("-" * 80)

    print(report.to_string())

    report.to_csv(
        REPORT_DIR
        / "training_feature_missingness.csv"
    )


# ---------------------------------------------------------
# Export split files
# ---------------------------------------------------------

def export_split(
    X: pd.DataFrame,
    y: pd.Series,
    name: str,
) -> None:

    output = X.copy()

    output[TARGET] = y.values

    output.to_csv(
        OUTPUT_DIR / f"{name}.csv",
        index=False,
    )


# ---------------------------------------------------------
# Export feature contract
# ---------------------------------------------------------

def export_feature_contract() -> None:

    rows = []

    for column in NUMERIC_FEATURES:
        rows.append(
            {
                "Feature": column,
                "FeatureType": "Numeric",
            }
        )

    for column in CATEGORICAL_FEATURES:
        rows.append(
            {
                "Feature": column,
                "FeatureType": "Categorical",
            }
        )

    pd.DataFrame(rows).to_csv(
        REPORT_DIR / "feature_contract.csv",
        index=False,
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("\n" + "=" * 80)
    print("STEP 3.6 - ML DATASET PREPARATION & SPLIT")
    print("=" * 80)

    df = load_data()

    df = filter_target(df)

    validate_features(df)

    X, y = build_xy(df)

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    ) = split_dataset(X, y)

    create_split_summary(
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    )

    create_feature_missingness_report(
        X_train
    )

    export_split(
        X_train,
        y_train,
        "train",
    )

    export_split(
        X_val,
        y_val,
        "validation",
    )

    export_split(
        X_test,
        y_test,
        "test",
    )

    export_feature_contract()

    print("\nFEATURE CONTRACT")
    print("-" * 80)

    print(
        f"Numeric features     : "
        f"{len(NUMERIC_FEATURES)}"
    )

    print(
        f"Categorical features : "
        f"{len(CATEGORICAL_FEATURES)}"
    )

    print(
        f"Total predictors     : "
        f"{len(NUMERIC_FEATURES) + len(CATEGORICAL_FEATURES)}"
    )

    print("\n" + "=" * 80)
    print("STEP 3.6 ML DATASET PREPARATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()