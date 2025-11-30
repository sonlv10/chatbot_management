-- Migration 004: Add training jobs and logs tables
-- Created: 2025-11-30
-- Description: Add tables to track Rasa model training jobs and their logs

-- Table to store training job information
CREATE TABLE IF NOT EXISTS training_jobs (
    id SERIAL PRIMARY KEY,
    bot_id INTEGER NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, running, completed, failed, cancelled
    progress INTEGER DEFAULT 0, -- 0-100 percentage
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    model_path VARCHAR(500), -- path to trained model file
    config JSONB, -- training configuration (epochs, pipeline, etc.)
    metrics JSONB, -- training metrics (accuracy, f1-score, etc.)
    error_message TEXT, -- error details if failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store training logs
CREATE TABLE IF NOT EXISTS training_logs (
    id SERIAL PRIMARY KEY,
    training_job_id INTEGER NOT NULL REFERENCES training_jobs(id) ON DELETE CASCADE,
    log_level VARCHAR(10) NOT NULL, -- DEBUG, INFO, WARNING, ERROR
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) -- stdout, stderr, rasa, custom
);

-- Indexes for better query performance
CREATE INDEX idx_training_jobs_bot_id ON training_jobs(bot_id);
CREATE INDEX idx_training_jobs_status ON training_jobs(status);
CREATE INDEX idx_training_jobs_created_at ON training_jobs(created_at DESC);
CREATE INDEX idx_training_logs_job_id ON training_logs(training_job_id);
CREATE INDEX idx_training_logs_timestamp ON training_logs(timestamp DESC);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_training_jobs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER training_jobs_updated_at_trigger
    BEFORE UPDATE ON training_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_training_jobs_updated_at();

-- Comments for documentation
COMMENT ON TABLE training_jobs IS 'Tracks Rasa model training jobs with status and progress';
COMMENT ON TABLE training_logs IS 'Stores logs generated during training process';
COMMENT ON COLUMN training_jobs.status IS 'Job status: pending, running, completed, failed, cancelled';
COMMENT ON COLUMN training_jobs.progress IS 'Training progress percentage (0-100)';
COMMENT ON COLUMN training_jobs.config IS 'Training configuration in JSON format';
COMMENT ON COLUMN training_jobs.metrics IS 'Training results metrics (accuracy, f1, etc.)';
