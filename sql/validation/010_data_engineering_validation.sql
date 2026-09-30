SELECT 'stg.CarListing' AS ObjectName, COUNT(*) AS RowCount FROM stg.CarListing
UNION ALL
SELECT 'stg.VehicleSpecification', COUNT(*) FROM stg.VehicleSpecification
UNION ALL
SELECT 'stg.Location', COUNT(*) FROM stg.Location
UNION ALL
SELECT 'curated.CarListing', COUNT(*) FROM curated.CarListing
UNION ALL
SELECT 'curated.VehicleSpecification', COUNT(*) FROM curated.VehicleSpecification
UNION ALL
SELECT 'curated.Location', COUNT(*) FROM curated.Location
UNION ALL
SELECT 'dw.FactCarListing', COUNT(*) FROM dw.FactCarListing;

SELECT
    COUNT(*) AS TotalListings,
    SUM(CASE WHEN ListingPrice IS NULL THEN 1 ELSE 0 END) AS MissingCleanPrice,
    SUM(CASE WHEN ModelYear IS NULL THEN 1 ELSE 0 END) AS MissingModelYear,
    SUM(CASE WHEN Kilometres IS NULL THEN 1 ELSE 0 END) AS MissingKilometres
FROM curated.CarListing;

SELECT
    MatchMethod,
    COUNT(*) AS MatchCount,
    AVG(CAST(MatchScore AS DECIMAL(10,2))) AS AverageMatchScore
FROM curated.CarListingVehicleMatch
GROUP BY MatchMethod;

SELECT
    MatchMethod,
    COUNT(*) AS MatchCount,
    AVG(CAST(MatchScore AS DECIMAL(10,2))) AS AverageMatchScore
FROM curated.CarListingLocationMatch
GROUP BY MatchMethod;
