from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "profiling"
)

OUTPUT_FILE = (
    REPORT_DIR
    / "phase1_data_quality_baseline.md"
)

LISTING_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "car_listings"
    / "Australian Vehicle Prices.csv"
)

LOCATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "locations"
    / "australian_postcodes.csv"
)

VEHICLE_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "vehicle_specs"
)


def profile_csv(path):
    df = pd.read_csv(
        path,
        low_memory=False
    )

    total_cells = (
        len(df)
        * len(df.columns)
    )

    duplicates = int(
        df.duplicated().sum()
    )

    missing_cells = int(
        df.isna().sum().sum()
    )

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "duplicates": duplicates,
        "duplicate_pct": (
            duplicates
            / len(df)
            * 100
            if len(df)
            else 0
        ),
        "missing_pct": (
            missing_cells
            / total_cells
            * 100
            if total_cells
            else 0
        ),
    }


def add_dataset_section(
    lines,
    name,
    path
):
    lines.extend([
        f"## {name}",
        "",
    ])

    if not path.exists():
        lines.extend([
            "**Status:** File not found",
            "",
            f"`{path}`",
            "",
        ])
        return

    profile = profile_csv(path)

    lines.extend([
        f"- Rows: {profile['rows']:,}",
        f"- Columns: {profile['columns']:,}",
        (
            "- Duplicate rows: "
            f"{profile['duplicates']:,}"
        ),
        (
            "- Duplicate percentage: "
            f"{profile['duplicate_pct']:.2f}%"
        ),
        (
            "- Overall missing-cell percentage: "
            f"{profile['missing_pct']:.2f}%"
        ),
        "",
    ])


def main():
    lines = [
        "# Phase 1 Data Quality Baseline",
        "",
        (
            "Raw-data baseline captured before "
            "Phase 2 transformations."
        ),
        "",
    ]

    add_dataset_section(
        lines,
        "Australian Vehicle Prices",
        LISTING_FILE
    )

    add_dataset_section(
        lines,
        "Australian Location Reference",
        LOCATION_FILE
    )

    lines.extend([
        "## Vehicle Specification Source",
        "",
    ])

    vehicle_files = sorted(
        VEHICLE_DIR.glob("*.csv")
    )

    if vehicle_files:
        total_rows = 0

        for path in vehicle_files:
            df = pd.read_csv(
                path,
                low_memory=False
            )

            total_rows += len(df)

            lines.append(
                f"- {path.name}: "
                f"{len(df):,} rows, "
                f"{len(df.columns)} columns"
            )

        lines.append(
            f"- Combined rows: "
            f"{total_rows:,}"
        )

    else:
        lines.append(
            "- No vehicle specification "
            "CSV has been added yet."
        )

    lines.extend([
        "",
        "## Candidate joins",
        "",
        (
            "- Listings → vehicle specs: "
            "Make + Model + ModelYear "
            "(+ Variant where possible)"
        ),
        (
            "- Listings → location reference: "
            "parsed Listing.Location "
            "→ locality + state"
        ),
        "",
        "## Phase 2 actions",
        "",
        (
            "- Design SQL staging schemas "
            "from the real source fields."
        ),
        "- Build raw-to-staging loaders.",
        "- Add data-quality rules.",
        "- Add rejected-record handling.",
        "- Normalize make/model/location.",
        "- Measure enrichment match rates.",
    ])

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print(
        f"Baseline report created: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
