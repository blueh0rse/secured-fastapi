#!/bin/sh
# Schema and seed data for the users service.
# Executed automatically by the postgres image entrypoint on first start.
set -eu

psql -v ON_ERROR_STOP=1 \
     --username "$POSTGRES_USER" \
     --dbname "$POSTGRES_DB" \
     -v seed_pw_admin="$SEED_PASSWORD_ADMIN" \
     -v seed_pw_alice="$SEED_PASSWORD_ALICE" \
     -v seed_pw_bob="$SEED_PASSWORD_BOB" \
     -v seed_pw_carol="$SEED_PASSWORD_CAROL" \
     -v seed_pw_dave="$SEED_PASSWORD_DAVE" <<'EOSQL'
CREATE EXTENSION IF NOT EXISTS pgcrypto;

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
-- Plaintext passwords are supplied via SEED_PASSWORD_* environment
-- variables (see .env.example) and hashed here with bcrypt at init time.
INSERT INTO users (username, email, hashed_password, role, is_active) VALUES
    ('admin', 'admin@example.com', crypt(:'seed_pw_admin', gen_salt('bf')), 'admin', TRUE),
    ('alice', 'alice@example.com', crypt(:'seed_pw_alice', gen_salt('bf')), 'user',  TRUE),
    ('bob',   'bob@example.com',   crypt(:'seed_pw_bob', gen_salt('bf')),   'user',  TRUE),
    ('carol', 'carol@example.com', crypt(:'seed_pw_carol', gen_salt('bf')), 'user',  FALSE),
    ('dave',  'dave@example.com',  crypt(:'seed_pw_dave', gen_salt('bf')),  'admin', TRUE);

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
EOSQL
