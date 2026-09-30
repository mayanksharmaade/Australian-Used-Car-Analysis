# Complete Data Engineering Step Map

| Roadmap Step | Implementation |
|---|---|
| 2.1 | `etl/profiling/inspect_source_schemas.py` |
| 2.2 | Production `stg.CarListing` in `sql/staging/010_create_production_staging_tables.sql` |
| 2.3 | Production `stg.VehicleSpecification` |
| 2.4 | Production `stg.Location` |
| 2.5 | `audit.PipelineRun`, `audit.RejectedRecord`, `etl/common/audit.py` |
| 2.6 | `etl/staging/load_*.py` |
| 2.7 | `cursor.fast_executemany = True` bulk-oriented loading |
| 2.8 | `etl/validation/validate_staging.py` |
| 2.9 | `audit.RejectedRecord` + `etl/validation/capture_rejected_records.py` |
| 2.10 | `etl/cleaning/clean_car_listings.py` |
| 2.11 | `etl/cleaning/clean_vehicle_specs.py` |
| 2.12 | `etl/cleaning/clean_locations.py` |
| 2.13 | `etl/cleaning/deduplicate_curated.py` |
| 2.14 | `ref.MakeMapping`, `ref.ModelMapping`, `normalize_vehicle_names.py` |
| 2.15 | `etl/matching/match_vehicle_specs.py` |
| 2.16 | `etl/matching/match_locations.py` |
| 2.17 | `etl/matching/assess_match_quality.py` |
| 2.18 | `curated`, `ref`, `dw` schemas |
| 2.19 | `dw.DimMake`, `DimModel`, `DimVehicle`, `DimLocation` |
| 2.20 | `dw.FactCarListing` |
| 2.21 | `etl/validation/reconcile_pipeline.py` + tests |
| 2.22 | `etl/pipeline/run_data_pipeline.py` |
