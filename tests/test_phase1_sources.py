from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CAR_FILE = (
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


def test_car_source_if_present_is_readable():
    if CAR_FILE.exists():
        df = pd.read_csv(
            CAR_FILE,
            nrows=10,
            low_memory=False
        )

        assert len(df) > 0


def test_location_source_if_present_has_expected_columns():
    if LOCATION_FILE.exists():
        df = pd.read_csv(
            LOCATION_FILE,
            nrows=10,
            low_memory=False
        )

        columns = {
            str(c).lower().strip()
            for c in df.columns
        }

        expected = {
            "locality",
            "state",
            "postcode",
            "latitude",
            "longitude",
        }

        assert expected.issubset(
            columns
        )
