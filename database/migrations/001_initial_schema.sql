CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS survey_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL CHECK (status IN ('REVIEW_REQUIRED', 'READY_FOR_CONFIRMATION', 'CONFIRMED', 'REJECTED')),
    total_rows INTEGER NOT NULL DEFAULT 0 CHECK (total_rows >= 0),
    valid_rows INTEGER NOT NULL DEFAULT 0 CHECK (valid_rows >= 0),
    rejected_rows INTEGER NOT NULL DEFAULT 0 CHECK (rejected_rows >= 0),
    warning_rows INTEGER NOT NULL DEFAULT 0 CHECK (warning_rows >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS valid_survey_records (
    id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL REFERENCES survey_batches(id) ON DELETE CASCADE,
    record_id VARCHAR(64) NOT NULL,
    survey_code VARCHAR(30) NOT NULL,
    interview_date DATE NOT NULL,
    department_code VARCHAR(10) NOT NULL,
    municipality_code VARCHAR(10) NOT NULL,
    urban_rural CHAR(1) NOT NULL CHECK (urban_rural IN ('U', 'R')),
    respondent_age SMALLINT NOT NULL CHECK (respondent_age BETWEEN 0 AND 120),
    respondent_sex VARCHAR(2) NOT NULL CHECK (respondent_sex IN ('F', 'M', 'X', 'NR')),
    household_size SMALLINT NOT NULL CHECK (household_size BETWEEN 1 AND 50),
    monthly_income_gtq NUMERIC(12, 2) CHECK (monthly_income_gtq >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (batch_id, record_id)
);

CREATE TABLE IF NOT EXISTS validation_errors (
    id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL REFERENCES survey_batches(id) ON DELETE CASCADE,
    row_number INTEGER NOT NULL CHECK (row_number >= 2),
    record_id VARCHAR(64),
    code VARCHAR(32) NOT NULL,
    severity VARCHAR(16) NOT NULL CHECK (severity IN ('ERROR', 'WARNING')),
    column_name VARCHAR(64),
    message TEXT NOT NULL,
    received_value TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_valid_survey_records_batch_id
    ON valid_survey_records (batch_id);

CREATE INDEX IF NOT EXISTS idx_validation_errors_batch_id
    ON validation_errors (batch_id);

CREATE INDEX IF NOT EXISTS idx_validation_errors_code
    ON validation_errors (code);
