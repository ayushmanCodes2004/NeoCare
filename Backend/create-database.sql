-- Create NeoSure database
CREATE DATABASE "NeoSure";

-- Connect to NeoSure database
\c "NeoSure";

-- Create extension for UUID support
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Verify
SELECT current_database();
