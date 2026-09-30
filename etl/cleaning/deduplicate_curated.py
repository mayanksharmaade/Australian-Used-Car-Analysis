from __future__ import annotations

from etl.common.db import get_connection


def deduplicate_curated():
    """
    Remove exact analytical duplicates while retaining the lowest surrogate key.

    Car listings:
      make + model + year + price + kilometres + title + location

    Vehicle specs:
      make + model + variant + year + engine + transmission + fuel

    Locations:
      suburb + state + postcode + latitude + longitude
    """
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            ;WITH Duplicates AS
            (
                SELECT
                    CarListingId,
                    ROW_NUMBER() OVER
                    (
                        PARTITION BY
                            ISNULL(MakeNormalized, ''),
                            ISNULL(ModelNormalized, ''),
                            ISNULL(ModelYear, -1),
                            ISNULL(ListingPrice, -1),
                            ISNULL(Kilometres, -1),
                            ISNULL(Title, ''),
                            ISNULL(LocationRaw, '')
                        ORDER BY CarListingId
                    ) AS rn
                FROM curated.CarListing
            )
            DELETE c
            FROM curated.CarListing c
            INNER JOIN Duplicates d
                ON c.CarListingId = d.CarListingId
            WHERE d.rn > 1;
            """
        )
        car_deleted = cursor.rowcount

        cursor.execute(
            """
            ;WITH Duplicates AS
            (
                SELECT
                    VehicleSpecificationId,
                    ROW_NUMBER() OVER
                    (
                        PARTITION BY
                            ISNULL(MakeNormalized, ''),
                            ISNULL(ModelNormalized, ''),
                            ISNULL(Variant, ''),
                            ISNULL(ModelYear, -1),
                            ISNULL(EngineDescription, ''),
                            ISNULL(Transmission, ''),
                            ISNULL(FuelType, '')
                        ORDER BY VehicleSpecificationId
                    ) AS rn
                FROM curated.VehicleSpecification
            )
            DELETE v
            FROM curated.VehicleSpecification v
            INNER JOIN Duplicates d
                ON v.VehicleSpecificationId = d.VehicleSpecificationId
            WHERE d.rn > 1;
            """
        )
        spec_deleted = cursor.rowcount

        cursor.execute(
            """
            ;WITH Duplicates AS
            (
                SELECT
                    LocationId,
                    ROW_NUMBER() OVER
                    (
                        PARTITION BY
                            ISNULL(SuburbNormalized, ''),
                            ISNULL(StateCode, ''),
                            ISNULL(Postcode, ''),
                            ISNULL(Latitude, 0),
                            ISNULL(Longitude, 0)
                        ORDER BY LocationId
                    ) AS rn
                FROM curated.Location
            )
            DELETE l
            FROM curated.Location l
            INNER JOIN Duplicates d
                ON l.LocationId = d.LocationId
            WHERE d.rn > 1;
            """
        )
        location_deleted = cursor.rowcount

        connection.commit()

        print(
            "Deduplication complete: "
            f"car listings={car_deleted}, "
            f"vehicle specs={spec_deleted}, "
            f"locations={location_deleted}"
        )


if __name__ == "__main__":
    deduplicate_curated()
