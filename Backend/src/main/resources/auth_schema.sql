-- Authentication and Patient Management Schema
-- This script creates tables for ANC worker authentication and patient management

-- Enable UUID generation extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ANC Workers Table
-- Stores authentication and profile information for ANC healthcare workers
CREATE TABLE IF NOT EXISTS anc_workers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(255) NOT NULL,
    phone           VARCHAR(10) NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    health_center   VARCHAR(255) NOT NULL,
    district        VARCHAR(255) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Patients Table
-- Stores patient demographic and pregnancy information
CREATE TABLE IF NOT EXISTS patients (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id       UUID NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    phone           VARCHAR(15),
    age             INTEGER,
    address         TEXT,
    village         VARCHAR(255),
    district        VARCHAR(255),
    lmp_date        DATE,
    edd_date        DATE,
    blood_group     VARCHAR(10),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_worker
        FOREIGN KEY (worker_id)
        REFERENCES anc_workers(id)
        ON DELETE CASCADE
);

-- Indexes for anc_workers table
CREATE UNIQUE INDEX IF NOT EXISTS idx_anc_workers_phone ON anc_workers(phone);
CREATE INDEX IF NOT EXISTS idx_anc_workers_district ON anc_workers(district);

-- Indexes for patients table
CREATE INDEX IF NOT EXISTS idx_patients_worker_id ON patients(worker_id);
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);
CREATE INDEX IF NOT EXISTS idx_patients_district ON patients(district);

-- Trigger function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to anc_workers table
CREATE TRIGGER update_anc_workers_updated_at
    BEFORE UPDATE ON anc_workers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to patients table
CREATE TRIGGER update_patients_updated_at
    BEFORE UPDATE ON patients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
