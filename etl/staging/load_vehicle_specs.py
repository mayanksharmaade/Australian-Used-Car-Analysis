from __future__ import annotations

from pathlib import Path
import json
import pandas as pd

from etl.common.audit import start_pipeline_run, complete_pipeline_run, fail_pipeline_run
from etl.common.db import get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "data" / "raw" / "vehicle_specs"


def _value(row, candidates):
    lookup = {str(c).strip().lower(): c for c in row.index}
    for candidate in candidates:
        key = candidate.lower()
        if key in lookup:
            return row[lookup[key]]
    return None


COLUMN_CANDIDATES = {
    "make": ["make", "manufacturer"],
    "model": ["model"],
    "variant": ["variant", "badge", "description"],
    "year": ["year", "model year", "modelyear"],
    "body": ["body style", "bodystyle", "body type", "bodytype"],
    "engine": ["engine", "engine description", "enginedescription"],
    "transmission": ["transmission"],
    "fuel": ["fuel", "fuel type", "fueltype"],
    "drive": ["drive", "drive type", "drivetype"],
    "seats": ["seats"],
    "fuel_consumption": ["fuel consumption", "fuelconsumption", "combined fuel consumption"],
    "co2": ["co2", "co2 emissions", "co2 combined"],
}


def load_vehicle_specs():
    files = sorted(SOURCE_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No vehicle spec CSV files under {SOURCE_DIR}")

    with get_connection() as connection:
        run_id = start_pipeline_run(connection, "LoadVehicleSpecifications", "Green Vehicle Guide")
        total = 0
        try:
            cursor = connection.cursor()
            cursor.fast_executemany = True
            cursor.execute("TRUNCATE TABLE stg.VehicleSpecification;")

            sql = """
            INSERT INTO stg.VehicleSpecification
            (
                SourceRowNumber, MakeRaw, ModelRaw, VariantRaw, ModelYearRaw,
                BodyStyleRaw, EngineRaw, TransmissionRaw, FuelTypeRaw, DriveTypeRaw,
                SeatsRaw, FuelConsumptionRaw, CO2Raw, RawJson,
                SourceFileName, PipelineRunId
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """

            for file in files:
                df = pd.read_csv(file, dtype=str, keep_default_na=False, low_memory=False)
                rows = []
                for idx, row in df.iterrows():
                    raw_json = json.dumps(
                        {str(k): (None if pd.isna(v) else str(v)) for k, v in row.to_dict().items()},
                        ensure_ascii=False,
                    )
                    rows.append((
                        idx + 2,
                        _value(row, COLUMN_CANDIDATES["make"]),
                        _value(row, COLUMN_CANDIDATES["model"]),
                        _value(row, COLUMN_CANDIDATES["variant"]),
                        _value(row, COLUMN_CANDIDATES["year"]),
                        _value(row, COLUMN_CANDIDATES["body"]),
                        _value(row, COLUMN_CANDIDATES["engine"]),
                        _value(row, COLUMN_CANDIDATES["transmission"]),
                        _value(row, COLUMN_CANDIDATES["fuel"]),
                        _value(row, COLUMN_CANDIDATES["drive"]),
                        _value(row, COLUMN_CANDIDATES["seats"]),
                        _value(row, COLUMN_CANDIDATES["fuel_consumption"]),
                        _value(row, COLUMN_CANDIDATES["co2"]),
                        raw_json,
                        file.name,
                        run_id,
                    ))
                cursor.executemany(sql, rows)
                total += len(rows)

            connection.commit()
            complete_pipeline_run(connection, run_id, rows_read=total, rows_loaded=total)
            print(f"Loaded {total:,} rows into stg.VehicleSpecification")
        except Exception as ex:
            connection.rollback()
            fail_pipeline_run(connection, run_id, str(ex))
            raise


if __name__ == "__main__":
    load_vehicle_specs()
