from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "car_listings"
    / "Australian Vehicle Prices.csv"
)

DATE_KEYWORDS = [
    "date",
    "listed",
    "listing",
    "created",
    "updated",
    "timestamp",
    "month",
    "quarter",
    "time",
]


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Add primary listings file here:\n{INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        nrows=100,
        low_memory=False
    )

    matches = [
        column
        for column in df.columns
        if any(
            keyword in column.lower()
            for keyword in DATE_KEYWORDS
        )
    ]

    print(
        "=== TEMPORAL FIELD CHECK ==="
    )

    if matches:
        print(
            "Potential temporal fields:"
        )

        for column in matches:
            print(f"- {column}")

        print(
            "\nRBA/ABS enrichment can be "
            "investigated further."
        )
    else:
        print(
            "No obvious listing/observation "
            "date field found."
        )

        print(
            "Defer RBA/ABS time-series "
            "enrichment."
        )


if __name__ == "__main__":
    main()
