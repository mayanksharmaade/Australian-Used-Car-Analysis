IF OBJECT_ID('dw.FactCarListing', 'U') IS NULL
BEGIN
    CREATE TABLE dw.FactCarListing
    (
        FactCarListingKey BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        CarListingId BIGINT NOT NULL,
        VehicleKey BIGINT NULL,
        LocationKey BIGINT NULL,
        ListingPrice DECIMAL(18,2) NULL,
        Kilometres INT NULL,
        FuelConsumptionLPer100Km DECIMAL(10,3) NULL,
        VehicleSpecificationId BIGINT NULL,
        VehicleMatchScore INT NULL,
        LocationMatchScore INT NULL,
        SourceFileName NVARCHAR(255) NOT NULL,
        PipelineRunId UNIQUEIDENTIFIER NULL,
        LoadedAtUtc DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_FactCarListing_DimVehicle
            FOREIGN KEY (VehicleKey) REFERENCES dw.DimVehicle(VehicleKey),
        CONSTRAINT FK_FactCarListing_DimLocation
            FOREIGN KEY (LocationKey) REFERENCES dw.DimLocation(LocationKey)
    );

    CREATE UNIQUE INDEX UX_FactCarListing_CarListingId
    ON dw.FactCarListing(CarListingId);
END;
