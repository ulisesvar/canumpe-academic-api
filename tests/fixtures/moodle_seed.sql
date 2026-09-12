-- Fake data only. No real student information.
--
-- Tests configure MOODLE_COURSE_ID=10, so course 10 (MATH101) is "in scope"
-- and course 20 (HIST201) represents an out-of-scope course that must never
-- be returned, no matter how active the enrolment.

INSERT INTO mdl_user (id, deleted) VALUES
    (1, 0),  -- Alice, account A0001: active, in scope
    (2, 0),  -- Bob, account A0002: active, but only in an out-of-scope course
    (3, 1),  -- deleted account, still has a "cuenta" value on record
    (4, 0),  -- Carol, account A0004: in scope, but enrolment method disabled
    (5, 0),  -- Dave, account A0005: in scope, but own enrolment suspended
    (6, 0),  -- Dup1, account A0009: shares an account number with Dup2
    (7, 0);  -- Dup2, account A0009: shares an account number with Dup1

INSERT INTO mdl_user_info_field (id, shortname, name, datatype, categoryid) VALUES
    (1, 'cuenta', 'No de Cuenta', 'text', 1);

INSERT INTO mdl_user_info_data (id, userid, fieldid, data) VALUES
    (1, 1, 1, 'A0001'),
    (2, 2, 1, 'A0002'),
    (3, 3, 1, 'A0003'),
    (4, 4, 1, 'A0004'),
    (5, 5, 1, 'A0005'),
    (6, 6, 1, 'A0009'),
    (7, 7, 1, 'A0009');

INSERT INTO mdl_course (id, shortname, fullname, startdate, enddate, visible) VALUES
    (10, 'MATH101', 'Mathematics 101', 1767225600, 0, 1),  -- in scope
    (20, 'HIST201', 'History 201', 1735689600, 0, 1);      -- out of scope

INSERT INTO mdl_enrol (id, courseid, status) VALUES
    (100, 10, 0),  -- enabled, Alice's enrolment method in the in-scope course
    (110, 10, 1),  -- disabled enrolment method in the in-scope course
    (120, 10, 0),  -- enabled method, but Dave's own enrolment is suspended
    (130, 10, 0),  -- enabled, Dup1's enrolment method in the in-scope course
    (200, 20, 0);  -- enabled, but this course is out of CANUMPE's scope

INSERT INTO mdl_user_enrolments (id, enrolid, userid, status) VALUES
    (1000, 100, 1, 0),  -- Alice, Math101: active, in scope -> should appear
    (1001, 200, 2, 0),  -- Bob, History201: active, out of scope -> excluded
    (1002, 110, 4, 0),  -- Carol, Math101: enrolment method disabled -> excluded
    (1003, 120, 5, 1),  -- Dave, Math101: own enrolment suspended -> excluded
    (1004, 130, 6, 0);  -- Dup1, Math101: active, in scope (ambiguous identity)
