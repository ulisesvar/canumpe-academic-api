-- Trimmed to the columns the Academic API actually queries, with the same
-- types as the real Moodle PostgreSQL schema. Used only to stand up a
-- disposable test database; never run against production.

CREATE TABLE IF NOT EXISTS mdl_user (
    id      bigint PRIMARY KEY,
    deleted smallint NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS mdl_user_info_field (
    id        bigint PRIMARY KEY,
    shortname character varying(255) NOT NULL,
    name      text NOT NULL,
    datatype  character varying(255) NOT NULL,
    categoryid bigint NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS mdl_user_info_data (
    id      bigint PRIMARY KEY,
    userid  bigint NOT NULL REFERENCES mdl_user(id),
    fieldid bigint NOT NULL REFERENCES mdl_user_info_field(id),
    data    text NOT NULL
);

CREATE TABLE IF NOT EXISTS mdl_course (
    id        bigint PRIMARY KEY,
    shortname character varying(255) NOT NULL DEFAULT '',
    fullname  character varying(1333) NOT NULL DEFAULT '',
    startdate bigint NOT NULL DEFAULT 0,
    enddate   bigint NOT NULL DEFAULT 0,
    visible   smallint NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS mdl_enrol (
    id       bigint PRIMARY KEY,
    courseid bigint NOT NULL REFERENCES mdl_course(id),
    status   bigint NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS mdl_user_enrolments (
    id      bigint PRIMARY KEY,
    enrolid bigint NOT NULL REFERENCES mdl_enrol(id),
    userid  bigint NOT NULL REFERENCES mdl_user(id),
    status  bigint NOT NULL DEFAULT 0
);
