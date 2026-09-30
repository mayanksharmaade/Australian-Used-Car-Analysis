from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_phase1_folder_structure():
    required = [
        "data/raw/car_listings",
        "data/raw/vehicle_specs",
        "data/raw/locations",
        "data/raw/economic",
        "ingestion/profiling",
        "docs",
        "reports/profiling/car_listings",
        "reports/profiling/vehicle_specs",
        "reports/profiling/locations",
    ]

    for relative_path in required:
        assert (
            PROJECT_ROOT
            / relative_path
        ).exists()


def test_phase1_scripts_exist():
    required = [
        "ingestion/profiling/01_profile_car_listings.py",
        "ingestion/profiling/02_profile_vehicle_specs.py",
        "ingestion/profiling/03_profile_location_data.py",
        "ingestion/profiling/04_check_temporal_fields.py",
        "scripts/build_raw_data_manifest.py",
        "scripts/build_dataset_inventory.py",
        "scripts/generate_phase1_baseline.py",
        "scripts/validate_phase1.py",
    ]

    for relative_path in required:
        assert (
            PROJECT_ROOT
            / relative_path
        ).exists()
