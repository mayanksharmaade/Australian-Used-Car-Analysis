/*
Production staging layer.
Raw source values are deliberately stored as NVARCHAR so the pipeline preserves
source fidelity and performs type conversion in the curated layer.
*/

IF OBJECT_ID('stg.CarListing', 'U') IS NOT NULL
    DROP TABLE stg.CarListing;

CREATE TABLE stg.CarListing
(
    CarListingStagingId BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    SourceRowNumber INT NULL,
    BrandRaw NVARCHAR(200) NULL,
    YearRaw NVARCHAR(50) NULL,
    ModelRaw NVARCHAR(300) NULL,
    CarSuvRaw NVARCHAR(100) NULL,
    TitleRaw NVARCHAR(500) NULL,
    UsedOrNewRaw NVARCHAR(100) NULL,
    TransmissionRaw NVARCHAR(150) NULL,
    EngineRaw NVARCHAR(300) NULL,
    DriveTypeRaw NVARCHAR(150) NULL,
    FuelTypeRaw NVARCHAR(150) NULL,
    FuelConsumptionRaw NVARCHAR(150) NULL,
    KilometresRaw NVARCHAR(150) NULL,
    ColourExtIntRaw NVARCHAR(300) NULL,
    LocationRaw NVARCHAR(300) NULL,
    CylindersInEngineRaw NVARCHAR(100) NULL,
    BodyTypeRaw NVARCHAR(150) NULL,
    DoorsRaw NVARCHAR(100) NULL,
    SeatsRaw NVARCHAR(100) NULL,
    PriceRaw NVARCHAR(150) NULL,
    SourceFileName NVARCHAR(255) NOT NULL,
    PipelineRunId UNIQUEIDENTIFIER NULL,
    LoadedAtUtc DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

IF OBJECT_ID('stg.VehicleSpecification', 'U') IS NOT NULL
    DROP TABLE stg.VehicleSpecification;

CREATE TABLE stg.VehicleSpecification
(
    VehicleSpecificationStagingId BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    SourceRowNumber INT NULL,
    MakeRaw NVARCHAR(200) NULL,
    ModelRaw NVARCHAR(300) NULL,
    VariantRaw NVARCHAR(500) NULL,
    ModelYearRaw NVARCHAR(100) NULL,
    BodyStyleRaw NVARCHAR(200) NULL,
    EngineRaw NVARCHAR(300) NULL,
    TransmissionRaw NVARCHAR(200) NULL,
    FuelTypeRaw NVARCHAR(200) NULL,
    DriveTypeRaw NVARCHAR(200) NULL,
    SeatsRaw NVARCHAR(100) NULL,
    FuelConsumptionRaw NVARCHAR(150) NULL,
    CO2Raw NVARCHAR(150) NULL,
    RawJson NVARCHAR(MAX) NULL,
    SourceFileName NVARCHAR(255) NOT NULL,
    PipelineRunId UNIQUEIDENTIFIER NULL,
    LoadedAtUtc DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

IF OBJECT_ID('stg.Location', 'U') IS NOT NULL
    DROP TABLE stg.Location;

CREATE TABLE stg.Location
(
    LocationStagingId BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    SourceRowNumber INT NULL,
    LocalityRaw NVARCHAR(250) NULL,
    StateRaw NVARCHAR(50) NULL,
    PostcodeRaw NVARCHAR(30) NULL,
    AddressCountRaw NVARCHAR(100) NULL,
    LatitudeRaw NVARCHAR(100) NULL,
    LongitudeRaw NVARCHAR(100) NULL,
    SourceFileName NVARCHAR(255) NOT NULL,
    PipelineRunId UNIQUEIDENTIFIER NULL,
    LoadedAtUtc DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
