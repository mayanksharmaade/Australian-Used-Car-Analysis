import pyodbc

from config.settings import (
    load_config,
    build_connection_string,
)


def create_database():
    cfg = load_config()["database"]

    database_name = cfg["database"]

    master_connection = build_connection_string(
        database_override="master"
    )

    with pyodbc.connect(
        master_connection,
        autocommit=True
    ) as conn:

        cursor = conn.cursor()

        cursor.execute(
            f"""
            IF DB_ID(N'{database_name}') IS NULL
            BEGIN
                CREATE DATABASE [{database_name}]
            END
            """
        )


def create_schemas_and_tables():
    with pyodbc.connect(
        build_connection_string(),
        autocommit=True
    ) as conn:

        cursor = conn.cursor()

        cursor.execute("""
        IF NOT EXISTS (
            SELECT 1
            FROM sys.schemas
            WHERE name = 'stg'
        )
            EXEC('CREATE SCHEMA stg');

        IF NOT EXISTS (
            SELECT 1
            FROM sys.schemas
            WHERE name = 'dim'
        )
            EXEC('CREATE SCHEMA dim');

        IF NOT EXISTS (
            SELECT 1
            FROM sys.schemas
            WHERE name = 'fact'
        )
            EXEC('CREATE SCHEMA fact');

        IF NOT EXISTS (
            SELECT 1
            FROM sys.schemas
            WHERE name = 'audit'
        )
            EXEC('CREATE SCHEMA audit');
        """)

        cursor.execute("""
        IF OBJECT_ID('stg.CarListing', 'U') IS NULL
        BEGIN
            CREATE TABLE stg.CarListing
            (
                SourceListingId NVARCHAR(100) NULL,
                Make NVARCHAR(100) NULL,
                Model NVARCHAR(150) NULL,
                ModelYear INT NULL,
                ListingPrice DECIMAL(18,2) NULL,
                Kilometres INT NULL,
                StateCode NVARCHAR(10) NULL,
                City NVARCHAR(150) NULL,
                Postcode NVARCHAR(10) NULL,
                BodyType NVARCHAR(50) NULL,
                Transmission NVARCHAR(50) NULL,
                FuelType NVARCHAR(50) NULL,
                EngineDescription NVARCHAR(150) NULL,
                ListingDate DATE NULL,
                SourceName NVARCHAR(100) NOT NULL,
                LoadedAtUtc DATETIME2 NOT NULL
                    DEFAULT SYSUTCDATETIME()
            )
        END
        """)


def main():
    print("Creating/verifying database...")
    create_database()

    print("Creating/verifying schemas and Phase 0 table...")
    create_schemas_and_tables()

    print("Database setup completed successfully.")


if __name__ == "__main__":
    main()
