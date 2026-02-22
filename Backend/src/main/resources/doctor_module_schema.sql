-- ═══════════════════════════════════════════════════════════════════════════════
-- DOCTOR MODULE SCHEMA
-- Implements doctor authentication + consultation management + video teleconsultation
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─── Doctor accounts ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS doctors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(255)    NOT NULL,
    phone           VARCHAR(15)     NOT NULL UNIQUE,
    email           VARCHAR(255)    UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,
    specialization  VARCHAR(255)    DEFAULT 'Obstetrics & Gynaecology',
    hospital        VARCHAR(255),
    district        VARCHAR(255),
    registration_no VARCHAR(100),               -- medical council reg number
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    is_available    BOOLEAN         NOT NULL DEFAULT TRUE, -- online/offline toggle
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_doctor_phone    ON doctors(phone);
CREATE INDEX        idx_doctor_district ON doctors(district);
CREATE INDEX        idx_doctor_available ON doctors(is_available);

-- ─── Consultation requests ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS consultations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Linked records
    visit_id        VARCHAR(255)    NOT NULL,  -- → anc_visits.id
    patient_id      VARCHAR(255)    NOT NULL,  -- → patients.id
    worker_id       VARCHAR(255)    NOT NULL,  -- → anc_workers.id
    doctor_id       VARCHAR(255),              -- → doctors.id (null until accepted)

    -- Risk info (copied from visit for quick sorting)
    risk_level      VARCHAR(20)     NOT NULL,  -- CRITICAL / HIGH / MEDIUM
    is_high_risk    BOOLEAN         NOT NULL DEFAULT TRUE,
    priority_score  INTEGER         NOT NULL DEFAULT 0,
                                               -- CRITICAL=100, HIGH=70, MEDIUM=40

    -- Status lifecycle
    status          VARCHAR(30)     NOT NULL DEFAULT 'PENDING',
                                               -- PENDING/ACCEPTED/IN_PROGRESS/COMPLETED/CANCELLED

    -- Video call
    room_url        VARCHAR(500),              -- Daily.co room URL
    doctor_token    TEXT,                      -- Daily.co token for doctor
    worker_token    TEXT,                      -- Daily.co token for worker

    -- Doctor's notes (filled on completion)
    doctor_notes    TEXT,
    diagnosis       TEXT,
    action_plan     TEXT,

    -- Timestamps
    accepted_at     TIMESTAMP,
    call_started_at TIMESTAMP,
    completed_at    TIMESTAMP,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_consult_doctor_id   ON consultations(doctor_id);
CREATE INDEX idx_consult_visit_id    ON consultations(visit_id);
CREATE INDEX idx_consult_patient_id  ON consultations(patient_id);
CREATE INDEX idx_consult_worker_id   ON consultations(worker_id);
CREATE INDEX idx_consult_status      ON consultations(status);
CREATE INDEX idx_consult_priority    ON consultations(priority_score DESC, created_at ASC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- END OF DOCTOR MODULE SCHEMA
-- ═══════════════════════════════════════════════════════════════════════════════
