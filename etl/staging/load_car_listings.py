from __future__ import annotations

from pathlib import Path
import json
import pandas as pd

from etl.common.audit import start_pipeline_run, complete_pipeline_run, fail_pipeline_run
from etl.common.db import get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "car_listings" / "Australian Vehicle Prices.csv"

EXPECTED_COLUMNS = [
    "Brand", "Year", "Model", "Car/Suv", "Title", "UsedOrNew",
    "Transmission", "Engine", "DriveType", "FuelType",
    "FuelConsumption", "Kilometres", "ColourExtInt", "Location",
    "CylindersinEngine", "BodyType", "Doors", "Seats", "Price",
]


def load_car_listings():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(SOURCE_FILE)

    df = pd.read_csv(SOURCE_FILE, dtype=str, keep_default_na=False, low_memory=False)
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Car listing source is missing columns: {missing}")

    with get_connection() as connection:
        run_id = start_pipeline_run(connection, "LoadCarListings", "Australian Vehicle Prices")
        try:
            cursor = connection.cursor()
            cursor.fast_executemany = True
            cursor.execute("TRUNCATE TABLE stg.CarListing;")

            sql = """
            INSERT INTO stg.CarListing
            (
                SourceRowNumber, BrandRaw, YearRaw, ModelRaw, CarSuvRaw, TitleRaw,
                UsedOrNewRaw, TransmissionRaw, EngineRaw, DriveTypeRaw, FuelTypeRaw,
                FuelConsumptionRaw, KilometresRaw, ColourExtIntRaw, LocationRaw,
                CylindersInEngineRaw, BodyTypeRaw, DoorsRaw, SeatsRaw, PriceRaw,
                SourceFileName, PipelineRunId
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """

            rows = []
            for idx, row in df.iterrows():
                rows.append((
                    idx + 2,
                    row["Brand"], row["Year"], row["Model"], row["Car/Suv"], row["Title"],
                    row["UsedOrNew"], row["Transmission"], row["Engine"], row["DriveType"],
                    row["FuelType"], row["FuelConsumption"], row["Kilometres"],
                    row["ColourExtInt"], row["Location"], row["CylindersinEngine"],
                    row["BodyType"], row["Doors"], row["Seats"], row["Price"],
                    SOURCE_FILE.name, run_id,
                ))

            cursor.executemany(sql, rows)
            connection.commit()
            complete_pipeline_run(
                connection, run_id,
                rows_read=len(df),
                rows_loaded=len(df),
                rows_rejected=0,
            )
            print(f"Loaded {len(df):,} rows into stg.CarListing")
        except Exception as ex:
            connection.rollback()
            fail_pipeline_run(connection, run_id, str(ex))
            raise


if __name__ == "__main__":
    load_car_listings()
