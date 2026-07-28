"""
Persistent RF Observatory Database
"""

from pathlib import Path
from analysis import signal
from config import SDR
import sqlite3
import numpy as np
from core.debug import debug


DATABASE_PATH = Path("data/rf_observatory.db")


class RFDatabase:

    def __init__(self):

        DATABASE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = sqlite3.connect(
            DATABASE_PATH
        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

        self.frequency_tolerance = 1000.0   # Hz
        self.merge_guard_band = SDR.merge_guard_band_hz

        self._create_schema()

    # -------------------------------------------------

    def frequency_bucket(
        self,
        frequency
    ):

        return int(
            round(
                frequency / 1000
            )
        )

    # -------------------------------------------------

    def store_signal(
        self,
        signal
    ):
        measurement = signal.measurement

        candidates = self.cursor.execute(
            """
            SELECT

                signal_id,

                observations,

                average_bandwidth,

                peak_bandwidth,

                center_frequency,

                start_frequency,

                stop_frequency

            FROM signals

            WHERE

                stop_frequency >= ?

                AND

                start_frequency <= ?
            """,
            (
                measurement.start_frequency - self.merge_guard_band,
                measurement.stop_frequency + self.merge_guard_band
            )
        ).fetchall()

        row = None
        best_score = float("-inf")

        candidate_results = []

        for candidate in candidates:

            overlap = (
                min(
                    candidate["stop_frequency"],
                    measurement.stop_frequency
                )
                -
                max(
                    candidate["start_frequency"],
                    measurement.start_frequency
                )
            )

            distance = max(
                candidate["start_frequency"] - measurement.stop_frequency,
                measurement.start_frequency - candidate["stop_frequency"],
                0
            )

            candidate_bandwidth = (
                candidate["stop_frequency"] -
                candidate["start_frequency"]
            )

            bandwidth_difference = abs(
                candidate_bandwidth -
                measurement.bandwidth
            )

            accepted = (
                distance <= self.merge_guard_band
            )

            score = (
                overlap
                - distance
                - bandwidth_difference
            )

            candidate_results.append({

                "signal_id": candidate["signal_id"],

                "start": candidate["start_frequency"],

                "stop": candidate["stop_frequency"],

                "distance": distance,

                "overlap": overlap,

                "candidate_bandwidth": candidate_bandwidth,

                "bandwidth_difference": bandwidth_difference,

                "score": score,

                "accepted": accepted

            })

            if accepted:

                if score > best_score:

                    best_score = score
                    row = candidate

        bucket = self.frequency_bucket(
            measurement.center_frequency
        )


        if row is None:

            cursor = self.cursor.execute(
                """
                INSERT INTO signals(

                    frequency_bucket,

                    center_frequency,

                    start_frequency,

                    stop_frequency,

                    average_bandwidth,

                    peak_bandwidth,

                    first_seen,

                    last_seen,

                    observations

                )

                VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    bucket,
                    measurement.center_frequency,
                    measurement.start_frequency,
                    measurement.stop_frequency,
                    measurement.bandwidth,
                    measurement.bandwidth,
                    measurement.timestamp.isoformat(),
                    measurement.timestamp.isoformat(),
                    1
                )
            )

            self.connection.commit()

            return cursor.lastrowid

        signal_id = row["signal_id"]

        observations = row["observations"]

        average_bandwidth = row["average_bandwidth"]

        peak_bandwidth = row["peak_bandwidth"]

        new_average = (

            average_bandwidth *
            observations +

            measurement.bandwidth

        ) / (

            observations + 1

        )

        new_peak = max(

            peak_bandwidth,

            measurement.bandwidth

        )

        self.cursor.execute(
            """
            UPDATE signals

            SET

                last_seen=?,

                observations=?,

                average_bandwidth=?,

                peak_bandwidth=?

            WHERE signal_id=?
            """,
            (
                measurement.timestamp.isoformat(),

                observations + 1,

                new_average,

                new_peak,

                signal_id
            )
        )

        self.connection.commit()

        return signal_id

    # -------------------------------------------------

    def store_observation(
        self,
        survey_id,
        window_id,
        emitter_id,
        signal
    ):

        measurement = signal.measurement

        self.cursor.execute(
            """
            INSERT INTO observations(

                survey_id,

                window_id,

                signal_id,

                timestamp,

                peak_power,

                peak_snr,

                noise_floor,

                confidence,

                bandwidth

            )

            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                survey_id,

                window_id,

                emitter_id,

                measurement.timestamp.isoformat(),

                measurement.peak_power,

                measurement.peak_snr,

                measurement.noise_floor,

                measurement.confidence,

                measurement.bandwidth
            )
        )

        self.connection.commit()

    # -------------------------------------------------

    def start_survey(
        self,
        started,
        receiver,
        sample_rate,
        gain,
        overlap,
        dwell
    ):

        cursor = self.cursor.execute(
            """
            INSERT INTO surveys(

                started,

                receiver,

                sample_rate,

                gain,

                overlap,

                dwell

            )

            VALUES(?,?,?,?,?,?)
            """,
            (
                started.isoformat(),

                receiver,

                sample_rate,

                gain,

                overlap,

                dwell
            )
        )

        self.connection.commit()

        return cursor.lastrowid

    # -------------------------------------------------

    def store_window(

        self,

        survey_id,

        observation,

        policy,

        signals

    ):

        snrs = [

            signal.measurement.peak_snr

            for signal in signals

        ]

        minimum_snr = (

            float(

                np.min(

                    snrs

                )

            )

            if snrs else None

        )

        maximum_snr = (

            float(

                np.max(

                    snrs

                )

            )

            if snrs else None

        )

        median_snr = (

            float(

                np.median(

                    snrs

                )

            )

            if snrs else None

        )

        cursor = self.cursor.execute(

            """

            INSERT INTO windows(

                survey_id,

                timestamp,

                center_frequency,

                noise_floor,

                noise_sigma,

                detection_threshold,

                background_bins,

                excluded_bins,

                detected_signals,

                minimum_snr,

                maximum_snr,

                median_snr

            )

            VALUES(

                ?,?,?,?,?,?,?,?,?,?,?,?

            )

            """,

            (

                survey_id,

                observation.capture.timestamp.isoformat(),

                observation.capture.center_frequency,

                policy.noise_floor_db,

                policy.noise_sigma_db,

                policy.detection_threshold_db,

                policy.background_bins,

                policy.excluded_bins,

                len(

                    signals

                ),

                minimum_snr,

                maximum_snr,

                median_snr

            )

        )

        self.connection.commit()

        return cursor.lastrowid

    # -------------------------------------------------

    def current_survey(
        self,
        survey_id
    ):

        return self.cursor.execute(
            """
            SELECT

                survey_id,

                started,

                finished,

                duration,

                windows,

                signals,

                receiver,

                sample_rate,

                gain

            FROM surveys

            WHERE survey_id = ?
            """,
            (
                survey_id,
            )
        ).fetchone()

    # -------------------------------------------------

    def export_signal_catalog(

        self,

        survey_id,

        filename

    ):

        import csv

        rows = self.cursor.execute(

            """

            SELECT

                s.center_frequency,

                o.timestamp,

                o.bandwidth,

                o.peak_power,

                o.peak_snr,

                o.noise_floor,

                o.confidence,

                s.observations

            FROM observations o

            JOIN signals s

                ON o.signal_id = s.signal_id

            WHERE

                o.survey_id = ?

            ORDER BY

                s.center_frequency

            """,

            (

                survey_id,

            )

        ).fetchall()

        with open(

            filename,

            "w",

            newline="",

            encoding="utf-8"

        ) as file:

            writer = csv.writer(

                file

            )

            writer.writerow(

                [
                    "Timestamp",

                    "Center Frequency (MHz)",

                    "Bandwidth (Hz)",

                    "Peak Power (dB)",

                    "Peak SNR (dB)",

                    "Noise Floor (dB)",

                    "Confidence",

                    "Observations"
                ]
            )

            for row in rows:

                writer.writerow(

                    [
                        row["timestamp"],

                        row["center_frequency"] / 1e6,

                        row["bandwidth"],

                        row["peak_power"],

                        row["peak_snr"],

                        row["noise_floor"],

                        row["confidence"],

                        row["observations"]
                    ]

                )


    def current_survey_summary(
        self,
        survey_id
    ):

        survey = self.current_survey(
            survey_id
        )

        strongest = self.cursor.execute(
            """
            SELECT

                MAX(peak_snr)

            FROM observations

            WHERE survey_id = ?
            """,
            (
                survey_id,
            )
        ).fetchone()[0]

        new_emitters = self.cursor.execute(
            """
            SELECT COUNT(*)

            FROM signals

            WHERE first_seen >= (
                SELECT started

                FROM surveys

                WHERE survey_id = ?
            )
            """,
            (
                survey_id,
            )
        ).fetchone()[0]

        known_emitters = self.cursor.execute(
            """
            SELECT COUNT(DISTINCT k.signal_id)

            FROM known_signal_matches k

            JOIN observations o

            ON o.signal_id = k.signal_id

            WHERE o.survey_id = ?
            """,
            (
                survey_id,
            )
        ).fetchone()[0]

        unknown_emitters = survey["signals"] - known_emitters

        return {

            "survey": survey,

            "duration": survey["duration"],

            "windows": survey["windows"],

            "signals": survey["signals"],

            "average_signals":

                survey["signals"] /
                max(
                    survey["windows"],
                    1
                ),

            "new_emitters": new_emitters,

            "known_emitters": known_emitters,

            "unknown_emitters": unknown_emitters,

            "strongest_signal": strongest

        }

    # -------------------------------------------------

    def strongest_signals(
        self,
        survey_id,
        limit=25
    ):

        return self.cursor.execute(
            """
            SELECT

                o.signal_id,

                s.center_frequency,

                COALESCE(
                    b.allocation,
                    'Unknown'
                ) AS band,

                o.peak_snr,

                o.bandwidth,

                o.timestamp

            FROM observations o

            JOIN signals s

                ON o.signal_id=s.signal_id

            LEFT JOIN signal_allocations b

                ON s.signal_id=b.signal_id

            WHERE

                o.survey_id=?

            ORDER BY

                o.peak_snr DESC

            LIMIT ?
            """,
            (
                survey_id,
                limit
            )
        ).fetchall()

    # -------------------------------------------------

    def new_emitters(
        self,
        survey_id,
        limit=25
    ):

        return self.cursor.execute(
            """
            SELECT

                s.signal_id,

                s.center_frequency,

                COALESCE(
                    b.allocation,
                    'Unknown'
                ) AS band,

                MAX(o.peak_snr) AS peak_snr,

                s.first_seen

            FROM signals s

            JOIN observations o

                ON s.signal_id=o.signal_id

            LEFT JOIN signal_allocations b

                ON s.signal_id=b.signal_id

            WHERE

                s.first_seen >= (

                    SELECT started

                    FROM surveys

                    WHERE survey_id=?

                )

            GROUP BY

                s.signal_id

            ORDER BY

                peak_snr DESC

            LIMIT ?
            """,
            (
                survey_id,
                limit
            )
        ).fetchall()


    # -------------------------------------------------

    def current_allocation_activity(
        self,
        survey_id
    ):

        return self.cursor.execute(
            """
            SELECT

                COALESCE(
                    a.allocation,
                    'Unknown'
                ) AS allocation,

                COUNT(*) AS observations,

                AVG(o.peak_snr) AS average_snr

            FROM observations o

            LEFT JOIN signal_allocations a

                ON o.signal_id = a.signal_id

            WHERE

                o.survey_id = ?

            GROUP BY

                allocation

            ORDER BY

                observations DESC
            """,
            (
                survey_id,
            )
        ).fetchall()

    # -------------------------------------------------

    def historical_allocation_statistics(self):

        return self.cursor.execute(
            """
            SELECT

                COALESCE(
                    allocation,
                    'Unknown'
                ) AS allocation,

                COUNT(*) AS emitters

            FROM signal_allocations

            GROUP BY

                allocation

            ORDER BY

                emitters DESC
            """
        ).fetchall()

    # -------------------------------------------------

    def historical_trends(self):

        return self.cursor.execute(
            """
            SELECT

                survey_id,

                started,

                duration,

                windows,

                signals

            FROM surveys

            ORDER BY

                survey_id
            """
        ).fetchall()

    # -------------------------------------------------

    def finish_survey(
        self,
        survey_id,
        finished,
        duration,
        windows,
        signals
    ):

        self.cursor.execute(
            """
            UPDATE surveys

            SET

                finished=?,

                duration=?,

                windows=?,

                signals=?

            WHERE survey_id=?
            """,
            (
                finished.isoformat(),

                duration,

                windows,

                signals,

                survey_id
            )
        )

        self.connection.commit()

    # -------------------------------------------------

    def store_allocations(

        self,

        signal_id,

        identified_band

    ):

        self.cursor.execute(

            """

            DELETE FROM signal_allocations

            WHERE signal_id = ?

            """,

            (

                signal_id,

            )

        )

        timestamp = (

            identified_band.signal

            .measurement

            .timestamp

            .isoformat()

        )

        for allocation in identified_band.allocations:

            self.cursor.execute(

                """

                INSERT INTO signal_allocations(

                    signal_id,

                    timestamp,

                    allocation

                )

                VALUES(?,?,?)

                """,

                (

                    signal_id,

                    timestamp,

                    allocation.name

                )

            )

        self.connection.commit()

    # -------------------------------------------------

    def store_known_signal(
        self,
        signal_id,
        known_signal,
        timestamp
    ):

        row = self.cursor.execute(
            """
            SELECT signal_id

            FROM known_signal_matches

            WHERE signal_id = ?

            LIMIT 1
            """,
            (
                signal_id,
            )
        ).fetchone()

        if row is not None:

            return

        self.cursor.execute(
            """
            INSERT INTO known_signal_matches(

                signal_id,

                frequency,

                service,

                system,

                site,

                license,

                county,

                state,

                identified

            )

            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                signal_id,

                known_signal.frequency,

                known_signal.service,

                known_signal.system,

                known_signal.site,

                known_signal.license,

                known_signal.county,

                known_signal.state,

                timestamp.isoformat()
            )
        )

        self.connection.commit()

    # -------------------------------------------------

    def store_fingerprint(
        self,
        emitter_id,
        signal
    ):
        measurement = signal.measurement

        self.cursor.execute(
            """
            INSERT INTO fingerprints(

                signal_id,

                timestamp,

                peak_snr,

                average_snr,

                bandwidth,

                confidence,

                variance,

                center_frequency

            )

            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                emitter_id,

                measurement.timestamp.isoformat(),

                measurement.peak_snr,

                measurement.peak_snr,

                measurement.bandwidth,

                measurement.confidence,

                0.0,

                measurement.center_frequency
            )
        )

        self.connection.commit()

    # -------------------------------------------------

    def close(self):

        self.connection.commit()

        self.connection.close()

    # -------------------------------------------------

    def commit(self):

        self.connection.commit()

    # -------------------------------------------------

    def _create_schema(self):

        self.cursor.executescript("""

PRAGMA journal_mode=WAL;

PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS windows(

    window_id INTEGER PRIMARY KEY,

    survey_id INTEGER NOT NULL,

    timestamp TEXT NOT NULL,

    center_frequency REAL NOT NULL,

    noise_floor REAL NOT NULL,

    noise_sigma REAL NOT NULL,

    detection_threshold REAL NOT NULL,

    background_bins INTEGER NOT NULL,

    excluded_bins INTEGER NOT NULL,

    detected_signals INTEGER NOT NULL,

    minimum_snr REAL,

    maximum_snr REAL,

    median_snr REAL,

    FOREIGN KEY(

        survey_id

    )

    REFERENCES surveys(

        survey_id

    )

);

CREATE TABLE IF NOT EXISTS surveys(

    survey_id INTEGER PRIMARY KEY AUTOINCREMENT,

    started TEXT,

    finished TEXT,

    duration REAL,

    windows INTEGER,

    signals INTEGER,

    receiver TEXT,

    sample_rate REAL,

    gain REAL,

    overlap REAL,

    dwell REAL

);

CREATE TABLE IF NOT EXISTS signals(

    signal_id INTEGER PRIMARY KEY AUTOINCREMENT,

    frequency_bucket INTEGER,

    center_frequency REAL,

    start_frequency REAL,

    stop_frequency REAL,

    average_bandwidth REAL,

    peak_bandwidth REAL,

    first_seen TEXT,

    last_seen TEXT,

    observations INTEGER DEFAULT 0

);

CREATE TABLE IF NOT EXISTS observations(

    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,

    survey_id INTEGER,

    window_id INTEGER,

    signal_id INTEGER,

    timestamp TEXT,

    peak_power REAL,

    peak_snr REAL,

    noise_floor REAL,

    confidence REAL,

    bandwidth REAL,

    FOREIGN KEY(survey_id)
        REFERENCES surveys(survey_id),

    FOREIGN KEY(window_id)
        REFERENCES windows(window_id),

    FOREIGN KEY(signal_id)
        REFERENCES signals(signal_id)

);

CREATE TABLE IF NOT EXISTS signal_allocations(

    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,

    signal_id INTEGER NOT NULL,

    timestamp TEXT NOT NULL,

    allocation TEXT NOT NULL,

    FOREIGN KEY(signal_id)
        REFERENCES signals(signal_id)

);

CREATE TABLE IF NOT EXISTS known_signal_matches(

    signal_id INTEGER PRIMARY KEY,

    frequency REAL,

    service TEXT,

    system TEXT,

    site TEXT,

    license TEXT,

    county TEXT,

    state TEXT,

    identified TEXT,

    FOREIGN KEY(signal_id)
        REFERENCES signals(signal_id)

);

CREATE TABLE IF NOT EXISTS fingerprints(

    fingerprint_id INTEGER PRIMARY KEY AUTOINCREMENT,

    signal_id INTEGER,

    timestamp TEXT,

    peak_snr REAL,

    average_snr REAL,

    bandwidth REAL,

    confidence REAL,

    variance REAL,

    center_frequency REAL,

    FOREIGN KEY(signal_id)
        REFERENCES signals(signal_id)

);

CREATE INDEX IF NOT EXISTS idx_signal_bucket
ON signals(frequency_bucket);

CREATE INDEX IF NOT EXISTS idx_observation_time
ON observations(timestamp);

CREATE INDEX IF NOT EXISTS idx_allocation
ON signal_allocations(allocation);

CREATE INDEX IF NOT EXISTS idx_known_service
ON known_signal_matches(service);

""")

        self.connection.commit()

    def top_emitters(
        self,
        limit=25
    ):

        return self.cursor.execute(
            """
            SELECT

                s.signal_id,

                s.center_frequency,

                s.observations,

                s.average_bandwidth,

                s.first_seen,

                s.last_seen,

                COALESCE(
                    GROUP_CONCAT(DISTINCT b.allocation),
                    'Unknown'
                ) AS allocations

            FROM signals s

            LEFT JOIN signal_allocations b

                ON s.signal_id = b.signal_id

            GROUP BY s.signal_id

            ORDER BY s.observations DESC

            LIMIT ?
            """,
            (
                limit,
            )
        ).fetchall()

    # -------------------------------------------------

    def newest_emitters(
        self,
        limit=25
    ):

        return self.cursor.execute(
            """
            SELECT *

            FROM signals

            ORDER BY first_seen DESC

            LIMIT ?
            """,
            (
                limit,
            )
        ).fetchall()

    # -------------------------------------------------

    def allocation_summary(self):

        total = self.cursor.execute(
            """
            SELECT COUNT(*)
            FROM signal_allocations
            """
        ).fetchone()[0]

        rows = self.cursor.execute(
            """
            SELECT

                allocation,

                COUNT(*) AS count

            FROM signal_allocations

            GROUP BY allocation

            ORDER BY count DESC
            """
        ).fetchall()

        results = []

        for row in rows:

            percent = 0.0

            if total:

                percent = (
                    row["count"] /
                    total
                ) * 100.0

            results.append({

                "allocation": row["allocation"],

                "count": row["count"],

                "percent": percent

            })

        return results

    # -------------------------------------------------

    def occupancy(self):

        return self.cursor.execute(
            """
            SELECT

                signal_id,

                COUNT(*) AS observations

            FROM observations

            GROUP BY signal_id

            ORDER BY observations DESC
            """
        ).fetchall()

    # -------------------------------------------------

    def strongest_emitters(
        self,
        survey_id,
        limit=25
    ):

        return self.cursor.execute(
            """
            WITH historical AS (

                SELECT

                    signal_id,

                    AVG(survey_peak_snr) AS historical_average_peak_snr

                FROM (

                    SELECT

                        signal_id,
                        survey_peak_snr,

                        ROW_NUMBER() OVER (

                            PARTITION BY signal_id
                            ORDER BY survey_id DESC

                        ) AS rn

                    FROM (

                        SELECT

                            signal_id,
                            survey_id,

                            MAX(peak_snr) AS survey_peak_snr

                        FROM observations

                        WHERE

                            survey_id < ?
                            AND peak_snr IS NOT NULL

                        GROUP BY

                            signal_id,
                            survey_id

                    )

                )

                WHERE rn <= 15

                GROUP BY signal_id

            )

            SELECT

                s.signal_id,

                s.center_frequency,

                s.observations,

                s.average_bandwidth,

                MAX(o.peak_snr) AS peak_snr,

                historical.historical_average_peak_snr,

                CASE

                    WHEN historical.historical_average_peak_snr IS NULL
                        OR historical.historical_average_peak_snr = 0

                    THEN NULL

                    ELSE

                        (
                            (
                                MAX(o.peak_snr)
                                - historical.historical_average_peak_snr
                            )
                            /
                            historical.historical_average_peak_snr
                        ) * 100.0

                END AS percent_difference,

                COALESCE(
                    GROUP_CONCAT(DISTINCT b.allocation),
                    'Unknown'
                ) AS allocations

            FROM signals s

            JOIN observations o

                ON s.signal_id = o.signal_id

            LEFT JOIN signal_allocations b

                ON s.signal_id = b.signal_id

            LEFT JOIN historical

                ON historical.signal_id = s.signal_id

            WHERE

                o.survey_id = ?

            GROUP BY

                s.signal_id,
                s.center_frequency,
                s.observations,
                s.average_bandwidth,
                historical.historical_average_peak_snr

            ORDER BY

                peak_snr DESC

            LIMIT ?

            """,
            (
                survey_id,
                survey_id,
                limit,
            )
        ).fetchall()

    # -------------------------------------------------

    def survey_summary(self):

        return self.cursor.execute(
            """
            SELECT

                COUNT(*) AS surveys,

                SUM(signals) AS signals,

                SUM(windows) AS windows,

                AVG(duration) AS average_duration

            FROM surveys
            """
        ).fetchone()

    # -------------------------------------------------

    def database_summary(self):

        return {

            "surveys": self.cursor.execute(
                "SELECT COUNT(*) FROM surveys"
            ).fetchone()[0],

            "emitters": self.cursor.execute(
                "SELECT COUNT(*) FROM signals"
            ).fetchone()[0],

            "observations": self.cursor.execute(
                "SELECT COUNT(*) FROM observations"
            ).fetchone()[0],

            "allocations": self.cursor.execute(
                "SELECT COUNT(*) FROM signal_allocations"
            ).fetchone()[0],

            "fingerprints": self.cursor.execute(
                "SELECT COUNT(*) FROM fingerprints"
            ).fetchone()[0]

        }

    # -------------------------------------------------

    def survey_intelligence(
        self,
        survey_id
    ):

        survey = self.current_survey(
            survey_id
        )

        total_observations = self.cursor.execute(
            """
            SELECT COUNT(*)
            FROM observations
            WHERE survey_id = ?
            """,
            (
                survey_id,
            )
        ).fetchone()[0]

        unknown = self.cursor.execute(
            """
            SELECT COUNT(DISTINCT o.signal_id)

            FROM observations o

            LEFT JOIN signal_allocations b

                ON o.signal_id = b.signal_id

            WHERE

                o.survey_id = ?

                AND

                COALESCE(b.allocation, 'Unknown') = 'Unknown'
            """,
            (
                survey_id,
            )
        ).fetchone()[0]

        return {

            "windows": survey["windows"],

            "signals": survey["signals"],

            "observations": total_observations,

            "unknown": unknown

        }

    def get_known_signals(self, survey_id):

        cursor = self.cursor.execute(
            """
            WITH historical AS (

                SELECT

                    signal_id,

                    AVG(survey_peak_snr) AS historical_average_peak_snr

                FROM (

                    SELECT

                        signal_id,
                        survey_peak_snr,

                        ROW_NUMBER() OVER (

                            PARTITION BY signal_id
                            ORDER BY survey_id DESC

                        ) AS rn

                    FROM (

                        SELECT

                            signal_id,
                            survey_id,

                            MAX(peak_snr) AS survey_peak_snr

                        FROM observations

                        WHERE

                            survey_id < ?
                            AND peak_snr IS NOT NULL

                        GROUP BY

                            signal_id,
                            survey_id

                    )

                )

                WHERE rn <= 7

                GROUP BY signal_id

            ),

            historical_bandwidth AS (

                SELECT

                    signal_id,

                    AVG(survey_bandwidth) AS historical_average_bandwidth

                FROM (

                    SELECT

                        signal_id,
                        survey_bandwidth,

                        ROW_NUMBER() OVER (

                            PARTITION BY signal_id
                            ORDER BY survey_id DESC

                        ) AS rn

                    FROM (

                        SELECT

                            signal_id,
                            survey_id,

                            AVG(bandwidth) AS survey_bandwidth

                        FROM observations

                        WHERE

                            survey_id < ?
                            AND bandwidth IS NOT NULL

                        GROUP BY

                            signal_id,
                            survey_id

                    )

                )

                WHERE rn <= 7

                GROUP BY signal_id

            )

            SELECT

                k.frequency,
                k.service,
                k.system,
                k.site,
                k.license,
                k.county,
                k.state,
                k.identified,

                MAX(o.peak_snr) AS current_peak_snr,

                AVG(o.bandwidth) AS current_bandwidth,

                historical.historical_average_peak_snr,

                historical_bandwidth.historical_average_bandwidth,

                CASE

                    WHEN historical.historical_average_peak_snr IS NULL
                        OR historical.historical_average_peak_snr = 0

                    THEN NULL

                    ELSE

                        (
                            (
                                MAX(o.peak_snr)
                                - historical.historical_average_peak_snr
                            )
                            /
                            historical.historical_average_peak_snr
                        ) * 100.0

                END AS percent_difference

            FROM known_signal_matches k

            JOIN observations o

                ON o.signal_id = k.signal_id

            LEFT JOIN historical

                ON historical.signal_id = k.signal_id

            LEFT JOIN historical_bandwidth

                ON historical_bandwidth.signal_id = k.signal_id

            WHERE

                o.survey_id = ?

            GROUP BY

                k.signal_id,
                k.frequency,
                k.service,
                k.system,
                k.site,
                k.license,
                k.county,
                k.state,
                k.identified,
                historical.historical_average_peak_snr,
                historical_bandwidth.historical_average_bandwidth

            ORDER BY

                ABS(COALESCE(percent_difference, 0)) DESC,
                current_peak_snr DESC

            """,
            (
                survey_id,
                survey_id,
                survey_id,
            )
        )

        return [dict(row) for row in cursor.fetchall()]