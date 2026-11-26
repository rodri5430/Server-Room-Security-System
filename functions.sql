CREATE TABLE tam.users (
    id SERIAL PRIMARY KEY,
    nif VARCHAR(9) NOT NULL UNIQUE CHECK (nif ~ '^[0-9]{9}$'),
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE tam.devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    model VARCHAR(50)
);

CREATE TABLE tam.temp_readings (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES tam.devices(id) ON DELETE CASCADE,
    temperature_value NUMERIC(5,2) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_temp_device_time ON tam.temp_readings (id_device, recorded_at DESC);

CREATE TABLE tam.access_logs (
    id SERIAL PRIMARY KEY,
    id_user INT REFERENCES tam.users(id) ON DELETE SET NULL,
    login_time TIMESTAMPTZ NOT NULL DEFAULT now(),
    login_exit_time TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'success' CHECK (status IN ('success','failed'))
);

CREATE TABLE tam.alarm_events (
    id SERIAL PRIMARY KEY,
    trigger_reason VARCHAR(100) NOT NULL,
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);
-- no máximo 1 alarme ativo
CREATE UNIQUE INDEX one_active_alarm ON tam.alarm_events ((TRUE)) WHERE resolved_at IS NULL;

CREATE TABLE tam.commands (
    id SERIAL PRIMARY KEY,
    id_device INT NOT NULL REFERENCES tam.devices(id) ON DELETE CASCADE,
    id_user INT REFERENCES tam.users(id) ON DELETE SET NULL,
    command_text TEXT NOT NULL,
    executed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    executed_at TIMESTAMPTZ
);
