--Create table appt_types
CREATE TABLE IF NOT EXISTS appt_types (
    appt_type_id SERIAL PRIMARY KEY,
    service_id INTEGER NOT NULL,
    appt_type_name TEXT NOT NULL,
    appt_duration_minutes INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
    updated_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
    UNIQUE (service_id, appt_type_name),
    CHECK (appt_duration_minutes > 0),
    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE
);