-- Initial migration for Oracle XE
-- Run in SQL Developer: copy and execute
@/app/database/schema.sql

-- Example: create sequence & trigger pattern (if you prefer sequences)
-- CREATE SEQUENCE users_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
-- and triggers to populate id from sequence if not using identity columns
