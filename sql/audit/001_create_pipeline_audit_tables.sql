IF OBJECT_ID('audit.PipelineRun', 'U') IS NULL
BEGIN
    CREATE TABLE audit.PipelineRun
    (
        PipelineRunId UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
        PipelineName NVARCHAR(150) NOT NULL,
        SourceName NVARCHAR(200) NULL,
        Status NVARCHAR(30) NOT NULL,
        RowsRead INT NOT NULL DEFAULT 0,
        RowsLoaded INT NOT NULL DEFAULT 0,
        RowsRejected INT NOT NULL DEFAULT 0,
        Message NVARCHAR(2000) NULL,
        StartedAtUtc DATETIME2 NOT NULL,
        CompletedAtUtc DATETIME2 NULL
    );
END;

IF OBJECT_ID('audit.RejectedRecord', 'U') IS NULL
BEGIN
    CREATE TABLE audit.RejectedRecord
    (
        RejectedRecordId BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        PipelineRunId UNIQUEIDENTIFIER NULL,
        SourceName NVARCHAR(200) NOT NULL,
        SourceFileName NVARCHAR(255) NOT NULL,
        SourceRowNumber INT NULL,
        ReasonCode NVARCHAR(100) NOT NULL,
        ReasonDetail NVARCHAR(1000) NULL,
        RawPayload NVARCHAR(MAX) NULL,
        RejectedAtUtc DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_RejectedRecord_PipelineRun
            FOREIGN KEY (PipelineRunId)
            REFERENCES audit.PipelineRun(PipelineRunId)
    );
END;
