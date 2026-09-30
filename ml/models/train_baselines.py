from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "model"
)

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "ml"
    / "baseline_models"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


TARGET = "ListingPrice"

RANDOM_STATE = 42


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


# ---------------------------------------------------------
# Load split
# ---------------------------------------------------------

def load_split(
    filename: str,
):

    path = DATA_DIR / filename

    df = pd.read_csv(path)

    X = df.drop(
        columns=[TARGET]
    )

    y = df[TARGET]

    return X, y


# ---------------------------------------------------------
# Preprocessor
# ---------------------------------------------------------

def build_preprocessor():

    numeric_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="most_frequent"
                ),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_pipeline,
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    return preprocessor


# ---------------------------------------------------------
# Model definitions
# ---------------------------------------------------------

def build_models():

    models = {
        "DummyMedian": (
            DummyRegressor(
                strategy="median"
            )
        ),

        "LinearRegression": (
            LinearRegression()
        ),

        "RandomForest": (
            RandomForestRegressor(
                n_estimators=300,
                random_state=RANDOM_STATE,
                n_jobs=-1,
                min_samples_leaf=2,
            )
        ),
    }

    return models


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

def calculate_metrics(
    y_true,
    predictions,
):

    mae = mean_absolute_error(
        y_true,
        predictions,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            predictions,
        )
    )

    r2 = r2_score(
        y_true,
        predictions,
    )

    return {
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
    }


# ---------------------------------------------------------
# Train and validate
# ---------------------------------------------------------

def train_models(
    X_train,
    y_train,
    X_val,
    y_val,
):

    models = build_models()

    results = []

    fitted_models = {}

    for name, model in models.items():

        print(
            f"\nTraining {name}..."
        )

        pipeline = Pipeline(
            steps=[
                (
                    "preprocessor",
                    build_preprocessor(),
                ),
                (
                    "model",
                    model,
                ),
            ]
        )

        pipeline.fit(
            X_train,
            y_train,
        )

        predictions = pipeline.predict(
            X_val
        )

        metrics = calculate_metrics(
            y_val,
            predictions,
        )

        results.append(
            {
                "Model": name,
                **metrics,
            }
        )

        fitted_models[name] = pipeline

        print(
            f"MAE  : "
            f"${metrics['MAE']:,.2f}"
        )

        print(
            f"RMSE : "
            f"${metrics['RMSE']:,.2f}"
        )

        print(
            f"R2   : "
            f"{metrics['R2']:.4f}"
        )

    results_df = pd.DataFrame(
        results
    )

    return (
        results_df,
        fitted_models,
    )


# ---------------------------------------------------------
# Select best model
# ---------------------------------------------------------

def select_best_model(
    results: pd.DataFrame,
    fitted_models: dict,
):

    # MAE is the primary selection metric because
    # it is directly interpretable in Australian dollars.
    best_row = (
        results
        .sort_values("MAE")
        .iloc[0]
    )

    best_name = best_row["Model"]

    best_model = (
        fitted_models[best_name]
    )

    return (
        best_name,
        best_model,
    )


# ---------------------------------------------------------
# Save validation predictions
# ---------------------------------------------------------

def save_validation_predictions(
    model,
    X_val,
    y_val,
) -> None:

    predictions = model.predict(
        X_val
    )

    result = pd.DataFrame(
        {
            "ActualPrice":
                y_val.to_numpy(),
            "PredictedPrice":
                predictions,
        }
    )

    result["AbsoluteError"] = (
        result["ActualPrice"]
        - result["PredictedPrice"]
    ).abs()

    result["Residual"] = (
        result["ActualPrice"]
        - result["PredictedPrice"]
    )

    result.to_csv(
        REPORT_DIR
        / "best_model_validation_predictions.csv",
        index=False,
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("\n" + "=" * 90)
    print("STEP 3.7 - BASELINE ML MODELS")
    print("=" * 90)

    X_train, y_train = load_split(
        "train.csv"
    )

    X_val, y_val = load_split(
        "validation.csv"
    )

    print(
        f"\nTraining rows   : "
        f"{len(X_train):,}"
    )

    print(
        f"Validation rows : "
        f"{len(X_val):,}"
    )

    print(
        f"Predictors      : "
        f"{X_train.shape[1]}"
    )

    (
        results,
        fitted_models,
    ) = train_models(
        X_train,
        y_train,
        X_val,
        y_val,
    )

    results = results.sort_values(
        "MAE"
    )

    print("\nMODEL COMPARISON")
    print("-" * 90)

    print(
        results.to_string(
            index=False,
            float_format=lambda x:
                f"{x:,.4f}",
        )
    )

    results.to_csv(
        REPORT_DIR
        / "baseline_model_comparison.csv",
        index=False,
    )

    (
        best_name,
        best_model,
    ) = select_best_model(
        results,
        fitted_models,
    )

    print(
        f"\nBest validation model: "
        f"{best_name}"
    )

    save_validation_predictions(
        best_model,
        X_val,
        y_val,
    )

    model_path = (
        MODEL_DIR
        / "best_baseline_model.joblib"
    )

    joblib.dump(
        best_model,
        model_path,
    )

    print(
        f"\nBest model saved to:\n"
        f"{model_path}"
    )

    print("\n" + "=" * 90)
    print("STEP 3.7 BASELINE ML MODELLING COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    main()