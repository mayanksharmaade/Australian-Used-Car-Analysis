IF OBJECT_ID('dw.FactCarListing', 'U') IS NOT NULL DROP TABLE dw.FactCarListing;
IF OBJECT_ID('dw.DimVehicle', 'U') IS NOT NULL DROP TABLE dw.DimVehicle;
IF OBJECT_ID('dw.DimModel', 'U') IS NOT NULL DROP TABLE dw.DimModel;
IF OBJECT_ID('dw.DimMake', 'U') IS NOT NULL DROP TABLE dw.DimMake;
IF OBJECT_ID('dw.DimLocation', 'U') IS NOT NULL DROP TABLE dw.DimLocation;

CREATE TABLE dw.DimMake
(
    MakeKey INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    MakeName NVARCHAR(200) NOT NULL,
    MakeNormalized NVARCHAR(200) NOT NULL UNIQUE
);

CREATE TABLE dw.DimModel
(
    ModelKey INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    MakeKey INT NOT NULL,
    ModelName NVARCHAR(300) NOT NULL,
    ModelNormalized NVARCHAR(300) NOT NULL,
    CONSTRAINT FK_DimModel_DimMake FOREIGN KEY (MakeKey) REFERENCES dw.DimMake(MakeKey),
    CONSTRAINT UQ_DimModel UNIQUE(MakeKey, ModelNormalized)
);

CREATE TABLE dw.DimVehicle
(
    VehicleKey BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    ModelKey INT NOT NULL,
    ModelYear INT NULL,
    BodyType NVARCHAR(150) NULL,
    Transmission NVARCHAR(150) NULL,
    FuelType NVARCHAR(150) NULL,
    DriveType NVARCHAR(150) NULL,
    CylinderCount INT NULL,
    Doors INT NULL,
    Seats INT NULL,
    CONSTRAINT FK_DimVehicle_DimModel FOREIGN KEY (ModelKey) REFERENCES dw.DimModel(ModelKey)
);

CREATE TABLE dw.DimLocation
(
    LocationKey BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    CuratedLocationId BIGINT NOT NULL UNIQUE,
    Suburb NVARCHAR(250) NULL,
    SuburbNormalized NVARCHAR(250) NULL,
    StateCode NVARCHAR(10) NULL,
    Postcode NVARCHAR(10) NULL,
    Latitude DECIMAL(10,7) NULL,
    Longitude DECIMAL(10,7) NULL,
    AddressCount INT NULL
);
