-- Private schema: never expose classroom records through the public Data API.
CREATE SCHEMA IF NOT EXISTS mathquest;
REVOKE ALL ON SCHEMA mathquest FROM PUBLIC, anon, authenticated;
CREATE TABLE IF NOT EXISTS mathquest.state(id INTEGER PRIMARY KEY,body TEXT NOT NULL,version INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS mathquest.config(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS mathquest.sessions(token TEXT PRIMARY KEY,role TEXT NOT NULL,student_uuid TEXT,expires DOUBLE PRECISION NOT NULL);
CREATE TABLE IF NOT EXISTS mathquest.files(id TEXT PRIMARY KEY,student_uuid TEXT NOT NULL,name TEXT NOT NULL,mime TEXT NOT NULL,body BYTEA NOT NULL,storage_path TEXT);
CREATE TABLE IF NOT EXISTS mathquest.pending_uploads(id TEXT PRIMARY KEY,student_uuid TEXT NOT NULL,name TEXT NOT NULL,mime TEXT NOT NULL,storage_path TEXT NOT NULL,size INTEGER NOT NULL,expires DOUBLE PRECISION NOT NULL);
CREATE TABLE IF NOT EXISTS mathquest.auth_attempts(key TEXT PRIMARY KEY,attempts INTEGER NOT NULL,expires DOUBLE PRECISION NOT NULL);
REVOKE ALL ON ALL TABLES IN SCHEMA mathquest FROM PUBLIC, anon, authenticated;
