from __future__ import annotations

from pathlib import Path
import re
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CAR_LISTING_FILE = PROJECT_ROOT / "data" / "raw" / "car_listings" / "Australian Vehicle Prices.csv"
VEHICLE_SPEC_DIR = PROJECT_ROOT / "data" / "raw" / "vehicle_specs"
LOCATION_FILE = PROJECT_ROOT / "data" / "raw" / "locations" / "australian_postcodes.csv"
REPORT_DIR = PROJECT_ROOT / "reports" / "data_engineering" / "source_schema"
GENERATED_SQL_DIR = PROJECT_ROOT / "sql" / "staging" / "generated"
SAMPLE_SIZE = 5000


def sql_safe_name(column_name):
    column_name = str(column_name).strip()
    column_name = re.sub(r"[^A-Za-z0-9_]+", "_", column_name)
    column_name = re.sub(r"_+", "_", column_name).strip("_")
    if not column_name:
        column_name = "Column"
    if column_name[0].isdigit():
        column_name = f"Col_{column_name}"
    return column_name


def infer_sql_type(series):
    non_null = series.dropna()
    if non_null.empty:
        return "NVARCHAR(255)"
    if pd.api.types.is_bool_dtype(series):
        return "BIT"
    if pd.api.types.is_integer_dtype(series):
        return "BIGINT"
    if pd.api.types.is_float_dtype(series):
        return "DECIMAL(18,4)"
    numeric = pd.to_numeric(non_null, errors="coerce")
    if numeric.notna().mean() >= 0.98:
        valid = numeric.dropna()
        return "BIGINT" if ((valid % 1) == 0).all() else "DECIMAL(18,4)"
    max_len = int(non_null.astype(str).str.len().max())
    if max_len <= 50:
        return "NVARCHAR(50)"
    if max_len <= 100:
        return "NVARCHAR(100)"
    if max_len <= 255:
        return "NVARCHAR(255)"
    if max_len <= 1000:
        return "NVARCHAR(1000)"
    return "NVARCHAR(MAX)"


def profile_dataset(dataset_name, file_path):
    df = pd.read_csv(file_path, nrows=SAMPLE_SIZE, low_memory=False)
    rows = []
    for column in df.columns:
        s = df[column]
        non_null = s.dropna()
        rows.append({
            "Dataset": dataset_name,
            "SourceFile": file_path.name,
            "SourceColumn": column,
            "SuggestedSqlColumn": sql_safe_name(column),
            "PandasDtype": str(s.dtype),
            "SuggestedSqlType": infer_sql_type(s),
            "RowsSampled": len(df),
            "NonNullCount": int(s.notna().sum()),
            "NullCount": int(s.isna().sum()),
            "NullPercentage": round(s.isna().mean() * 100, 2),
            "UniqueCount": int(s.nunique(dropna=True)),
            "MaxStringLength": int(non_null.astype(str).str.len().max()) if not non_null.empty else 0,
            "ExampleValues": " | ".join(non_null.astype(str).head(3).tolist()),
        })
    return pd.DataFrame(rows), {
        "Dataset": dataset_name,
        "SourceFile": file_path.name,
        "RowsSampled": len(df),
        "Columns": len(df.columns),
        "DuplicateRowsInSample": int(df.duplicated().sum()),
    }


def validate_source_files():
    missing = []
    if not CAR_LISTING_FILE.exists():
        missing.append(str(CAR_LISTING_FILE))
    vehicle_files = sorted(VEHICLE_SPEC_DIR.glob("*.csv")) if VEHICLE_SPEC_DIR.exists() else []
    if not vehicle_files:
        missing.append(str(VEHICLE_SPEC_DIR / "*.csv"))
    if not LOCATION_FILE.exists():
        missing.append(str(LOCATION_FILE))
    if missing:
        raise FileNotFoundError("Missing required sources:\n" + "\n".join(missing))
    return vehicle_files


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    vehicle_files = validate_source_files()
    summaries = []

    car_profile, summary = profile_dataset("CarListings", CAR_LISTING_FILE)
    summaries.append(summary)
    car_profile.to_csv(REPORT_DIR / "car_listings_schema_profile.csv", index=False)

    vehicle_profiles = []
    for file in vehicle_files:
        profile, summary = profile_dataset("VehicleSpecifications", file)
        vehicle_profiles.append(profile)
        summaries.append(summary)
    pd.concat(vehicle_profiles, ignore_index=True).to_csv(
        REPORT_DIR / "vehicle_specs_schema_profile.csv", index=False
    )

    location_profile, summary = profile_dataset("Locations", LOCATION_FILE)
    summaries.append(summary)
    location_profile.to_csv(REPORT_DIR / "locations_schema_profile.csv", index=False)

    pd.DataFrame(summaries).to_csv(REPORT_DIR / "source_file_summary.csv", index=False)

    print("SOURCE SCHEMA INSPECTION COMPLETE")
    print(f"Reports: {REPORT_DIR}")


if __name__ == "__main__":
    main()
