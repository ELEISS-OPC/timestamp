-- =========================
-- DROP TABLES (optional reset)
-- =========================
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS employee CASCADE;
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
    role_name TEXT NOT NULL UNIQUE
) INHERITS (default_table);

-- =========================
-- USER/EMPLOYEE TABLE
-- =========================
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    middle_name TEXT,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role_id INTEGER NOT NULL,

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
    employee_id INTEGER NOT NULL,

    time_in TIMESTAMP NOT NULL,
    time_out TIMESTAMP,

    time_in_selfie TEXT NOT NULL,
    time_out_selfie TEXT,

    time_in_latitude FLOAT NOT NULL,
    time_in_longitude FLOAT NOT NULL,

    time_out_latitude FLOAT,
    time_out_longitude FLOAT,

    CONSTRAINT fk_attendance_employee
        FOREIGN KEY (employee_id)
        REFERENCES user(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) INHERITS (default_table);

-- =========================
-- INDEXES
-- =========================
CREATE INDEX idx_user_role_id ON user(role_id);
CREATE INDEX idx_attendance_employee_id ON attendance(employee_id);
CREATE INDEX idx_attendance_time_in ON attendance(time_in);
