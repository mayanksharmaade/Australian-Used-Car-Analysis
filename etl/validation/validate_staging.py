from __future__ import annotations

from etl.common.db import get_connection


CHECKS = {
    "CarListing rows": "SELECT COUNT(*) FROM stg.CarListing;",
    "VehicleSpecification rows": "SELECT COUNT(*) FROM stg.VehicleSpecification;",
    "Location rows": "SELECT COUNT(*) FROM stg.Location;",
    "CarListing missing Brand": """
        SELECT COUNT(*) FROM stg.CarListing
        WHERE NULLIF(LTRIM(RTRIM(BrandRaw)), '') IS NULL;
    """,
    "CarListing missing Model": """
        SELECT COUNT(*) FROM stg.CarListing
        WHERE NULLIF(LTRIM(RTRIM(ModelRaw)), '') IS NULL;
    """,
    "CarListing missing Price": """
        SELECT COUNT(*) FROM stg.CarListing
        WHERE NULLIF(LTRIM(RTRIM(PriceRaw)), '') IS NULL;
    """,
}


def validate_staging():
    with get_connection() as connection:
        cursor = connection.cursor()
        print("STAGING VALIDATION")
        print("-" * 60)
        for name, sql in CHECKS.items():
            cursor.execute(sql)
            value = cursor.fetchone()[0]
            print(f"{name:<40} {value:,}" if isinstance(value, int) else f"{name:<40} {value}")


if __name__ == "__main__":
    validate_staging()
