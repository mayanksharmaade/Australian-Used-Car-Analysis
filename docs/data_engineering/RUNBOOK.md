# Data Engineering Pipeline Runbook

## Prerequisites

Required raw files:

```text
data/raw/car_listings/Australian Vehicle Prices.csv
data/raw/vehicle_specs/*.csv
data/raw/locations/australian_postcodes.csv
```

Existing configuration:

```text
config/config.yaml
```

The project already uses SQL Server database:

```text
AustralianUsedCarAnalytics
```

## 1. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

## 2. Install dependencies

```powershell
pip install -r requirements.txt
```

## 3. Inspect actual source schemas

```powershell
python -m etl.profiling.inspect_source_schemas
```

Review:

```text
reports/data_engineering/source_schema/
```

## 4. Run unit tests

```powershell
pytest -q
```

## 5. Create Data Engineering SQL objects

WARNING: this replaces the Phase-0 sample `stg.CarListing` table with the
production raw staging table.

```powershell
python scripts/setup_data_engineering_database.py
```

## 6. Run loaders one at a time while learning

```powershell
python -m etl.staging.load_car_listings
python -m etl.staging.load_vehicle_specs
python -m etl.staging.load_locations
python -m etl.validation.validate_staging
python -m etl.validation.capture_rejected_records
```

## 7. Clean each source

```powershell
python -m etl.cleaning.clean_car_listings
python -m etl.cleaning.clean_vehicle_specs
python -m etl.cleaning.clean_locations
python -m etl.cleaning.deduplicate_curated
```

## 8. Apply optional reference mappings

```powershell
python -m etl.matching.normalize_vehicle_names
```

## 9. Integrate the sources

```powershell
python -m etl.matching.match_vehicle_specs
python -m etl.matching.match_locations
python -m etl.matching.assess_match_quality
```

## 10. Build the warehouse

```powershell
python -m etl.warehouse.load_dimensions
python -m etl.warehouse.load_fact_car_listing
```

## 11. Reconcile

```powershell
python -m etl.validation.reconcile_pipeline
```

## 12. Full automated pipeline

Only after the individual steps are understood and tested:

```powershell
python -m etl.pipeline.run_data_pipeline
```

## Important Green Vehicle Guide note

GVG exports can use different headings. `load_vehicle_specs.py` supports common
heading variants and stores the full source row in `RawJson`. After running
schema profiling, update `COLUMN_CANDIDATES` if your downloaded files use a
different heading.

## Git suggestion

After successful end-to-end validation:

```powershell
git add .
git commit -m "Complete used car data engineering pipeline"
```
