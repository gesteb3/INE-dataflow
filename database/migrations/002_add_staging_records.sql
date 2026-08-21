ALTER TABLE validation_errors
    ALTER COLUMN row_number DROP NOT NULL;

ALTER TABLE validation_errors
    DROP CONSTRAINT IF EXISTS validation_errors_row_number_check;

ALTER TABLE validation_errors
    ADD CONSTRAINT validation_errors_row_number_check
    CHECK (row_number IS NULL OR row_number >= 2);

CREATE TABLE IF NOT EXISTS staged_survey_records (
    id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL REFERENCES survey_batches(id) ON DELETE CASCADE,
    row_number INTEGER NOT NULL CHECK (row_number >= 2),
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

CREATE INDEX IF NOT EXISTS idx_staged_survey_records_batch_id
    ON staged_survey_records (batch_id);
