-- Create table appts
CREATE TABLE IF NOT EXISTS appts (
    appt_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    appt_type_name TEXT NOT NULL,
    appt_starts_at TEXT NOT NULL,
    appt_ends_at TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
    updated_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE,
    FOREIGN KEY (service_id, appt_type_name) REFERENCES appt_types(service_id, appt_type_name) ON DELETE CASCADE
);