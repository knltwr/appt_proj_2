-- Create table users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
    updated_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
    UNIQUE (email)
);

-- Create table services
CREATE TABLE IF NOT EXISTS services (
    service_id SERIAL PRIMARY KEY,
    host_id INTEGER NOT NULL,
    service_name TEXT NOT NULL,
    street_address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    phone_number TEXT UNIQUE NOT NULL,
    is_open_mo INTEGER NOT NULL DEFAULT 0,
    open_time_mo TEXT NOT NULL,
    close_time_mo TEXT NOT NULL,
    is_open_tu INTEGER NOT NULL DEFAULT 0,
    open_time_tu TEXT NOT NULL,
    close_time_tu TEXT NOT NULL,
    is_open_we INTEGER NOT NULL DEFAULT 0,
    open_time_we TEXT NOT NULL,
    close_time_we TEXT NOT NULL,
    is_open_th INTEGER NOT NULL DEFAULT 0,
    open_time_th TEXT NOT NULL,
    close_time_th TEXT NOT NULL,
    is_open_fr INTEGER NOT NULL DEFAULT 0,
    open_time_fr TEXT NOT NULL,
    close_time_fr TEXT NOT NULL,
    is_open_sa INTEGER NOT NULL DEFAULT 0,
    open_time_sa TEXT NOT NULL,
    close_time_sa TEXT NOT NULL,
    is_open_su INTEGER NOT NULL DEFAULT 0,
    open_time_su TEXT NOT NULL,
    close_time_su TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
    updated_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
    FOREIGN KEY (host_id) REFERENCES users(user_id) ON DELETE CASCADE
);

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