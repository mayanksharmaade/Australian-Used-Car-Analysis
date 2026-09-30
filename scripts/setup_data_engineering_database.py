from pathlib import Path

from etl.common.db import get_connection, execute_sql_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SQL_FILES = [
    PROJECT_ROOT / "sql" / "schemas" / "002_create_data_engineering_schemas.sql",
    PROJECT_ROOT / "sql" / "audit" / "001_create_pipeline_audit_tables.sql",
    PROJECT_ROOT / "sql" / "staging" / "010_create_production_staging_tables.sql",
    PROJECT_ROOT / "sql" / "curated" / "001_create_curated_tables.sql",
    PROJECT_ROOT / "sql" / "reference" / "001_create_reference_tables.sql",
    PROJECT_ROOT / "sql" / "warehouse" / "001_create_dimensions.sql",
    PROJECT_ROOT / "sql" / "warehouse" / "002_create_fact_car_listing.sql",
]


def main():
    with get_connection() as connection:
        for sql_file in SQL_FILES:
            if not sql_file.exists():
                raise FileNotFoundError(sql_file)
            print(f"Executing {sql_file.relative_to(PROJECT_ROOT)}")
            execute_sql_file(connection, sql_file)

    print("Data Engineering SQL objects are ready.")


if __name__ == "__main__":
    main()
