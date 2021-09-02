DROP TABLE IF EXISTS device;

CREATE TABLE device (
    device_id TEXT UNIQUE NOT NULL,
    device_name TEXT NOT NULL,
    device_type TEXT NOT NULL
);
-- lower(hex(randomblob(16))) 

INSERT INTO device (
    device_id,
    device_name,
    device_type
) VALUES (
    '1234',
    'Test device',
    'test devicetype'
);