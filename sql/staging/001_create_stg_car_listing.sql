IF OBJECT_ID('stg.CarListing', 'U') IS NULL
BEGIN
    CREATE TABLE stg.CarListing
    (
        SourceListingId NVARCHAR(100) NULL,
        Make NVARCHAR(100) NULL,
        Model NVARCHAR(150) NULL,
        ModelYear INT NULL,
        ListingPrice DECIMAL(18,2) NULL,
        Kilometres INT NULL,
        StateCode NVARCHAR(10) NULL,
        City NVARCHAR(150) NULL,
        Postcode NVARCHAR(10) NULL,
        BodyType NVARCHAR(50) NULL,
        Transmission NVARCHAR(50) NULL,
        FuelType NVARCHAR(50) NULL,
        EngineDescription NVARCHAR(150) NULL,
        ListingDate DATE NULL,
        SourceName NVARCHAR(100) NOT NULL,
        LoadedAtUtc DATETIME2 NOT NULL
            DEFAULT SYSUTCDATETIME()
    )
END
