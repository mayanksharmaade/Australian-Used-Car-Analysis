from __future__ import annotations

from pathlib import Path
import pandas as pd

from etl.common.db import get_connection

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "reports" / "data_engineering" / "match_quality"


def assess_match_quality():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        summary = pd.read_sql_query(
            """
            SELECT
                (SELECT COUNT(*) FROM curated.CarListing) AS TotalListings,
                (SELECT COUNT(*) FROM curated.CarListingVehicleMatch) AS VehicleSpecMatches,
                (SELECT COUNT(*) FROM curated.CarListingLocationMatch) AS LocationMatches;
            """,
            connection,
        )

        vehicle_methods = pd.read_sql_query(
            """
            SELECT MatchMethod, COUNT(*) AS MatchCount, AVG(CAST(MatchScore AS DECIMAL(10,2))) AS AvgScore
            FROM curated.CarListingVehicleMatch
            GROUP BY MatchMethod
            ORDER BY MatchCount DESC;
            """,
            connection,
        )

        location_methods = pd.read_sql_query(
            """
            SELECT MatchMethod, COUNT(*) AS MatchCount, AVG(CAST(MatchScore AS DECIMAL(10,2))) AS AvgScore
            FROM curated.CarListingLocationMatch
            GROUP BY MatchMethod
            ORDER BY MatchCount DESC;
            """,
            connection,
        )

    total = int(summary.loc[0, "TotalListings"] or 0)
    vehicle = int(summary.loc[0, "VehicleSpecMatches"] or 0)
    location = int(summary.loc[0, "LocationMatches"] or 0)
    summary["VehicleSpecMatchPct"] = round(vehicle * 100 / total, 2) if total else 0
    summary["LocationMatchPct"] = round(location * 100 / total, 2) if total else 0

    summary.to_csv(REPORT_DIR / "match_summary.csv", index=False)
    vehicle_methods.to_csv(REPORT_DIR / "vehicle_match_methods.csv", index=False)
    location_methods.to_csv(REPORT_DIR / "location_match_methods.csv", index=False)

    print(summary.to_string(index=False))


if __name__ == "__main__":
    assess_match_quality()
