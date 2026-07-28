DROP TABLE IF EXISTS known_signals;

CREATE TABLE known_signals (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    frequency REAL NOT NULL,

    service TEXT NOT NULL,

    system TEXT NOT NULL,

    site TEXT NOT NULL,

    license TEXT NOT NULL,

    county TEXT NOT NULL,

    state TEXT NOT NULL

);

CREATE INDEX idx_frequency
ON known_signals(frequency);

CREATE INDEX idx_service
ON known_signals(service);

CREATE INDEX idx_county
ON known_signals(county);
