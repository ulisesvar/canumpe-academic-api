-- Fake data only. No real student information.

INSERT INTO students (telegram_id, telegram_username, account_number) VALUES
    (1001, 'alice_test', 'A0001'),
    (1002, 'bob_test', 'A0002');

INSERT INTO attendance_sessions (opened_by, opened_at, closes_at, status, closed_at) VALUES
    (1, '2026-09-01 14:00:00+00', '2026-09-01 14:15:00+00', 'CLOSED', '2026-09-01 14:15:00+00'),
    (1, '2026-09-08 14:00:00+00', '2026-09-08 14:15:00+00', 'CLOSED', '2026-09-08 14:15:00+00'),
    (1, '2026-09-11 14:00:00+00', '2026-09-11 14:15:00+00', 'OPEN', NULL);

-- Alice (A0001) attended session 1, missed session 2, session 3 still open.
INSERT INTO attendances (session_id, student_id, latitude, longitude, distance_meters, created_at) VALUES
    (1, 1, 19.4326, -99.1332, 5.2, '2026-09-01 14:03:00+00');

-- Bob (A0002) has no attendance records at all.
