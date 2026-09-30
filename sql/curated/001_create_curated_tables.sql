IF OBJECT_ID('curated.CarListingVehicleMatch', 'U') IS NOT NULL DROP TABLE curated.CarListingVehicleMatch;
IF OBJECT_ID('curated.CarListingLocationMatch', 'U') IS NOT NULL DROP TABLE curated.CarListingLocationMatch;
IF OBJECT_ID('curated.CarListing', 'U') IS NOT NULL DROP TABLE curated.CarListing;
IF OBJECT_ID('curated.VehicleSpecification', 'U') IS NOT NULL DROP TABLE curated.VehicleSpecification;
IF OBJECT_ID('curated.Location', 'U') IS NOT NULL DROP TABLE curated.Location;

CREATE TABLE curated.CarListing
(
    CarListingId BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    CarListingStagingId BIGINT NOT NULL,
    Make NVARCHAR(200) NULL,
    MakeNormalized NVARCHAR(200) NULL,
    ModelYear INT NULL,
    Model NVARCHAR(300) NULL,
    ModelNormalized NVARCHAR(300) NULL,
    CarSuv NVARCHAR(100) NULL,
    Title NVARCHAR(500) NULL,
    VehicleCondition NVARCHAR(100) NULL,
    Transmission NVARCHAR(150) NULL,
    EngineDescription NVARCHAR(300) NULL,
    DriveType NVARCHAR(150) NULL,
    FuelType NVARCHAR(150) NULL,
    FuelConsumptionLPer100Km DECIMAL(10,3) NULL,
    Kilometres INT NULL,
    ColourExtInt NVARCHAR(300) NULL,
    LocationRaw NVARCHAR(300) NULL,
    SuburbRaw NVARCHAR(250) NULL,
    SuburbNormalized NVARCHAR(250) NULL,
    StateCodeRaw NVARCHAR(10) NULL,
    PostcodeRaw NVARCHAR(10) NULL,
    CylinderCount INT NULL,
    BodyType NVARCHAR(150) NULL,
    Doors INT NULL,
    Seats INT NULL,
    ListingPrice DECIMAL(18,2) NULL,
    ListingPriceRaw NVARCHAR(150) NULL,
    SourceFileName NVARCHAR(255) NOT NULL,
    PipelineRunId UNIQUEIDENTIFIER NULL,
    CuratedAtUtc DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_CuratedCarListing_MakeModelYear
ON curated.CarListing(MakeNormalized, ModelNormalized, ModelYear);

CREATE TABLE curated.VehicleSpecification
(
    VehicleSpecificationId BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    VehicleSpecificationStagingId BIGINT NOT NULL,
    Make NVARCHAR(200) NULL,
    MakeNormalized NVARCHAR(200) NULL,
    Model NVARCHAR(300) NULL,
    ModelNormalized NVARCHAR(300) NULL,
    Variant NVARCHAR(500) NULL,
    ModelYear INT NULL,
    BodyStyle NVARCHAR(200) NULL,
    EngineDescription NVARCHAR(300) NULL,
    Transmission NVARCHAR(200) NULL,
    FuelType NVARCHAR(200) NULL,
    DriveType NVARCHAR(200) NULL,
    Seats INT NULL,
    FuelConsumptionLPer100Km DECIMAL(10,3) NULL,
    CO2GPerKm DECIMAL(10,3) NULL,
    SourceFileName NVARCHAR(255) NOT NULL,
    PipelineRunId UNIQUEIDENTIFIER NULL,
    CuratedAtUtc DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_CuratedVehicleSpec_MakeModelYear
ON curated.VehicleSpecification(MakeNormalized, ModelNormalized, ModelYear);

CREATE TABLE curated.Location
(
    LocationId BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    LocationStagingId BIGINT NOT NULL,
    Suburb NVARCHAR(250) NULL,
    SuburbNormalized NVARCHAR(250) NULL,
    StateCode NVARCHAR(10) NULL,
    Postcode NVARCHAR(10) NULL,
    AddressCount INT NULL,
    Latitude DECIMAL(10,7) NULL,
    Longitude DECIMAL(10,7) NULL,
    SourceFileName NVARCHAR(255) NOT NULL,
    PipelineRunId UNIQUEIDENTIFIER NULL,
    CuratedAtUtc DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_CuratedLocation_Postcode ON curated.Location(Postcode);
CREATE INDEX IX_CuratedLocation_SuburbState ON curated.Location(SuburbNormalized, StateCode);

CREATE TABLE curated.CarListingVehicleMatch
(
    CarListingId BIGINT NOT NULL PRIMARY KEY,
    VehicleSpecificationId BIGINT NOT NULL,
    MatchScore INT NOT NULL,
    MatchMethod NVARCHAR(50) NOT NULL,
    MatchedAtUtc DATETIME2 NOT NULL,
    CONSTRAINT FK_CarListingVehicleMatch_CarListing
        FOREIGN KEY (CarListingId) REFERENCES curated.CarListing(CarListingId),
    CONSTRAINT FK_CarListingVehicleMatch_VehicleSpecification
        FOREIGN KEY (VehicleSpecificationId) REFERENCES curated.VehicleSpecification(VehicleSpecificationId)
);

CREATE TABLE curated.CarListingLocationMatch
(
    CarListingId BIGINT NOT NULL PRIMARY KEY,
    LocationId BIGINT NOT NULL,
    MatchScore INT NOT NULL,
    MatchMethod NVARCHAR(50) NOT NULL,
    MatchedAtUtc DATETIME2 NOT NULL,
    CONSTRAINT FK_CarListingLocationMatch_CarListing
        FOREIGN KEY (CarListingId) REFERENCES curated.CarListing(CarListingId),
    CONSTRAINT FK_CarListingLocationMatch_Location
        FOREIGN KEY (LocationId) REFERENCES curated.Location(LocationId)
);
