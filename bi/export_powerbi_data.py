from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ANALYTICS_FILE = (
    PROJECT_ROOT
    / "data"
    / "analytics"
    / "used_car_market_analytics.csv"
)

FINAL_METRICS_FILE = (
    PROJECT_ROOT
    / "reports"
    / "ml"
    / "final_evaluation"
    / "final_test_metrics.csv"
)

FEATURE_IMPORTANCE_FILE = (
    PROJECT_ROOT
    / "reports"
    / "ml"
    / "final_evaluation"
    / "permutation_feature_importance.csv"
)

TEST_PREDICTIONS_FILE = (
    PROJECT_ROOT
    / "reports"
    / "ml"
    / "final_evaluation"
    / "final_test_predictions.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "powerbi"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def main():

    print("\n" + "=" * 90)
    print(
        "STEP 4.1 - POWER BI DATA EXPORT"
    )
    print("=" * 90)

    df = pd.read_csv(
        ANALYTICS_FILE
    )

    # Main market dataset
    df.to_csv(
        OUTPUT_DIR
        / "market_listings.csv",
        index=False,
    )

    # Brand summary
    brand_summary = (
        df.groupby(
            "MakeName",
            dropna=False,
        )
        .agg(
            ListingCount=(
                "CarListingId",
                "count",
            ),
            AveragePrice=(
                "ListingPrice",
                "mean",
            ),
            MedianPrice=(
                "ListingPrice",
                "median",
            ),
            AverageKilometres=(
                "Kilometres",
                "mean",
            ),
            AverageVehicleAge=(
                "VehicleAge",
                "mean",
            ),
        )
        .reset_index()
    )

    brand_summary.to_csv(
        OUTPUT_DIR
        / "brand_summary.csv",
        index=False,
    )

    # Model summary
    model_summary = (
        df.groupby(
            [
                "MakeName",
                "ModelName",
            ],
            dropna=False,
        )
        .agg(
            ListingCount=(
                "CarListingId",
                "count",
            ),
            AveragePrice=(
                "ListingPrice",
                "mean",
            ),
            MedianPrice=(
                "ListingPrice",
                "median",
            ),
            AverageKilometres=(
                "Kilometres",
                "mean",
            ),
        )
        .reset_index()
    )

    model_summary.to_csv(
        OUTPUT_DIR
        / "model_summary.csv",
        index=False,
    )

    # Price position summary
    price_position = (
        df["PricePosition"]
        .value_counts()
        .rename_axis(
            "PricePosition"
        )
        .reset_index(
            name="ListingCount"
        )
    )

    price_position.to_csv(
        OUTPUT_DIR
        / "price_position_summary.csv",
        index=False,
    )

    # ML supporting tables
    pd.read_csv(
        FINAL_METRICS_FILE
    ).to_csv(
        OUTPUT_DIR
        / "model_performance.csv",
        index=False,
    )

    pd.read_csv(
        FEATURE_IMPORTANCE_FILE
    ).to_csv(
        OUTPUT_DIR
        / "feature_importance.csv",
        index=False,
    )

    pd.read_csv(
        TEST_PREDICTIONS_FILE
    ).to_csv(
        OUTPUT_DIR
        / "test_predictions.csv",
        index=False,
    )

    print(
        f"\nPower BI files written to:\n"
        f"{OUTPUT_DIR}"
    )

    print("\n" + "=" * 90)
    print("STEP 4.1 COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    main()