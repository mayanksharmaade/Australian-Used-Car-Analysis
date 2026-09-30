from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
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

DATA_DIR = PROJECT_ROOT / "data" / "model"

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "ml"
    / "final_evaluation"
)

MODEL_DIR = PROJECT_ROOT / "models"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)


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


def load_split(filename):

    df = pd.read_csv(
        DATA_DIR / filename
    )

    X = df.drop(columns=[TARGET])
    y = df[TARGET]

    return X, y


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

    return ColumnTransformer(
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


def calculate_metrics(
    y_true,
    predictions,
):

    return {
        "MAE":
            mean_absolute_error(
                y_true,
                predictions,
            ),

        "RMSE":
            np.sqrt(
                mean_squared_error(
                    y_true,
                    predictions,
                )
            ),

        "R2":
            r2_score(
                y_true,
                predictions,
            ),
    }


def build_candidate_models():

    return {
        "RF_Baseline": {
            "n_estimators": 300,
            "max_depth": None,
            "min_samples_leaf": 2,
            "max_features": 1.0,
        },

        "RF_500Trees": {
            "n_estimators": 500,
            "max_depth": None,
            "min_samples_leaf": 2,
            "max_features": 1.0,
        },

        "RF_Leaf1": {
            "n_estimators": 400,
            "max_depth": None,
            "min_samples_leaf": 1,
            "max_features": 1.0,
        },

        "RF_Depth25": {
            "n_estimators": 400,
            "max_depth": 25,
            "min_samples_leaf": 2,
            "max_features": 1.0,
        },

        "RF_SqrtFeatures": {
            "n_estimators": 500,
            "max_depth": None,
            "min_samples_leaf": 2,
            "max_features": "sqrt",
        },
    }


def evaluate_candidates(
    X_train,
    y_train,
    X_val,
    y_val,
):

    results = []
    fitted = {}

    candidates = build_candidate_models()

    for name, params in candidates.items():

        print(
            f"\nTraining candidate: {name}"
        )

        model = RandomForestRegressor(
            **params,
            random_state=RANDOM_STATE,
            n_jobs=-1,
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
                **params,
                **metrics,
            }
        )

        fitted[name] = pipeline

        print(
            f"MAE  : ${metrics['MAE']:,.2f}"
        )
        print(
            f"RMSE : ${metrics['RMSE']:,.2f}"
        )
        print(
            f"R2   : {metrics['R2']:.4f}"
        )

    result_df = pd.DataFrame(
        results
    ).sort_values("MAE")

    return result_df, fitted


def refit_final_model(
    best_name,
    X_train,
    y_train,
    X_val,
    y_val,
):

    params = (
        build_candidate_models()
        [best_name]
    )

    final_model = Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(),
            ),
            (
                "model",
                RandomForestRegressor(
                    **params,
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    X_train_final = pd.concat(
        [
            X_train,
            X_val,
        ],
        ignore_index=True,
    )

    y_train_final = pd.concat(
        [
            y_train,
            y_val,
        ],
        ignore_index=True,
    )

    final_model.fit(
        X_train_final,
        y_train_final,
    )

    return final_model


def evaluate_test(
    model,
    X_test,
    y_test,
):

    predictions = model.predict(
        X_test
    )

    metrics = calculate_metrics(
        y_test,
        predictions,
    )

    result = pd.DataFrame(
        {
            "ActualPrice":
                y_test.to_numpy(),

            "PredictedPrice":
                predictions,
        }
    )

    result["Residual"] = (
        result["ActualPrice"]
        - result["PredictedPrice"]
    )

    result["AbsoluteError"] = (
        result["Residual"].abs()
    )

    result["AbsolutePercentageError"] = (
        result["AbsoluteError"]
        / result["ActualPrice"]
        * 100
    )

    result.to_csv(
        REPORT_DIR
        / "final_test_predictions.csv",
        index=False,
    )

    return metrics, result


def calculate_feature_importance(
    model,
    X_test,
    y_test,
):

    print(
        "\nCalculating permutation importance..."
    )

    importance = permutation_importance(
        model,
        X_test,
        y_test,
        scoring="neg_mean_absolute_error",
        n_repeats=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    result = pd.DataFrame(
        {
            "Feature":
                X_test.columns,

            "ImportanceMean":
                importance.importances_mean,

            "ImportanceStd":
                importance.importances_std,
        }
    )

    result = result.sort_values(
        "ImportanceMean",
        ascending=False,
    )

    result.to_csv(
        REPORT_DIR
        / "permutation_feature_importance.csv",
        index=False,
    )

    print(
        result.head(15).to_string(
            index=False
        )
    )


def main():

    print("\n" + "=" * 90)
    print(
        "STEP 3.8 - MODEL IMPROVEMENT, FINAL TEST EVALUATION & EXPLAINABILITY"
    )
    print("=" * 90)

    X_train, y_train = load_split(
        "train.csv"
    )

    X_val, y_val = load_split(
        "validation.csv"
    )

    X_test, y_test = load_split(
        "test.csv"
    )

    results, _ = evaluate_candidates(
        X_train,
        y_train,
        X_val,
        y_val,
    )

    print("\nVALIDATION MODEL COMPARISON")
    print("-" * 90)
    print(results.to_string(index=False))

    results.to_csv(
        REPORT_DIR
        / "random_forest_tuning_results.csv",
        index=False,
    )

    best_name = (
        results.iloc[0]["Model"]
    )

    print(
        f"\nSelected configuration: "
        f"{best_name}"
    )

    final_model = refit_final_model(
        best_name,
        X_train,
        y_train,
        X_val,
        y_val,
    )

    test_metrics, predictions = (
        evaluate_test(
            final_model,
            X_test,
            y_test,
        )
    )

    print("\nFINAL TEST RESULTS")
    print("-" * 90)

    print(
        f"MAE  : "
        f"${test_metrics['MAE']:,.2f}"
    )

    print(
        f"RMSE : "
        f"${test_metrics['RMSE']:,.2f}"
    )

    print(
        f"R2   : "
        f"{test_metrics['R2']:.4f}"
    )

    pd.DataFrame(
        [
            {
                "Model":
                    best_name,
                **test_metrics,
            }
        ]
    ).to_csv(
        REPORT_DIR
        / "final_test_metrics.csv",
        index=False,
    )

    calculate_feature_importance(
        final_model,
        X_test,
        y_test,
    )

    model_path = (
        MODEL_DIR
        / "final_used_car_price_model.joblib"
    )

    joblib.dump(
        final_model,
        model_path,
    )

    print(
        f"\nFinal model saved to:\n"
        f"{model_path}"
    )

    print("\n" + "=" * 90)
    print("STEP 3.8 COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    main()