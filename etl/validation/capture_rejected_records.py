from __future__ import annotations

import json

from etl.common.db import get_connection


def capture_rejected_records():
    """
    Record analytically unusable records without deleting raw staging rows.

    Rejection here means "not suitable for the core analytical fact table",
    not "delete from source history".
    """
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM audit.RejectedRecord
            WHERE SourceName IN
            (
                'Australian Vehicle Prices',
                'Green Vehicle Guide',
                'Australian Postcodes'
            );
            """
        )

        cursor.execute(
            """
            INSERT INTO audit.RejectedRecord
            (
                PipelineRunId, SourceName, SourceFileName, SourceRowNumber,
                ReasonCode, ReasonDetail, RawPayload, RejectedAtUtc
            )
            SELECT
                PipelineRunId,
                'Australian Vehicle Prices',
                SourceFileName,
                SourceRowNumber,
                CASE
                    WHEN NULLIF(LTRIM(RTRIM(BrandRaw)), '') IS NULL THEN 'MISSING_MAKE'
                    WHEN NULLIF(LTRIM(RTRIM(ModelRaw)), '') IS NULL THEN 'MISSING_MODEL'
                    ELSE 'INVALID_CORE_LISTING'
                END,
                'Core listing record is missing make or model.',
                CONCAT(
                    '{"BrandRaw":"', REPLACE(ISNULL(BrandRaw,''), '"', '\"'),
                    '","ModelRaw":"', REPLACE(ISNULL(ModelRaw,''), '"', '\"'),
                    '","PriceRaw":"', REPLACE(ISNULL(PriceRaw,''), '"', '\"'), '"}'
                ),
                SYSUTCDATETIME()
            FROM stg.CarListing
            WHERE NULLIF(LTRIM(RTRIM(BrandRaw)), '') IS NULL
               OR NULLIF(LTRIM(RTRIM(ModelRaw)), '') IS NULL;
            """
        )
        car_rejected = cursor.rowcount

        cursor.execute(
            """
            INSERT INTO audit.RejectedRecord
            (
                PipelineRunId, SourceName, SourceFileName, SourceRowNumber,
                ReasonCode, ReasonDetail, RawPayload, RejectedAtUtc
            )
            SELECT
                PipelineRunId,
                'Green Vehicle Guide',
                SourceFileName,
                SourceRowNumber,
                'MISSING_MAKE_OR_MODEL',
                'Vehicle specification cannot participate in make/model matching.',
                RawJson,
                SYSUTCDATETIME()
            FROM stg.VehicleSpecification
            WHERE NULLIF(LTRIM(RTRIM(MakeRaw)), '') IS NULL
               OR NULLIF(LTRIM(RTRIM(ModelRaw)), '') IS NULL;
            """
        )
        spec_rejected = cursor.rowcount

        cursor.execute(
            """
            INSERT INTO audit.RejectedRecord
            (
                PipelineRunId, SourceName, SourceFileName, SourceRowNumber,
                ReasonCode, ReasonDetail, RawPayload, RejectedAtUtc
            )
            SELECT
                PipelineRunId,
                'Australian Postcodes',
                SourceFileName,
                SourceRowNumber,
                'MISSING_LOCATION_KEY',
                'Location record is missing postcode and locality.',
                CONCAT(
                    '{"LocalityRaw":"', REPLACE(ISNULL(LocalityRaw,''), '"', '\"'),
                    '","PostcodeRaw":"', REPLACE(ISNULL(PostcodeRaw,''), '"', '\"'), '"}'
                ),
                SYSUTCDATETIME()
            FROM stg.Location
            WHERE NULLIF(LTRIM(RTRIM(PostcodeRaw)), '') IS NULL
              AND NULLIF(LTRIM(RTRIM(LocalityRaw)), '') IS NULL;
            """
        )
        location_rejected = cursor.rowcount

        connection.commit()

        print(
            "Rejected-record capture complete: "
            f"listings={car_rejected}, specs={spec_rejected}, locations={location_rejected}"
        )


if __name__ == "__main__":
    capture_rejected_records()
