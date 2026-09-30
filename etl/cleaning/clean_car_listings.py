from __future__ import annotations

import re
import pandas as pd

from etl.common.db import get_connection
from etl.common.text_utils import (
    clean_text, normalize_key, parse_integer, parse_price, parse_fuel_consumption
)


def split_location(value):
    text = clean_text(value)
    if not text:
        return None, None, None
    # Common source examples are suburb, state. Postcode may or may not be present.
    parts = [p.strip() for p in re.split(r"[,|]", text) if p.strip()]
    postcode_match = re.search(r"\b(\d{4})\b", text)
    postcode = postcode_match.group(1) if postcode_match else None
    state = None
    for token in parts:
        if token.upper() in {"ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA"}:
            state = token.upper()
            break
    suburb = parts[0] if parts else text
    return suburb, state, postcode


def clean_car_listings():
    with get_connection() as connection:
        df = pd.read_sql_query("SELECT * FROM stg.CarListing;", connection)

        records = []
        for row in df.itertuples(index=False):
            suburb, state, postcode = split_location(row.LocationRaw)
            make = clean_text(row.BrandRaw)
            model = clean_text(row.ModelRaw)
            records.append((
                row.CarListingStagingId,
                make,
                normalize_key(make),
                parse_integer(row.YearRaw),
                model,
                normalize_key(model),
                clean_text(row.CarSuvRaw),
                clean_text(row.TitleRaw),
                clean_text(row.UsedOrNewRaw),
                clean_text(row.TransmissionRaw),
                clean_text(row.EngineRaw),
                clean_text(row.DriveTypeRaw),
                clean_text(row.FuelTypeRaw),
                parse_fuel_consumption(row.FuelConsumptionRaw),
                parse_integer(row.KilometresRaw),
                clean_text(row.ColourExtIntRaw),
                clean_text(row.LocationRaw),
                clean_text(suburb),
                normalize_key(suburb),
                state,
                postcode,
                parse_integer(row.CylindersInEngineRaw),
                clean_text(row.BodyTypeRaw),
                parse_integer(row.DoorsRaw),
                parse_integer(row.SeatsRaw),
                parse_price(row.PriceRaw),
                row.PriceRaw,
                row.SourceFileName,
                row.PipelineRunId,
            ))

        cursor = connection.cursor()
        cursor.execute("DELETE FROM  curated.CarListing;")
        cursor.fast_executemany = True
        cursor.executemany(
            """
            INSERT INTO curated.CarListing
            (
                CarListingStagingId, Make, MakeNormalized, ModelYear, Model, ModelNormalized,
                CarSuv, Title, VehicleCondition, Transmission, EngineDescription, DriveType,
                FuelType, FuelConsumptionLPer100Km, Kilometres, ColourExtInt, LocationRaw,
                SuburbRaw, SuburbNormalized, StateCodeRaw, PostcodeRaw, CylinderCount, BodyType, Doors, Seats,
                ListingPrice, ListingPriceRaw, SourceFileName, PipelineRunId
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            records,
        )
        connection.commit()
        print(f"Cleaned {len(records):,} car listings into curated.CarListing")


if __name__ == "__main__":
    clean_car_listings()
