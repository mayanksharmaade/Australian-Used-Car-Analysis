from __future__ import annotations

from etl.staging.load_car_listings import load_car_listings
from etl.staging.load_vehicle_specs import load_vehicle_specs
from etl.staging.load_locations import load_locations
from etl.validation.validate_staging import validate_staging
from etl.validation.capture_rejected_records import capture_rejected_records
from etl.cleaning.clean_car_listings import clean_car_listings
from etl.cleaning.clean_vehicle_specs import clean_vehicle_specs
from etl.cleaning.clean_locations import clean_locations
from etl.cleaning.deduplicate_curated import deduplicate_curated
from etl.matching.normalize_vehicle_names import apply_reference_mappings
from etl.matching.match_vehicle_specs import match_vehicle_specs
from etl.matching.match_locations import match_locations
from etl.matching.assess_match_quality import assess_match_quality
from etl.warehouse.load_dimensions import load_dimensions
from etl.warehouse.load_fact_car_listing import load_fact_car_listing
from etl.validation.reconcile_pipeline import reconcile_pipeline


def run_pipeline():
    print("\n1/14 Load car listings")
    load_car_listings()

    print("\n2/14 Load vehicle specifications")
    load_vehicle_specs()

    print("\n3/14 Load locations")
    load_locations()

    print("\n4/14 Validate staging")
    validate_staging()

    print("\n5/14 Capture rejected records")
    capture_rejected_records()
from etl.common.db import get_connection

with get_connection() as connection:
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE curated.CarListingVehicleMatch;")
    cursor.execute("TRUNCATE TABLE curated.CarListingLocationMatch;")
    connection.commit()
    print("\n6/14 Clean car listings")
    clean_car_listings()

    print("\n7/14 Clean vehicle specifications")
    clean_vehicle_specs()

    print("\n8/14 Clean locations")
    clean_locations()

    print("\n9/14 Deduplicate curated data")
    deduplicate_curated()

    print("\n10/14 Apply make/model mappings")
    apply_reference_mappings()

    print("\n11/14 Match vehicle specifications")
    match_vehicle_specs()

    print("\n12/14 Match locations")
    match_locations()

    print("\n13/14 Build warehouse")
    load_dimensions()
    load_fact_car_listing()

    print("\n14/14 Validate and report")
    assess_match_quality()
    reconcile_pipeline()

    print("\nDATA ENGINEERING PIPELINE COMPLETE")

if __name__ == "__main__":
    run_pipeline()
