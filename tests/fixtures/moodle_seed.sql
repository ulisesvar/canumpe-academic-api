-- Fake data only. No real student information.

INSERT INTO mdl_user (id, deleted) VALUES
    (1, 0),  -- Alice, account A0001
    (2, 0),  -- Bob, account A0002
    (3, 1);  -- deleted account, still has a "cuenta" value on record

INSERT INTO mdl_user_info_field (id, shortname, name, datatype, categoryid) VALUES
    (1, 'cuenta', 'No de Cuenta', 'text', 1);

INSERT INTO mdl_user_info_data (id, userid, fieldid, data) VALUES
    (1, 1, 1, 'A0001'),
    (2, 2, 1, 'A0002'),
    (3, 3, 1, 'A0003');

INSERT INTO mdl_course (id, shortname, fullname, startdate, enddate, visible) VALUES
    (10, 'MATH101', 'Mathematics 101', 1767225600, 0, 1),          -- Alice: active, visible
    (20, 'HIST201', 'History 201', 1735689600, 1751328000, 0),     -- Bob: active, hidden
    (30, 'PHYS301', 'Physics 301', 1735689600, 0, 1),              -- disabled enrolment method
    (40, 'CHEM101', 'Chemistry 101', 1735689600, 0, 1);            -- Alice: active, older start date

INSERT INTO mdl_enrol (id, courseid, status) VALUES
    (100, 10, 0),  -- enabled, used by Alice's Math101 enrolment
    (200, 20, 0),  -- enabled, used by Bob's History201 enrolment
    (400, 30, 1),  -- disabled enrolment method on Physics301
    (500, 20, 0),  -- enabled, but Alice's own enrolment via it is suspended
    (600, 40, 0);  -- enabled, used by Alice's Chemistry101 enrolment

INSERT INTO mdl_user_enrolments (id, enrolid, userid, status) VALUES
    (1000, 100, 1, 0),  -- Alice, Math101: active -> should appear
    (1001, 500, 1, 1),  -- Alice, History201: suspended enrolment -> excluded
    (1002, 200, 2, 0),  -- Bob, History201: active -> should appear (hidden course)
    (1003, 400, 1, 0),  -- Alice, Physics301: enrolment method itself disabled -> excluded
    (1004, 600, 1, 0);  -- Alice, Chemistry101: active -> should appear
