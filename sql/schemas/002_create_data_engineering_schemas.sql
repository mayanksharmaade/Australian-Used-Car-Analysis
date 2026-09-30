IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'ref')
    EXEC('CREATE SCHEMA ref');

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'curated')
    EXEC('CREATE SCHEMA curated');

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'dw')
    EXEC('CREATE SCHEMA dw');

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'ml')
    EXEC('CREATE SCHEMA ml');
