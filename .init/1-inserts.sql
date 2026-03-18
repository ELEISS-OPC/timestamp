-- =========================
-- DEFAULT DATA
-- =========================
INSERT INTO role (role_id, role_name) VALUES
(1, 'Admin'),
(2, 'Officer'),
(3, 'Employee');


INSERT INTO employee (employee_id, first_name, middle_name, last_name, email, password, role_id) VALUES
(1, 'John', 'Allister', 'Doe', 'john.doe@example.com', 'password123', 1),
(2, 'Jane', 'Marie', 'Smith', 'jane.smith@example.com', 'password456', 3),
(3, 'Alice', 'Grace', 'Johnson', 'alice.johnson@example.com', 'password789', 3);
