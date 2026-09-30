# Source Integration Strategy

## Source 1 — Primary listing grain

Australian Vehicle Prices is the core listing / vehicle-observation dataset.

## Source 1 → Source 2

Candidate vehicle-specification matching fields:

- Make
- Model
- ModelYear
- Variant where available

Measure:

- exact match rate
- normalized match rate
- ambiguous match rate
- unmatched rate

Blind fuzzy matching is not allowed.

## Source 1 → Source 3

Listing `Location` will be standardized and matched to locality/state.

Expected enrichment:

- suburb/locality
- postcode
- state
- latitude
- longitude

## Optional RBA / ABS

Economic indicators will only be joined when a reliable listing/observation date exists.

Do not join macroeconomic indicators to vehicle model year.

## Phase boundary

Phase 1:
- acquire
- preserve
- document
- profile
- assess join feasibility

Phase 2:
- design SQL staging tables from actual schemas
- load staging
- validate
- clean
- standardize
- reject invalid records
- match entities
- integrate sources
