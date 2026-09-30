from __future__ import annotations

from etl.common.db import get_connection


def reconcile_pipeline():
    queries = {
        "stg.CarListing": "SELECT COUNT(*) FROM stg.CarListing;",
        "curated.CarListing": "SELECT COUNT(*) FROM curated.CarListing;",
        "dw.FactCarListing": "SELECT COUNT(*) FROM dw.FactCarListing;",
        "stg.VehicleSpecification": "SELECT COUNT(*) FROM stg.VehicleSpecification;",
        "curated.VehicleSpecification": "SELECT COUNT(*) FROM curated.VehicleSpecification;",
        "stg.Location": "SELECT COUNT(*) FROM stg.Location;",
        "curated.Location": "SELECT COUNT(*) FROM curated.Location;",
    }

    with get_connection() as connection:
        cursor = connection.cursor()
        counts = {}

        for name, sql in queries.items():
            cursor.execute(sql)
            counts[name] = cursor.fetchone()[0]

    print("PIPELINE RECONCILIATION")
    print("-" * 60)

    for name, value in counts.items():
        print(f"{name:<35} {value:,}")

    # ---------------------------------------------------------
    # Car listing reconciliation
    # ---------------------------------------------------------

    staging_car_count = counts["stg.CarListing"]
    curated_car_count = counts["curated.CarListing"]
    fact_car_count = counts["dw.FactCarListing"]

    # Cleaning/deduplication can legitimately reduce the number
    # of records, but curated should never contain MORE records
    # than staging.
    if curated_car_count > staging_car_count:
        raise AssertionError(
            "Curated car listing count cannot exceed staging count."
        )

    # The warehouse fact table should never contain more records
    # than the curated source.
    if fact_car_count > curated_car_count:
        raise AssertionError(
            "Fact car listing count cannot exceed curated count."
        )

    car_cleaning_reduction = staging_car_count - curated_car_count
    fact_reduction = curated_car_count - fact_car_count

    print()
    print("CAR LISTING RECONCILIATION")
    print("-" * 60)

    print(
        f"Rows removed during cleaning/deduplication: "
        f"{car_cleaning_reduction:,}"
    )

    print(
        f"Curated rows not loaded into fact table: "
        f"{fact_reduction:,}"
    )

    # ---------------------------------------------------------
    # Location reconciliation
    # ---------------------------------------------------------

    if counts["stg.Location"] != counts["curated.Location"]:
        raise AssertionError(
            "Location staging/curated row counts differ."
        )

    print()
    print("Reconciliation checks passed.")


if __name__ == "__main__":
    reconcile_pipeline()