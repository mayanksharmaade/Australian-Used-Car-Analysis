from __future__ import annotations

from etl.common.db import get_connection


def match_locations():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE curated.CarListingLocationMatch;")

        cursor.execute(
            """
            ;WITH Candidate AS
            (
                SELECT
                    c.CarListingId,
                    l.LocationId,
                    CASE
                        WHEN c.PostcodeRaw IS NOT NULL
                         AND c.PostcodeRaw = l.Postcode
                            THEN 100
                        WHEN c.SuburbRaw IS NOT NULL
                         AND c.SuburbNormalized = l.SuburbNormalized
                         AND (c.StateCodeRaw IS NULL OR c.StateCodeRaw = l.StateCode)
                            THEN 80
                        ELSE 0
                    END AS MatchScore,
                    CASE
                        WHEN c.PostcodeRaw IS NOT NULL
                         AND c.PostcodeRaw = l.Postcode
                            THEN 'POSTCODE'
                        WHEN c.SuburbRaw IS NOT NULL
                         AND c.SuburbNormalized = l.SuburbNormalized
                            THEN 'SUBURB_STATE'
                        ELSE 'NO_MATCH'
                    END AS MatchMethod,
                    ROW_NUMBER() OVER
                    (
                        PARTITION BY c.CarListingId
                        ORDER BY
                            CASE
                                WHEN c.PostcodeRaw IS NOT NULL
                                 AND c.PostcodeRaw = l.Postcode THEN 100
                                WHEN c.SuburbRaw IS NOT NULL
                                 AND c.SuburbNormalized = l.SuburbNormalized
                                 AND (c.StateCodeRaw IS NULL OR c.StateCodeRaw = l.StateCode)
                                    THEN 80
                                ELSE 0
                            END DESC,
                            l.LocationId
                    ) AS rn
                FROM curated.CarListing c
                INNER JOIN curated.Location l
                    ON (
                        c.PostcodeRaw IS NOT NULL
                        AND c.PostcodeRaw = l.Postcode
                    )
                    OR (
                        c.SuburbRaw IS NOT NULL
                        AND c.SuburbNormalized = l.SuburbNormalized
                        AND (c.StateCodeRaw IS NULL OR c.StateCodeRaw = l.StateCode)
                    )
            )
            INSERT INTO curated.CarListingLocationMatch
            (
                CarListingId,
                LocationId,
                MatchScore,
                MatchMethod,
                MatchedAtUtc
            )
            SELECT
                CarListingId,
                LocationId,
                MatchScore,
                MatchMethod,
                SYSUTCDATETIME()
            FROM Candidate
            WHERE rn = 1
              AND MatchScore > 0;
            """
        )
        connection.commit()
        cursor.execute("SELECT COUNT(*) FROM curated.CarListingLocationMatch;")
        count = cursor.fetchone()[0]
        print(f"Matched {count:,} listings to locations.")


if __name__ == "__main__":
    match_locations()
