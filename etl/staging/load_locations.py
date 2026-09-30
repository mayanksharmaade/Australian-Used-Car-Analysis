from __future__ import annotations

from pathlib import Path
import json
import pandas as pd

from etl.common.audit import start_pipeline_run, complete_pipeline_run, fail_pipeline_run
from etl.common.db import get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_FILE = PROJECT_ROOT / "data" / "raw" / "locations" / "australian_postcodes.csv"


def _column(df, name):
    lookup = {str(c).strip().lower(): c for c in df.columns}
    return lookup.get(name.lower())


def load_locations():
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(SOURCE_FILE)

    df = pd.read_csv(SOURCE_FILE, dtype=str, keep_default_na=False, low_memory=False)
    required = [
    "state",
    "postcode",
    "count",
    "latitude",
    "longitude",
]
    missing = [c for c in required if _column(df, c) is None]
    if missing:
        raise ValueError(f"Location source is missing columns: {missing}")

    count_col = _column(df, "count")
    if "locality" not in df.columns:
        df["locality"] = None

    with get_connection() as connection:
        run_id = start_pipeline_run(connection, "LoadLocations", "Australian Postcodes")
        try:
            cursor = connection.cursor()
            cursor.fast_executemany = True
            cursor.execute("TRUNCATE TABLE stg.Location;")

            sql = """
            INSERT INTO stg.Location
            (
                SourceRowNumber, LocalityRaw, StateRaw, PostcodeRaw, AddressCountRaw,
                LatitudeRaw, LongitudeRaw, SourceFileName, PipelineRunId
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """

            rows = []
            for idx, row in df.iterrows():
                rows.append((
                    idx + 2,
                    row[_column(df, "locality")],
                    row[_column(df, "state")],
                    row[_column(df, "postcode")],
                    row[count_col] if count_col else None,
                    row[_column(df, "latitude")],
                    row[_column(df, "longitude")],
                    SOURCE_FILE.name,
                    run_id,
                ))

            cursor.executemany(sql, rows)
            connection.commit()
            complete_pipeline_run(connection, run_id, rows_read=len(df), rows_loaded=len(df))
            print(f"Loaded {len(df):,} rows into stg.Location")
        except Exception as ex:
            connection.rollback()
            fail_pipeline_run(connection, run_id, str(ex))
            raise


if __name__ == "__main__":
    load_locations()
