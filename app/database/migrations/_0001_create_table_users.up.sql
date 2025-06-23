-- Create table users
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
    updated_at TIMESTAMP NOT NULL DEFAULT (now() at time zone 'utc'),
    UNIQUE (email)
);