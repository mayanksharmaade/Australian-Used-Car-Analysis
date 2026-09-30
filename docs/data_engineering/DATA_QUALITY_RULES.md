# Data Quality Rules

## Car listings

- Make and model should be present for useful analytical records.
- `ModelYear` is parsed from raw text; impossible years are reviewed during EDA.
- `ListingPrice` remains NULL when source text is not numeric, including `POA`.
- `Kilometres` strips commas and textual units before conversion.
- Raw price and location values are retained in the curated layer for traceability.

## Vehicle specifications

- Make/model/year are the primary deterministic integration candidates.
- Exact make+model+year receives match score 100.
- Make+model fallback receives match score 80.
- Variant matching is deferred until the real GVG data is reviewed.

## Locations

- Postcode match receives score 100.
- Suburb/state fallback receives score 80.
- Coordinates are parsed to decimals.
- Postcodes are preserved as strings to keep leading zeroes.

## Matching

Match percentages are outputs, not hard-coded success claims. Review the actual
`reports/data_engineering/match_quality/` results before Phase 3.
