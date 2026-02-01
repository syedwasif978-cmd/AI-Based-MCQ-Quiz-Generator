-- Oracle-compatible schema for AI MCQ Quiz Generator (sequence + trigger pattern)
-- Run these in SQL Developer (XE) as the target schema user (or connect as that user before running).
-- This file safely drops existing objects if present, creates sequences & triggers, defines tables, indexes and FK constraints.

-- DROP TABLES (safe drop if exists)
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE quiz_answer_keys CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN
  IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE quiz_questions CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN
  IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE user_quizzes CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN
  IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE professors CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN
  IF SQLCODE != -942 THEN RAISE; END IF;
END;
/
-- DROP SEQUENCES & TRIGGERS (if present)
BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE professors_seq';
EXCEPTION WHEN OTHERS THEN
  IF SQLCODE != -2289 AND SQLCODE != -1428 AND SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE user_quizzes_seq';
EXCEPTION WHEN OTHERS THEN
  IF SQLCODE != -2289 AND SQLCODE != -1428 AND SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE quiz_questions_seq';
EXCEPTION WHEN OTHERS THEN
  IF SQLCODE != -2289 AND SQLCODE != -1428 AND SQLCODE != -942 THEN RAISE; END IF;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP SEQUENCE quiz_answer_keys_seq';
EXCEPTION WHEN OTHERS THEN
  IF SQLCODE != -2289 AND SQLCODE != -1428 AND SQLCODE != -942 THEN RAISE; END IF;
END;
/
-- Create sequences
CREATE SEQUENCE professors_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE user_quizzes_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE quiz_questions_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;
CREATE SEQUENCE quiz_answer_keys_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;

-- Create tables
CREATE TABLE professors (
  id NUMBER PRIMARY KEY,
  full_name VARCHAR2(255) NOT NULL,
  email VARCHAR2(255) UNIQUE NOT NULL,
  password_hash VARCHAR2(255) NOT NULL,
  subject VARCHAR2(100),
  institution VARCHAR2(255)
);

CREATE OR REPLACE TRIGGER trg_professors_id
BEFORE INSERT ON professors
FOR EACH ROW
WHEN (new.id IS NULL)
BEGIN
  SELECT professors_seq.NEXTVAL INTO :new.id FROM dual;
END;
/
CREATE TABLE user_quizzes (
  id NUMBER PRIMARY KEY,
  user_id NUMBER NOT NULL,
  subject VARCHAR2(100),
  difficulty VARCHAR2(20),
  num_questions NUMBER,
  created_at DATE DEFAULT SYSDATE,
  questions_clob CLOB
);

CREATE OR REPLACE TRIGGER trg_user_quizzes_id
BEFORE INSERT ON user_quizzes
FOR EACH ROW
WHEN (new.id IS NULL)
BEGIN
  SELECT user_quizzes_seq.NEXTVAL INTO :new.id FROM dual;
END;
/
CREATE TABLE quiz_questions (
  id NUMBER PRIMARY KEY,
  quiz_id NUMBER NOT NULL,
  q_text CLOB,
  opt_a VARCHAR2(1000),
  opt_b VARCHAR2(1000),
  opt_c VARCHAR2(1000),
  opt_d VARCHAR2(1000),
  order_index NUMBER
);

CREATE OR REPLACE TRIGGER trg_quiz_questions_id
BEFORE INSERT ON quiz_questions
FOR EACH ROW
WHEN (new.id IS NULL)
BEGIN
  SELECT quiz_questions_seq.NEXTVAL INTO :new.id FROM dual;
END;
/
CREATE TABLE quiz_answer_keys (
  id NUMBER PRIMARY KEY,
  quiz_id NUMBER NOT NULL,
  encrypted_blob BLOB
);

CREATE OR REPLACE TRIGGER trg_quiz_answer_keys_id
BEFORE INSERT ON quiz_answer_keys
FOR EACH ROW
WHEN (new.id IS NULL)
BEGIN
  SELECT quiz_answer_keys_seq.NEXTVAL INTO :new.id FROM dual;
END;
/
-- Indexes
CREATE INDEX idx_user_quizzes_user ON user_quizzes(user_id);
CREATE INDEX idx_quiz_questions_quiz ON quiz_questions(quiz_id);
CREATE INDEX idx_quiz_answers_quiz ON quiz_answer_keys(quiz_id);

-- Optional foreign keys
ALTER TABLE user_quizzes ADD CONSTRAINT fk_user_quizzes_professor FOREIGN KEY (user_id) REFERENCES professors(id);
ALTER TABLE quiz_questions ADD CONSTRAINT fk_quiz_questions_quiz FOREIGN KEY (quiz_id) REFERENCES user_quizzes(id);
ALTER TABLE quiz_answer_keys ADD CONSTRAINT fk_quiz_answer_keys_quiz FOREIGN KEY (quiz_id) REFERENCES user_quizzes(id);

-- Done
