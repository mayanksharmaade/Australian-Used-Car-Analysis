from __future__ import annotations

from etl.common.db import get_connection


def load_dimensions():
    with get_connection() as connection:
        cursor = connection.cursor()

        # ---------------------------------------------------------
        # Reset warehouse tables
        # ---------------------------------------------------------
        # Delete child/fact tables first because of foreign keys.
        cursor.execute("DELETE FROM dw.FactCarListing;")
        cursor.execute("DELETE FROM dw.DimVehicle;")
        cursor.execute("DELETE FROM dw.DimModel;")
        cursor.execute("DELETE FROM dw.DimMake;")
        cursor.execute("DELETE FROM dw.DimLocation;")

        # ---------------------------------------------------------
        # DimMake
        # ---------------------------------------------------------
        cursor.execute(
            """
            INSERT INTO dw.DimMake
            (
                MakeName,
                MakeNormalized
            )
            SELECT DISTINCT
                Make,
                MakeNormalized
            FROM curated.CarListing
            WHERE Make IS NOT NULL
              AND MakeNormalized IS NOT NULL;
            """
        )

        # ---------------------------------------------------------
        # DimModel
        # ---------------------------------------------------------
        # One row for each Make + normalized Model combination.
        # MIN(Model) provides a deterministic display value if
        # multiple source spellings exist.
        cursor.execute(
            """
            INSERT INTO dw.DimModel
            (
                MakeKey,
                ModelName,
                ModelNormalized
            )
            SELECT
                dm.MakeKey,
                MIN(c.Model) AS ModelName,
                c.ModelNormalized
            FROM curated.CarListing c
            INNER JOIN dw.DimMake dm
                ON dm.MakeNormalized = c.MakeNormalized
            WHERE c.ModelNormalized IS NOT NULL
            GROUP BY
                dm.MakeKey,
                c.ModelNormalized;
            """
        )

        # ---------------------------------------------------------
        # DimLocation
        # ---------------------------------------------------------
        cursor.execute(
            """
            INSERT INTO dw.DimLocation
            (
                CuratedLocationId,
                Suburb,
                SuburbNormalized,
                StateCode,
                Postcode,
                Latitude,
                Longitude,
                AddressCount
            )
            SELECT
                LocationId AS CuratedLocationId,
                Suburb,
                SuburbNormalized,
                StateCode,
                Postcode,
                Latitude,
                Longitude,
                AddressCount
            FROM curated.Location;
            """
        )

        # ---------------------------------------------------------
        # DimVehicle
        # ---------------------------------------------------------
        cursor.execute(
            """
            ;WITH VehicleSource AS
            (
                SELECT DISTINCT
                    dmo.ModelKey,
                    c.ModelYear,
                    c.BodyType,
                    c.Transmission,
                    c.FuelType,
                    c.DriveType,
                    c.CylinderCount,
                    c.Doors,
                    c.Seats
                FROM curated.CarListing c
                INNER JOIN dw.DimMake dma
                    ON c.MakeNormalized = dma.MakeNormalized
                INNER JOIN dw.DimModel dmo
                    ON dmo.MakeKey = dma.MakeKey
                   AND c.ModelNormalized = dmo.ModelNormalized
            )
            INSERT INTO dw.DimVehicle
            (
                ModelKey,
                ModelYear,
                BodyType,
                Transmission,
                FuelType,
                DriveType,
                CylinderCount,
                Doors,
                Seats
            )
            SELECT
                ModelKey,
                ModelYear,
                BodyType,
                Transmission,
                FuelType,
                DriveType,
                CylinderCount,
                Doors,
                Seats
            FROM VehicleSource;
            """
        )

        # ---------------------------------------------------------
        # Commit
        # ---------------------------------------------------------
        connection.commit()

        print("Loaded warehouse dimensions.")


if __name__ == "__main__":
    load_dimensions()