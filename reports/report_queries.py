"""
JCRO Report Queries

All report database access is centralized here.
"""


class ReportQueries:

    # -------------------------------------------------

    def __init__(

        self,

        database,

        survey_id

    ):

        self.database = database

        self.survey_id = survey_id

    # -------------------------------------------------

    def survey(

        self

    ):

        return self.database.current_survey(

            self.survey_id

        )

    # -------------------------------------------------

    def survey_summary(

        self

    ):

        return self.database.current_survey_summary(

            self.survey_id

        )

    # -------------------------------------------------

    def receiver_configuration(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                receiver,

                sample_rate,

                gain,

                overlap,

                dwell,

                started,

                finished

            FROM surveys

            WHERE survey_id = ?

            """,

            (

                self.survey_id,

            )

        ).fetchone()

    # -------------------------------------------------

    def environment_summary(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                AVG(noise_floor)         AS average_noise,

                MIN(noise_floor)         AS minimum_noise,

                MAX(noise_floor)         AS maximum_noise,

                AVG(noise_sigma)         AS average_sigma,

                AVG(detection_threshold) AS average_threshold,

                AVG(detected_signals)    AS average_signals,

                MAX(detected_signals)    AS busiest_window,

                MIN(detected_signals)    AS quietest_window,

                AVG(background_bins)     AS average_background_bins,

                AVG(excluded_bins)       AS average_excluded_bins,

                AVG(minimum_snr)         AS average_minimum_snr,

                MAX(maximum_snr)         AS maximum_snr,

                AVG(median_snr)          AS average_median_snr

            FROM windows

            WHERE survey_id = ?

            """,

            (

                self.survey_id,

            )

        ).fetchone()


    # -------------------------------------------------

    def snr_statistics(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                AVG(peak_snr) AS average_snr,

                MIN(peak_snr) AS minimum_snr,

                MAX(peak_snr) AS maximum_snr,

                COUNT(*)      AS observations

            FROM observations

            WHERE survey_id = ?

            """,

            (

                self.survey_id,

            )

        ).fetchone()

    # -------------------------------------------------

    def bandwidth_statistics(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                AVG(bandwidth) AS average_bandwidth,

                MIN(bandwidth) AS minimum_bandwidth,

                MAX(bandwidth) AS maximum_bandwidth,

                COUNT(*)       AS observations

            FROM observations

            WHERE survey_id = ?

            """,

            (

                self.survey_id,

            )

        ).fetchone()

    # -------------------------------------------------

    def allocation_statistics(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                COUNT(*)                  AS emitters,

                COUNT(*) AS allocations,
                
                COUNT(DISTINCT b.allocation) AS unique_allocations

            FROM signal_allocations b

            JOIN observations o

                ON b.signal_id = o.signal_id

            WHERE

                o.survey_id = ?

            """,

            (

                self.survey_id,

            )

        ).fetchone()

    # -------------------------------------------------

    def known_signal_count(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                COUNT(DISTINCT k.signal_id)

            FROM known_signal_matches k

            JOIN observations o

                ON k.signal_id = o.signal_id

            WHERE

                o.survey_id = ?

            """,

            (

                self.survey_id,

            )

        ).fetchone()[0]

    # -------------------------------------------------

    def unknown_signal_count(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                COUNT(DISTINCT o.signal_id)

            FROM observations o

            LEFT JOIN known_signal_matches k

                ON o.signal_id = k.signal_id

            WHERE

                o.survey_id = ?

                AND

                k.signal_id IS NULL

            """,

            (

                self.survey_id,

            )

        ).fetchone()[0]

    # -------------------------------------------------

    def allocation_activity(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                b.allocation,

                COUNT(*) AS signals

            FROM signal_allocations b

            JOIN observations o

                ON b.signal_id = o.signal_id

            WHERE

                o.survey_id = ?

            GROUP BY

                b.allocation

            ORDER BY

                signals DESC

            """,

            (

                self.survey_id,

            )

        ).fetchall()

    # -------------------------------------------------

    def strongest_emitters(

        self,

        limit=50

    ):

        return self.database.cursor.execute(

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

                s.center_frequency,

                MAX(o.peak_snr) AS peak_snr,

                MAX(s.peak_bandwidth) AS bandwidth,

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

            FROM observations o

            JOIN signals s

                ON o.signal_id = s.signal_id

            LEFT JOIN signal_allocations b

                ON s.signal_id = b.signal_id

            LEFT JOIN historical

                ON historical.signal_id = s.signal_id

            WHERE

                o.survey_id = ?

            GROUP BY

                s.signal_id,
                s.center_frequency,
                historical.historical_average_peak_snr

            ORDER BY

                MAX(o.peak_snr) DESC

            LIMIT ?

            """,

            (

                self.survey_id,
                self.survey_id,
                limit

            )

        ).fetchall()

    # -------------------------------------------------

    def most_observed_signals(

        self,

        limit=50

    ):

        return self.database.cursor.execute(

            """

            SELECT

                s.center_frequency,

                s.observations,

                s.average_bandwidth,

                s.peak_bandwidth,

                s.first_seen,

                s.last_seen,

                AVG(o.peak_snr) AS average_snr,

                b.allocation

            FROM signals s

            JOIN signal_allocations b
                ON s.signal_id = b.signal_id

            JOIN observations o
                ON s.signal_id = o.signal_id

            WHERE b.allocation != 'FM Broadcast'

            GROUP BY

                s.signal_id,

                s.center_frequency,

                s.observations,

                s.average_bandwidth,

                s.peak_bandwidth,

                s.first_seen,

                s.last_seen,

                b.allocation

            ORDER BY

                s.observations DESC,

                s.center_frequency

            LIMIT ?

            """,

            (

                limit,

            )

        ).fetchall()

    # -------------------------------------------------

    def known_signals(

        self,

        limit=30

    ):

        signals = self.database.get_known_signals(

            self.survey_id

        )

        if limit is None:

            return signals

        return signals[:limit]

  # -------------------------------------------------
    def new_signal_identifications(

        self,

        limit=30

    ):

        sql = """

            SELECT

                s.center_frequency,

                MAX(o.peak_snr) AS peak_snr,

                MAX(s.peak_bandwidth) AS bandwidth,

                k.service,

                k.system,

                k.site,

                k.license,

                k.county,

                k.state

            FROM observations o

            JOIN signals s

                ON o.signal_id = s.signal_id

            JOIN known_signal_matches k

                ON s.signal_id = k.signal_id

            WHERE

                o.survey_id = ?

                AND

                s.first_seen >= (

                    SELECT started

                    FROM surveys

                    WHERE survey_id = ?

                )

            GROUP BY

                s.signal_id

            ORDER BY

                MAX(o.peak_snr) DESC

        """

        parameters = [

            self.survey_id,

            self.survey_id

        ]

        if limit is not None:

            sql += "\nLIMIT ?"

            parameters.append(

                limit

            )

        return self.database.cursor.execute(

            sql,

            parameters

        ).fetchall()

  # -------------------------------------------------
    def signal_catalog(

        self,

        limit=None

    ):

        sql = """

            SELECT

                s.center_frequency,

                s.start_frequency,

                s.stop_frequency,

                o.bandwidth,

                o.peak_snr,

                o.noise_floor,

                o.confidence,

                o.timestamp

            FROM observations o

            JOIN signals s

                ON o.signal_id = s.signal_id

            WHERE

                o.survey_id = ?

            ORDER BY

                s.center_frequency

        """

        parameters = [

            self.survey_id

        ]

        if limit is not None:

            sql += "\nLIMIT ?"

            parameters.append(

                limit

            )

        return self.database.cursor.execute(

            sql,

            parameters

        ).fetchall()

    # -------------------------------------------------

    def snr_values(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                peak_snr

            FROM observations

            WHERE

                survey_id = ?

            ORDER BY

                peak_snr

            """,

            (

                self.survey_id,

            )

        ).fetchall()

    # -------------------------------------------------

    def bandwidth_values(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                bandwidth

            FROM observations

            WHERE

                survey_id = ?

            ORDER BY

                bandwidth

            """,

            (

                self.survey_id,

            )

        ).fetchall()

    # -------------------------------------------------

    def frequency_values(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                s.center_frequency

            FROM observations o

            JOIN signals s

                ON o.signal_id = s.signal_id

            WHERE

                o.survey_id = ?

            ORDER BY

                s.center_frequency

            """,

            (

                self.survey_id,

            )

        ).fetchall()

    # -------------------------------------------------

    def historical_allocation_activity(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                allocation,

                COUNT(*) AS signals

            FROM signal_allocations

            GROUP BY

                allocation

            ORDER BY

                signals DESC

            """

        ).fetchall()

    # -------------------------------------------------

    def historical_service_activity(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                service,

                COUNT(*) AS signals

            FROM known_signal_matches

            GROUP BY

                service

            ORDER BY

                signals DESC

            """

        ).fetchall()
    
# -------------------------------------------------

    def historical_strongest_emitters(

        self,

        limit=50

    ):

        return self.database.cursor.execute(

            """

            SELECT

                s.center_frequency,

                MAX(o.peak_snr) AS peak_snr,

                MAX(s.peak_bandwidth) AS bandwidth,

                GROUP_CONCAT(DISTINCT a.allocation) AS allocations,

                k.service,

                MAX(o.timestamp) AS observed

            FROM observations o

            JOIN signals s

                ON o.signal_id = s.signal_id

            LEFT JOIN signal_allocations a

                ON s.signal_id = a.signal_id

            LEFT JOIN known_signal_matches k

                ON s.signal_id = k.signal_id

            GROUP BY

                s.signal_id

            ORDER BY

                peak_snr DESC

            LIMIT ?

            """,

            (

                limit,

            )

        ).fetchall()
    
    # -------------------------------------------------

    def historical_snr_values(

        self

    ):

        return self.database.cursor.execute(

            """

            SELECT

                peak_snr

            FROM observations

            WHERE

                peak_snr IS NOT NULL

            ORDER BY

                peak_snr

            """

        ).fetchall()
    

    def knowledge_identifications(

        self

    ):

        return self.database.get_known_signals(

            self.survey_id

        )