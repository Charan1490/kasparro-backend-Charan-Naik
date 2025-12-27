-- Database initialization script
-- This runs when the PostgreSQL container first starts

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant all privileges to the user
GRANT ALL PRIVILEGES ON DATABASE crypto_db TO crypto_user;

-- Set default permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO crypto_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO crypto_user;
