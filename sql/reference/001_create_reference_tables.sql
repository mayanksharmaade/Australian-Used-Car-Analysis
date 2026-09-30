IF OBJECT_ID('ref.MakeMapping', 'U') IS NULL
BEGIN
    CREATE TABLE ref.MakeMapping
    (
        MakeMappingId INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        SourceMakeNormalized NVARCHAR(200) NOT NULL,
        CanonicalMakeNormalized NVARCHAR(200) NOT NULL,
        IsActive BIT NOT NULL DEFAULT 1,
        Notes NVARCHAR(500) NULL,
        CONSTRAINT UQ_MakeMapping_Source UNIQUE(SourceMakeNormalized)
    );
END;

IF OBJECT_ID('ref.ModelMapping', 'U') IS NULL
BEGIN
    CREATE TABLE ref.ModelMapping
    (
        ModelMappingId INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        MakeNormalized NVARCHAR(200) NOT NULL,
        SourceModelNormalized NVARCHAR(300) NOT NULL,
        CanonicalModelNormalized NVARCHAR(300) NOT NULL,
        IsActive BIT NOT NULL DEFAULT 1,
        Notes NVARCHAR(500) NULL,
        CONSTRAINT UQ_ModelMapping_Source UNIQUE(MakeNormalized, SourceModelNormalized)
    );
END;
