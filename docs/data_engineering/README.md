# Data Engineering Pipeline

This folder documents the implementation previously described in the roadmap as **Phase 2**.

Repository names are responsibility-based rather than phase-number-based.

## Layers

1. Raw files — immutable external source data.
2. `stg` — source-faithful SQL Server staging.
3. `curated` — typed, cleaned and normalized records.
4. `ref` — manual make/model normalization mappings.
5. matching — source integration between listings, GVG and locations.
6. `dw` — analytical dimensional model for EDA, ML and Power BI.
7. `audit` — pipeline execution and rejected-record tracking.

The pipeline deliberately stores staging source values as text. This protects
source fidelity and prevents values such as `POA`, `45,123 km`, or `7.5 L/100km`
from being silently lost during ingestion.
