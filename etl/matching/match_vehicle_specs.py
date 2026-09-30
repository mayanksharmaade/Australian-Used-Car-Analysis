from __future__ import annotations

from etl.common.db import get_connection


def match_vehicle_specs():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE curated.CarListingVehicleMatch;")

        cursor.execute(
            """
            ;WITH Candidate AS
            (
                SELECT
                    c.CarListingId,
                    v.VehicleSpecificationId,
                    CASE
                        WHEN c.MakeNormalized = v.MakeNormalized
                         AND c.ModelNormalized = v.ModelNormalized
                         AND c.ModelYear = v.ModelYear
                            THEN 100
                        WHEN c.MakeNormalized = v.MakeNormalized
                         AND c.ModelNormalized = v.ModelNormalized
                            THEN 80
                        ELSE 0
                    END AS MatchScore,
                    CASE
                        WHEN c.MakeNormalized = v.MakeNormalized
                         AND c.ModelNormalized = v.ModelNormalized
                         AND c.ModelYear = v.ModelYear
                            THEN 'MAKE_MODEL_YEAR'
                        WHEN c.MakeNormalized = v.MakeNormalized
                         AND c.ModelNormalized = v.ModelNormalized
                            THEN 'MAKE_MODEL'
                        ELSE 'NO_MATCH'
                    END AS MatchMethod,
                    ROW_NUMBER() OVER
                    (
                        PARTITION BY c.CarListingId
                        ORDER BY
                            CASE
                                WHEN c.MakeNormalized = v.MakeNormalized
                                 AND c.ModelNormalized = v.ModelNormalized
                                 AND c.ModelYear = v.ModelYear THEN 100
                                WHEN c.MakeNormalized = v.MakeNormalized
                                 AND c.ModelNormalized = v.ModelNormalized THEN 80
                                ELSE 0
                            END DESC,
                            v.VehicleSpecificationId
                    ) AS rn
                FROM curated.CarListing c
                INNER JOIN curated.VehicleSpecification v
                    ON c.MakeNormalized = v.MakeNormalized
                   AND c.ModelNormalized = v.ModelNormalized
            )
            INSERT INTO curated.CarListingVehicleMatch
            (
                CarListingId,
                VehicleSpecificationId,
                MatchScore,
                MatchMethod,
                MatchedAtUtc
            )
            SELECT
                CarListingId,
                VehicleSpecificationId,
                MatchScore,
                MatchMethod,
                SYSUTCDATETIME()
            FROM Candidate
            WHERE rn = 1
              AND MatchScore > 0;
            """
        )
        connection.commit()
        cursor.execute("SELECT COUNT(*) FROM curated.CarListingVehicleMatch;")
        count = cursor.fetchone()[0]
        print(f"Matched {count:,} listings to vehicle specifications.")


if __name__ == "__main__":
    match_vehicle_specs()
