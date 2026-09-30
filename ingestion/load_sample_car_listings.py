from pathlib import Path
import pandas as pd
import pyodbc

from config.settings import build_connection_string

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "car_listings"
    / "sample_car_listings.csv"
)

REQUIRED_COLUMNS = [
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
]

VALID_STATES = {
    "SA", "NSW", "VIC", "QLD",
    "WA", "TAS", "ACT", "NT"
}


def validate(df):
    missing = [
        c for c in REQUIRED_COLUMNS
        if c not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    for col in ["Make", "Model", "StateCode"]:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
        )

    df["ModelYear"] = pd.to_numeric(
        df["ModelYear"], errors="raise"
    ).astype(int)

    df["ListingPrice"] = pd.to_numeric(
        df["ListingPrice"], errors="raise"
    )

    df["Kilometres"] = pd.to_numeric(
        df["Kilometres"], errors="raise"
    ).astype(int)

    df["ListingDate"] = pd.to_datetime(
        df["ListingDate"], errors="raise"
    ).dt.date

    if df["Make"].isna().any():
        raise ValueError("Make cannot be null.")

    if df["Model"].isna().any():
        raise ValueError("Model cannot be null.")

    if (df["ListingPrice"] <= 0).any():
        raise ValueError(
            "ListingPrice must be greater than zero."
        )

    if (df["Kilometres"] < 0).any():
        raise ValueError(
            "Kilometres cannot be negative."
        )

    states = set(
        df["StateCode"].dropna().astype(str)
    )

    if not states.issubset(VALID_STATES):
        raise ValueError(
            f"Invalid StateCode(s): {states - VALID_STATES}"
        )

    return df


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Sample file missing: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)
    df = validate(df)

    insert_sql = """
    INSERT INTO stg.CarListing
    (
        SourceListingId,
        Make,
        Model,
        ModelYear,
        ListingPrice,
        Kilometres,
        StateCode,
        City,
        Postcode,
        BodyType,
        Transmission,
        FuelType,
        EngineDescription,
        ListingDate,
        SourceName
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    with pyodbc.connect(
        build_connection_string()
    ) as conn:

        cursor = conn.cursor()

        for row in df[REQUIRED_COLUMNS].itertuples(
            index=False,
            name=None
        ):
            cursor.execute(insert_sql, row)

        conn.commit()

    print(
        f"Loaded {len(df):,} sample row(s) "
        "into stg.CarListing."
    )


if __name__ == "__main__":
    main()
