CREATE DATABASE anc_db;
\c anc_db;

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS anc_visits (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Patient & worker identifiers
    patient_id        VARCHAR(255),
    patient_name      VARCHAR(255),
    worker_id         VARCHAR(255),
    phc_id            VARCHAR(255),

    -- ANC input from React
    clinical_summary  TEXT,
    structured_data   JSONB NOT NULL,

    -- FastAPI /analyze output (exact field names from response)
    is_high_risk      BOOLEAN,
    risk_level        VARCHAR(20),        -- CRITICAL / HIGH / MEDIUM / LOW
    detected_risks    JSONB,              -- ["Severe Anaemia", "Twin Pregnancy", ...]
    explanation       TEXT,
    confidence        NUMERIC(4,3),       -- 0.000 to 1.000
    recommendation    TEXT,
    visit_metadata    JSONB,              -- nullable extra metadata from FastAPI

    -- Processing lifecycle
    status            VARCHAR(30) DEFAULT 'REGISTERED',  -- REGISTERED/AI_ANALYZED/AI_FAILED
    ai_error_message  TEXT,

    -- Timestamps
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Standard indexes
CREATE INDEX idx_anc_patient_id     ON anc_visits(patient_id);
CREATE INDEX idx_anc_worker_id      ON anc_visits(worker_id);
CREATE INDEX idx_anc_risk_level     ON anc_visits(risk_level);
CREATE INDEX idx_anc_is_high_risk   ON anc_visits(is_high_risk);
CREATE INDEX idx_anc_created_at     ON anc_visits(created_at DESC);

-- GIN indexes for JSONB columns
CREATE INDEX idx_anc_structured     ON anc_visits USING GIN(structured_data);
CREATE INDEX idx_anc_detected_risks ON anc_visits USING GIN(detected_risks);
