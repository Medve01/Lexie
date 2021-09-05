DROP TABLE IF EXISTS device;
DROP TABLE IF EXISTS devicetype;


CREATE TABLE device (
    device_id TEXT UNIQUE NOT NULL,
    device_name TEXT NOT NULL,
    device_type INT NOT NULL
);

CREATE TABLE devicetype (
    devicetype_name TEXT UNIQUE NOT NULL
);


INSERT INTO device (
    device_id,
    device_name,
    device_type
) VALUES (
    '1234',
    'Test device',
    1
);

INSERT INTO devicetype (rowid,devicetype_name) VALUES (1, 'Test devicetype');
INSERT INTO devicetype (rowid,devicetype_name) VALUES (2, 'Shelly1');
