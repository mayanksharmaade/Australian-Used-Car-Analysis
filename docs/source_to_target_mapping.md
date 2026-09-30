# Source-to-Target Mapping

## Source 1 — Australian Vehicle Prices

| Source field | Planned target | Phase 2 transformation |
|---|---|---|
| Brand | Make | trim, case and name normalization |
| Year | ModelYear | numeric conversion |
| Model | Model | text normalization |
| UsedOrNew | VehicleCondition | category mapping |
| Transmission | Transmission | category normalization |
| Engine | EngineDescription | preserve + parse |
| DriveType | DriveType | normalization |
| FuelType | FuelType | normalization |
| FuelConsumption | FuelConsumptionLPer100Km | parse numeric |
| Kilometres | Kilometres | remove commas/units |
| ColourExtInt | Exterior/InteriorColour | split if feasible |
| Location | LocationRaw | parse + geographic matching |
| CylindersinEngine | CylinderCount | parse numeric |
| BodyType | BodyType | normalization |
| Doors | Doors | parse integer |
| Seats | Seats | parse integer |
| Price | ListingPrice | currency → decimal |

Exact mappings must be corrected after profiling the actual CSV.

## Source 2 — Green Vehicle Guide

Candidate fields:
- Make
- Model
- Variant
- Year
- Engine
- Transmission
- Fuel
- Fuel consumption
- Drive
- Body style
- Seats
- CO2 emissions

Candidate join:

`Make + Model + Year`

Use Variant/Engine/Transmission for disambiguation where possible.

## Source 3 — Australian postcode/locality reference

Expected useful fields:

- locality → Suburb
- state → StateCode
- postcode → Postcode
- latitude → Latitude
- longitude → Longitude
- count → AddressCount

Candidate join:

`Listing.Location → locality + state`
