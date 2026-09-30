from __future__ import annotations

import pandas as pd

from etl.common.db import get_connection
from etl.common.text_utils import clean_text, normalize_key, parse_integer, parse_decimal


def clean_vehicle_specs():
    with get_connection() as connection:
        df = pd.read_sql_query("SELECT * FROM stg.VehicleSpecification;", connection)
        records = []

        for row in df.itertuples(index=False):
            make = clean_text(row.MakeRaw)
            model = clean_text(row.ModelRaw)
            records.append((
                row.VehicleSpecificationStagingId,
                make,
                normalize_key(make),
                model,
                normalize_key(model),
                clean_text(row.VariantRaw),
                parse_integer(row.ModelYearRaw),
                clean_text(row.BodyStyleRaw),
                clean_text(row.EngineRaw),
                clean_text(row.TransmissionRaw),
                clean_text(row.FuelTypeRaw),
                clean_text(row.DriveTypeRaw),
                parse_integer(row.SeatsRaw),
                parse_decimal(row.FuelConsumptionRaw),
                parse_decimal(row.CO2Raw),
                row.SourceFileName,
                row.PipelineRunId,
            ))

        cursor = connection.cursor()
        cursor.execute("DELETE FROM  curated.VehicleSpecification;")
        cursor.fast_executemany = True
        cursor.executemany(
            """
            INSERT INTO curated.VehicleSpecification
            (
                VehicleSpecificationStagingId, Make, MakeNormalized, Model, ModelNormalized,
                Variant, ModelYear, BodyStyle, EngineDescription, Transmission, FuelType,
                DriveType, Seats, FuelConsumptionLPer100Km, CO2GPerKm,
                SourceFileName, PipelineRunId
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            records,
        )
        connection.commit()
        print(f"Cleaned {len(records):,} vehicle specifications into curated.VehicleSpecification")


if __name__ == "__main__":
    clean_vehicle_specs()
