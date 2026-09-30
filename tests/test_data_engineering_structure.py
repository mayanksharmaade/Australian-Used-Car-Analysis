from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "etl/staging/load_car_listings.py",
    "etl/staging/load_vehicle_specs.py",
    "etl/staging/load_locations.py",
    "etl/cleaning/clean_car_listings.py",
    "etl/cleaning/clean_vehicle_specs.py",
    "etl/cleaning/clean_locations.py",
    "etl/cleaning/deduplicate_curated.py",
    "etl/validation/capture_rejected_records.py",
    "etl/matching/match_vehicle_specs.py",
    "etl/matching/match_locations.py",
    "etl/warehouse/load_dimensions.py",
    "etl/warehouse/load_fact_car_listing.py",
    "etl/pipeline/run_data_pipeline.py",
    "scripts/setup_data_engineering_database.py",
    "sql/staging/010_create_production_staging_tables.sql",
    "sql/curated/001_create_curated_tables.sql",
    "sql/warehouse/001_create_dimensions.sql",
    "sql/warehouse/002_create_fact_car_listing.sql",
]


def test_required_files_exist():
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    assert not missing, f"Missing Data Engineering files: {missing}"
