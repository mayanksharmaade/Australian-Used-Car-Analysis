from __future__ import annotations

import pandas as pd

from etl.common.db import get_connection
from etl.common.text_utils import clean_text, normalize_key, parse_integer, parse_decimal


def clean_locations():
    with get_connection() as connection:
        df = pd.read_sql_query("SELECT * FROM stg.Location;", connection)
        records = []

        for row in df.itertuples(index=False):
            locality = clean_text(row.LocalityRaw)
            state = clean_text(row.StateRaw)
            postcode = clean_text(row.PostcodeRaw)
            records.append((
                row.LocationStagingId,
                locality,
                normalize_key(locality),
                state.upper() if state else None,
                postcode.zfill(4) if postcode and postcode.isdigit() else postcode,
                parse_integer(row.AddressCountRaw),
                parse_decimal(row.LatitudeRaw),
                parse_decimal(row.LongitudeRaw),
                row.SourceFileName,
                row.PipelineRunId,
            ))

        cursor = connection.cursor()
        cursor.execute("DELETE FROM  curated.Location;")
        cursor.fast_executemany = True
        cursor.executemany(
            """
            INSERT INTO curated.Location
            (
                LocationStagingId, Suburb, SuburbNormalized, StateCode, Postcode,
                AddressCount, Latitude, Longitude, SourceFileName, PipelineRunId
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            records,
        )
        connection.commit()
        print(f"Cleaned {len(records):,} locations into curated.Location")


if __name__ == "__main__":
    clean_locations()
