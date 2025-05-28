-- This script sets up the PostgreSQL database schema for the project.

CREATE TABLE IF NOT EXISTS info (
    id SERIAL PRIMARY KEY,
    raspberry_id INTEGER NOT NULL,
    people INTEGER NOT NULL,
    humidity INTEGER NOT NULL,
    temperature INTEGER NOT NULL,
    co2 INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN NOT NULL DEFAULT FALSE
);