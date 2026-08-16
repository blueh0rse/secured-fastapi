-- Schema and seed data for the users service.
-- Executed automatically by the postgres image entrypoint on first start.

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50)  UNIQUE NOT NULL,
    email           VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role            VARCHAR(20)  NOT NULL DEFAULT 'user',
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action     VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed accounts used for local development and the test suite.
-- Passwords are hashed with MD5 below; the plaintext values live in
-- docker-compose.yml and tests/conftest.py.
INSERT INTO users (username, email, hashed_password, role, is_active) VALUES
    ('admin', 'admin@example.com', 'd746e6a75d583c259678b8c6915c6112', 'admin', TRUE),
    ('alice', 'alice@example.com', '5518012b4067eb6714aa4820fd4780ec', 'user',  TRUE),
    ('bob',   'bob@example.com',   '30831a97f2be7b6cd073b71944c45b4d', 'user',  TRUE),
    ('carol', 'carol@example.com', 'fe962b20904154c2bf2b20ca95bfd68b', 'user',  FALSE),
    ('dave',  'dave@example.com',  'c45620638e5ff5e6020eb9c66a7edd34', 'admin', TRUE);

INSERT INTO audit_logs (user_id, action, ip_address) VALUES
    (1, 'login',           '10.0.0.11'),
    (1, 'user_created',    '10.0.0.11'),
    (2, 'login',           '10.0.0.24'),
    (2, 'profile_updated', '10.0.0.24'),
    (2, 'login',           '10.0.0.25'),
    (3, 'login',           '10.0.0.31'),
    (3, 'profile_updated', '10.0.0.31'),
    (4, 'login',           '10.0.0.42'),
    (5, 'login',           '10.0.0.53'),
    (5, 'user_created',    '10.0.0.53');
