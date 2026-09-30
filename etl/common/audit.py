from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def start_pipeline_run(connection, pipeline_name: str, source_name: str | None = None) -> str:
    run_id = str(uuid4())
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO audit.PipelineRun
            (
                PipelineRunId,
                PipelineName,
                SourceName,
                Status,
                StartedAtUtc
            )
            VALUES (?, ?, ?, 'Running', SYSUTCDATETIME());
            """,
            run_id,
            pipeline_name,
            source_name,
        )
        connection.commit()
    finally:
        cursor.close()
    return run_id


def complete_pipeline_run(
    connection,
    run_id: str,
    *,
    rows_read: int = 0,
    rows_loaded: int = 0,
    rows_rejected: int = 0,
    message: str | None = None,
) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            UPDATE audit.PipelineRun
            SET
                Status = 'Succeeded',
                RowsRead = ?,
                RowsLoaded = ?,
                RowsRejected = ?,
                Message = ?,
                CompletedAtUtc = SYSUTCDATETIME()
            WHERE PipelineRunId = ?;
            """,
            rows_read,
            rows_loaded,
            rows_rejected,
            message,
            run_id,
        )
        connection.commit()
    finally:
        cursor.close()


def fail_pipeline_run(connection, run_id: str, message: str) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            UPDATE audit.PipelineRun
            SET
                Status = 'Failed',
                Message = ?,
                CompletedAtUtc = SYSUTCDATETIME()
            WHERE PipelineRunId = ?;
            """,
            message[:2000],
            run_id,
        )
        connection.commit()
    finally:
        cursor.close()


def add_rejected_record(
    connection,
    *,
    run_id: str,
    source_name: str,
    source_file_name: str,
    source_row_number: int | None,
    reason_code: str,
    reason_detail: str,
    raw_payload: str | None,
) -> None:
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO audit.RejectedRecord
            (
                PipelineRunId,
                SourceName,
                SourceFileName,
                SourceRowNumber,
                ReasonCode,
                ReasonDetail,
                RawPayload,
                RejectedAtUtc
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, SYSUTCDATETIME());
            """,
            run_id,
            source_name,
            source_file_name,
            source_row_number,
            reason_code,
            reason_detail[:1000],
            raw_payload,
        )
    finally:
        cursor.close()
