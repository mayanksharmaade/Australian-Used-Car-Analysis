IF NOT EXISTS (
    SELECT 1 FROM sys.schemas WHERE name = 'stg'
)
    EXEC('CREATE SCHEMA stg');

IF NOT EXISTS (
    SELECT 1 FROM sys.schemas WHERE name = 'dim'
)
    EXEC('CREATE SCHEMA dim');

IF NOT EXISTS (
    SELECT 1 FROM sys.schemas WHERE name = 'fact'
)
    EXEC('CREATE SCHEMA fact');

IF NOT EXISTS (
    SELECT 1 FROM sys.schemas WHERE name = 'audit'
)
    EXEC('CREATE SCHEMA audit');
