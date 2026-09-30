from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FEATURE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "used_car_ml_features.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "final_used_car_price_model.joblib"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "analytics"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "ml"
    / "final_dataset"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


MODEL_FEATURES = [
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
    "MakeName",
    "ModelName",
    "BodyType",
    "Transmission",
    "FuelType",
    "DriveType",
]


def main():

    print("\n" + "=" * 90)
    print(
        "STEP 3.9 - FINAL ANALYTICS / PREDICTION DATASET"
    )
    print("=" * 90)

    df = pd.read_csv(
        FEATURE_FILE
    )

    model = joblib.load(
        MODEL_FILE
    )

    valid_features = df[
        MODEL_FEATURES
    ].copy()

    predictions = model.predict(
        valid_features
    )

    df["PredictedPrice"] = predictions

    df["PriceDifference"] = (
        df["ListingPrice"]
        - df["PredictedPrice"]
    )

    df["AbsolutePriceDifference"] = (
        df["PriceDifference"].abs()
    )

    df["PriceDifferencePct"] = (
        df["PriceDifference"]
        / df["PredictedPrice"]
        * 100
    )

    df["PricePosition"] = "Near Model Estimate"

    df.loc[
        df["PriceDifferencePct"] >= 15,
        "PricePosition",
    ] = "Above Model Estimate"

    df.loc[
        df["PriceDifferencePct"] <= -15,
        "PricePosition",
    ] = "Below Model Estimate"

    output_file = (
        OUTPUT_DIR
        / "used_car_market_analytics.csv"
    )

    df.to_csv(
        output_file,
        index=False,
    )

    summary = pd.DataFrame(
        [
            {
                "TotalListings":
                    len(df),

                "AverageListingPrice":
                    df[
                        "ListingPrice"
                    ].mean(),

                "MedianListingPrice":
                    df[
                        "ListingPrice"
                    ].median(),

                "AverageKilometres":
                    df[
                        "Kilometres"
                    ].mean(),

                "AverageModelEstimate":
                    df[
                        "PredictedPrice"
                    ].mean(),

                "AboveModelEstimate":
                    (
                        df["PricePosition"]
                        == "Above Model Estimate"
                    ).sum(),

                "BelowModelEstimate":
                    (
                        df["PricePosition"]
                        == "Below Model Estimate"
                    ).sum(),
            }
        ]
    )

    summary.to_csv(
        REPORT_DIR
        / "analytics_dataset_summary.csv",
        index=False,
    )

    print(
        f"\nRows exported : {len(df):,}"
    )

    print(
        f"\nAnalytics dataset:\n"
        f"{output_file}"
    )

    print("\n" + "=" * 90)
    print("STEP 3.9 COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    main()