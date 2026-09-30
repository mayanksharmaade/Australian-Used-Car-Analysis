from __future__ import annotations

from etl.common.db import get_connection


def load_fact_car_listing():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM dw.FactCarListing;")

        cursor.execute(
            """
            ;WITH Resolved AS
            (
                SELECT
                    c.CarListingId,
                    dv.VehicleKey,
                    dl.LocationKey,
                    c.ListingPrice,
                    c.Kilometres,
                    c.FuelConsumptionLPer100Km,
                    vm.VehicleSpecificationId,
                    vm.MatchScore AS VehicleMatchScore,
                    lm.MatchScore AS LocationMatchScore,
                    c.SourceFileName,
                    c.PipelineRunId,
                    ROW_NUMBER() OVER
                    (
                        PARTITION BY c.CarListingId
                        ORDER BY dv.VehicleKey
                    ) AS rn
                FROM curated.CarListing c
                INNER JOIN dw.DimMake dma
                    ON c.MakeNormalized = dma.MakeNormalized
                INNER JOIN dw.DimModel dmo
                    ON dmo.MakeKey = dma.MakeKey
                   AND c.ModelNormalized = dmo.ModelNormalized
                LEFT JOIN dw.DimVehicle dv
                    ON dv.ModelKey = dmo.ModelKey
                   AND ISNULL(dv.ModelYear, -1) = ISNULL(c.ModelYear, -1)
                   AND ISNULL(dv.BodyType, '') = ISNULL(c.BodyType, '')
                   AND ISNULL(dv.Transmission, '') = ISNULL(c.Transmission, '')
                   AND ISNULL(dv.FuelType, '') = ISNULL(c.FuelType, '')
                   AND ISNULL(dv.DriveType, '') = ISNULL(c.DriveType, '')
                   AND ISNULL(dv.CylinderCount, -1) = ISNULL(c.CylinderCount, -1)
                   AND ISNULL(dv.Doors, -1) = ISNULL(c.Doors, -1)
                   AND ISNULL(dv.Seats, -1) = ISNULL(c.Seats, -1)
                LEFT JOIN curated.CarListingVehicleMatch vm
                    ON vm.CarListingId = c.CarListingId
                LEFT JOIN curated.CarListingLocationMatch lm
                    ON lm.CarListingId = c.CarListingId
                LEFT JOIN dw.DimLocation dl
                    ON dl.CuratedLocationId = lm.LocationId
            )
            INSERT INTO dw.FactCarListing
            (
                CarListingId,
                VehicleKey,
                LocationKey,
                ListingPrice,
                Kilometres,
                FuelConsumptionLPer100Km,
                VehicleSpecificationId,
                VehicleMatchScore,
                LocationMatchScore,
                SourceFileName,
                PipelineRunId
            )
            SELECT
                CarListingId,
                VehicleKey,
                LocationKey,
                ListingPrice,
                Kilometres,
                FuelConsumptionLPer100Km,
                VehicleSpecificationId,
                VehicleMatchScore,
                LocationMatchScore,
                SourceFileName,
                PipelineRunId
            FROM Resolved
            WHERE rn = 1;
            """
        )

        connection.commit()
        cursor.execute("SELECT COUNT(*) FROM dw.FactCarListing;")
        count = cursor.fetchone()[0]
        print(f"Loaded {count:,} rows into dw.FactCarListing")


if __name__ == "__main__":
    load_fact_car_listing()
