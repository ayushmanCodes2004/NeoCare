-- Doctor and Consultation Module Schema

-- Create doctors table
CREATE TABLE IF NOT EXISTS doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    license_number VARCHAR(50) NOT NULL,
    hospital VARCHAR(255) NOT NULL,
    district VARCHAR(100) NOT NULL,
    years_of_experience INTEGER,
    role VARCHAR(20) DEFAULT 'DOCTOR',
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create consultations table
CREATE TABLE IF NOT EXISTS consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL,
    worker_id UUID NOT NULL,
    doctor_id UUID NOT NULL,
    visit_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'REQUESTED',
    risk_level VARCHAR(20) NOT NULL,
    room_id VARCHAR(255),
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    doctor_notes TEXT,
    prescription TEXT,
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES anc_workers(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_consultations_doctor_id ON consultations(doctor_id);
CREATE INDEX IF NOT EXISTS idx_consultations_worker_id ON consultations(worker_id);
CREATE INDEX IF NOT EXISTS idx_consultations_patient_id ON consultations(patient_id);
CREATE INDEX IF NOT EXISTS idx_consultations_status ON consultations(status);
CREATE INDEX IF NOT EXISTS idx_consultations_risk_level ON consultations(risk_level);
CREATE INDEX IF NOT EXISTS idx_consultations_scheduled_at ON consultations(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_doctors_email ON doctors(email);
CREATE INDEX IF NOT EXISTS idx_doctors_phone ON doctors(phone);
CREATE INDEX IF NOT EXISTS idx_doctors_is_available ON doctors(is_available);

-- Add comments
COMMENT ON TABLE doctors IS 'Stores doctor information for video consultations';
COMMENT ON TABLE consultations IS 'Stores consultation requests and video call details';
COMMENT ON COLUMN consultations.status IS 'REQUESTED, SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED';
COMMENT ON COLUMN consultations.risk_level IS 'LOW, HIGH, CRITICAL';
