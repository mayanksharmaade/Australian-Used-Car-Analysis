USE AustralianUsedCarAnalytics;
GO

-- Starter checks. Thresholds will be refined after profiling real data.
SELECT COUNT(*) AS TotalRows FROM stg.CarListing;

SELECT
    SUM(CASE WHEN Make IS NULL OR LTRIM(RTRIM(Make)) = '' THEN 1 ELSE 0 END) AS MissingMake,
    SUM(CASE WHEN Model IS NULL OR LTRIM(RTRIM(Model)) = '' THEN 1 ELSE 0 END) AS MissingModel,
    SUM(CASE WHEN ListingPrice IS NULL OR ListingPrice <= 0 THEN 1 ELSE 0 END) AS InvalidPrice,
    SUM(CASE WHEN Kilometres IS NOT NULL AND Kilometres < 0 THEN 1 ELSE 0 END) AS InvalidKilometres
FROM stg.CarListing;
GO
