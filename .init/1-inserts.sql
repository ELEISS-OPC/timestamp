-- =========================
-- DEFAULT DATA
-- =========================
INSERT INTO role (id, name) VALUES
(1, 'Admin'),
(2, 'Officer'),
(3, 'Employee');


INSERT INTO users (id, first_name, middle_name, last_name, email, password, role_id) VALUES
(1, 'John', 'Allister', 'Doe', 'john.doe@example.com', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 1),
(2, 'Jane', 'Marie', 'Smith', 'jane.smith@example.com', 'c6ba91b90d922e159893f46c387e5dc1b3dc5c101a5a4522f03b987177a24a91', 2),
(3, 'Alice', 'Grace', 'Johnson', 'alice.johnson@example.com', '5efc2b017da4f7736d192a74dde5891369e0685d4d38f2a455b6fcdab282df9c', 3);
