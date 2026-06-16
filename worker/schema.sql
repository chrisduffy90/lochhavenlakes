-- Run this in the Neon SQL editor

CREATE TABLE IF NOT EXISTS signups (
  id         SERIAL PRIMARY KEY,
  first_name TEXT        NOT NULL,
  last_name  TEXT        NOT NULL DEFAULT '',
  email      TEXT        NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incident_litter (
  id                   SERIAL PRIMARY KEY,
  lake                 TEXT        NOT NULL,
  incident_date        TIMESTAMPTZ,
  location_description TEXT        NOT NULL,
  location_lat         FLOAT,
  location_lng         FLOAT,
  description          TEXT        NOT NULL,
  photo_url            TEXT,
  reporter_name        TEXT,
  reporter_email       TEXT,
  status               TEXT        NOT NULL DEFAULT 'published',
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incident_wildlife (
  id                   SERIAL PRIMARY KEY,
  lake                 TEXT        NOT NULL,
  incident_date        TIMESTAMPTZ,
  location_description TEXT        NOT NULL,
  location_lat         FLOAT,
  location_lng         FLOAT,
  description          TEXT        NOT NULL,
  photo_url            TEXT,
  reporter_name        TEXT,
  reporter_email       TEXT,
  status               TEXT        NOT NULL DEFAULT 'published',
  species              TEXT,
  condition            TEXT        NOT NULL,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incident_water_quality (
  id                   SERIAL PRIMARY KEY,
  lake                 TEXT        NOT NULL,
  incident_date        TIMESTAMPTZ,
  location_description TEXT        NOT NULL,
  location_lat         FLOAT,
  location_lng         FLOAT,
  description          TEXT        NOT NULL,
  photo_url            TEXT,
  reporter_name        TEXT,
  reporter_email       TEXT,
  status               TEXT        NOT NULL DEFAULT 'published',
  observation_type     TEXT        NOT NULL,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
