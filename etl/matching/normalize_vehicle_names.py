from __future__ import annotations

from etl.common.db import get_connection


def apply_reference_mappings():
    """
    Applies optional manual mappings maintained in ref.MakeMapping and ref.ModelMapping.
    Empty mapping tables are valid; the normalized source values remain unchanged.
    """
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE c
            SET c.MakeNormalized = m.CanonicalMakeNormalized
            FROM curated.CarListing c
            INNER JOIN ref.MakeMapping m
                ON c.MakeNormalized = m.SourceMakeNormalized
            WHERE m.IsActive = 1;
            """
        )

        cursor.execute(
            """
            UPDATE v
            SET v.MakeNormalized = m.CanonicalMakeNormalized
            FROM curated.VehicleSpecification v
            INNER JOIN ref.MakeMapping m
                ON v.MakeNormalized = m.SourceMakeNormalized
            WHERE m.IsActive = 1;
            """
        )

        cursor.execute(
            """
            UPDATE c
            SET c.ModelNormalized = m.CanonicalModelNormalized
            FROM curated.CarListing c
            INNER JOIN ref.ModelMapping m
                ON c.MakeNormalized = m.MakeNormalized
               AND c.ModelNormalized = m.SourceModelNormalized
            WHERE m.IsActive = 1;
            """
        )

        cursor.execute(
            """
            UPDATE v
            SET v.ModelNormalized = m.CanonicalModelNormalized
            FROM curated.VehicleSpecification v
            INNER JOIN ref.ModelMapping m
                ON v.MakeNormalized = m.MakeNormalized
               AND v.ModelNormalized = m.SourceModelNormalized
            WHERE m.IsActive = 1;
            """
        )

        connection.commit()
        print("Applied reference make/model mappings.")


if __name__ == "__main__":
    apply_reference_mappings()
