DROP TABLE IF EXISTS device;
DROP TABLE IF EXISTS devicetype;
DROP TABLE IF EXISTS device_attributes;



CREATE TABLE device (
    device_id TEXT UNIQUE NOT NULL,
    device_name TEXT NOT NULL,
    device_type INT NOT NULL, -- relay, light, roller, sensor, etc.
    device_product TEXT NOT NULL, -- shelly1, shelly1l, shelly_ht, etc. always lowercase
    device_manufacturer TEXT NOT NULL -- shelly, xiaomi, etc. always lowercase
);

CREATE TABLE devicetype (
    devicetype_name TEXT UNIQUE NOT NULL,
    devicetype_actions TEXT NOT NULL
);

CREATE TABLE device_attributes (
    device_id TEXT UNIQUE NOT NULL,
    device_attributes TEXT
);

INSERT INTO devicetype (rowid,devicetype_name, devicetype_actions) VALUES (1, 'Relay', '[{"name": "onoff", "icon": "fa fa-toggle-on"}, {"name": "toggle", "icon": "fas fa-bullseye"}]');
INSERT INTO devicetype (rowid,devicetype_name, devicetype_actions) VALUES (2, 'Light', '[{"name": "onoff", "icon": "fa fa-toggle-on"}, {"name": "toggle", "icon": "fas fa-bullseye"}]');

INSERT INTO device (
    device_id,
    device_name,
    device_type,
    device_product,
    device_manufacturer
) VALUES (
    '1234',
    'Bedroom light',
    1,
    'shelly1',
    'shelly'
);

INSERT INTO device_attributes (
    device_id,
    device_attributes
) VALUES (
    '1234',
    '{"ip_address": "192.168.100.37"}'
);
INSERT INTO device (
    device_id,
    device_name,
    device_type,
    device_product,
    device_manufacturer
) VALUES (
    '4321',
    'Office light',
    1,
    'shelly1',
    'shelly'
);


INSERT INTO device_attributes (
    device_id,
    device_attributes
) VALUES (
    '4321',
    '{"ip_address": "192.168.0.50"}'
);