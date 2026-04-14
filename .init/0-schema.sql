-- =========================
-- DROP TABLES (optional reset)
-- =========================
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS role CASCADE;
DROP TABLE IF EXISTS default_table CASCADE;

-- =========================
-- BASE TABLE (PARENT)
-- =========================
CREATE TABLE default_table (
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- ROLE TABLE
-- =========================
CREATE TABLE role (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
) INHERITS (default_table);

-- =========================
-- USER/EMPLOYEE TABLE
-- =========================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    avatar_url TEXT,
    avatar_url_preview TEXT,

    CONSTRAINT fk_user_role
        FOREIGN KEY (role_id)
        REFERENCES role(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) INHERITS (default_table);

-- =========================
-- ATTENDANCE TABLE
-- =========================
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,

    time_in TIMESTAMPTZ NOT NULL,
    time_out TIMESTAMPTZ,

    time_in_selfie TEXT NOT NULL,
    time_in_selfie_preview TEXT NOT NULL,
    time_out_selfie TEXT,
    time_out_selfie_preview TEXT,

    time_in_latitude FLOAT NOT NULL,
    time_in_longitude FLOAT NOT NULL,

    time_out_latitude FLOAT,
    time_out_longitude FLOAT,

    CONSTRAINT fk_attendance_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) INHERITS (default_table);

-- =========================
-- INDEXES
-- =========================
CREATE INDEX idx_user_role_id ON users(role_id);
CREATE INDEX idx_attendance_user_id ON attendance(user_id);
CREATE INDEX idx_attendance_time_in ON attendance(time_in);
