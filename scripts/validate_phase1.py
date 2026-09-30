from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    (
        "Primary car listing dataset",
        PROJECT_ROOT
        / "data"
        / "raw"
        / "car_listings"
        / "Australian Vehicle Prices.csv"
    ),
    (
        "Location reference dataset",
        PROJECT_ROOT
        / "data"
        / "raw"
        / "locations"
        / "australian_postcodes.csv"
    ),
    (
        "Source register",
        PROJECT_ROOT
        / "docs"
        / "data_source_register.csv"
    ),
    (
        "Dataset inventory",
        PROJECT_ROOT
        / "docs"
        / "dataset_inventory.csv"
    ),
    (
        "Source-to-target mapping",
        PROJECT_ROOT
        / "docs"
        / "source_to_target_mapping.md"
    ),
    (
        "Integration strategy",
        PROJECT_ROOT
        / "docs"
        / "source_integration_strategy.md"
    ),
    (
        "Raw-data manifest",
        PROJECT_ROOT
        / "data"
        / "raw"
        / "raw_data_manifest.csv"
    ),
    (
        "Phase 1 baseline",
        PROJECT_ROOT
        / "reports"
        / "profiling"
        / "phase1_data_quality_baseline.md"
    ),
]


def main():
    failures = 0

    print(
        "=== PHASE 1 VALIDATION ===\n"
    )

    for label, path in (
        REQUIRED_FILES
    ):
        if path.exists():
            print(
                f"PASS  {label}"
            )
        else:
            print(
                f"FAIL  {label}"
            )
            print(
                f"      Missing: {path}"
            )
            failures += 1

    vehicle_dir = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "vehicle_specs"
    )

    vehicle_files = list(
        vehicle_dir.glob("*.csv")
    )

    if vehicle_files:
        print(
            "PASS  Vehicle "
            "specification source "
            f"({len(vehicle_files)} CSV file(s))"
        )
    else:
        print(
            "FAIL  Vehicle "
            "specification source"
        )
        print(
            "      Add Green Vehicle "
            "Guide CSV export(s)."
        )
        failures += 1

    if failures:
        print(
            f"\nPhase 1 validation "
            f"FAILED with "
            f"{failures} issue(s)."
        )
        sys.exit(1)

    print(
        "\nPhase 1 validation PASSED."
    )


if __name__ == "__main__":
    main()
