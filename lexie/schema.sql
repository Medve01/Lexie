DROP TABLE IF EXISTS device;
DROP TABLE IF EXISTS devicetype;


CREATE TABLE device (
    device_id TEXT UNIQUE NOT NULL,
    device_name TEXT NOT NULL,
    device_type INT NOT NULL
);

CREATE TABLE devicetype (
    devicetype_name TEXT UNIQUE NOT NULL,
    devicetype_manufacturer TEXT NOT NULL
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

INSERT INTO devicetype (rowid,devicetype_name, devicetype_manufacturer) VALUES (1, 'Test devicetype', 'Test');
INSERT INTO devicetype (rowid,devicetype_name, devicetype_manufacturer) VALUES (2, 'Shelly1', 'Shelly');
