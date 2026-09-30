import sys
import pyodbc

from config.settings import build_connection_string

EXPECTED_COLUMNS = [
    "SourceListingId",
    "Make",
    "Model",
    "ModelYear",
    "ListingPrice",
    "Kilometres",
    "StateCode",
    "City",
    "Postcode",
    "BodyType",
    "Transmission",
    "FuelType",
    "EngineDescription",
    "ListingDate",
    "SourceName",
    "LoadedAtUtc",
]


def main():
    failures = 0

    print("=== PHASE 0 FINAL VALIDATION ===")

    try:
        with pyodbc.connect(
            build_connection_string(),
            timeout=10
        ) as conn:

            cursor = conn.cursor()

            cursor.execute(
                "SELECT @@SERVERNAME, DB_NAME()"
            )

            server_name, db_name = cursor.fetchone()

            print(f"PASS SQL Server: {server_name}")
            print(f"PASS Database:   {db_name}")

            cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'stg'
              AND TABLE_NAME = 'CarListing'
            """)

            table_exists = cursor.fetchone()[0] == 1

            if table_exists:
                print("PASS stg.CarListing exists")
            else:
                print("FAIL stg.CarListing missing")
                failures += 1

            cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'stg'
              AND TABLE_NAME = 'CarListing'
            ORDER BY ORDINAL_POSITION
            """)

            actual_columns = [
                row[0]
                for row in cursor.fetchall()
            ]

            missing_columns = [
                col
                for col in EXPECTED_COLUMNS
                if col not in actual_columns
            ]

            if missing_columns:
                print(
                    f"FAIL Missing columns: {missing_columns}"
                )
                failures += 1
            else:
                print("PASS Expected staging columns")

            if table_exists:
                cursor.execute(
                    "SELECT COUNT(*) FROM stg.CarListing"
                )

                row_count = cursor.fetchone()[0]

                print(
                    f"INFO stg.CarListing row count: {row_count}"
                )

    except Exception as exc:
        print(f"FAIL Validation exception: {exc}")
        failures += 1

    if failures:
        print(
            f"Phase 0 validation FAILED "
            f"with {failures} issue(s)."
        )
        sys.exit(1)

    print("Phase 0 validation PASSED.")


if __name__ == "__main__":
    main()
