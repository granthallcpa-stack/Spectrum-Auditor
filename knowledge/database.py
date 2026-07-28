"""
SQLite interface for the RF Knowledge Database.
"""

from pathlib import Path
import csv
import sqlite3

from knowledge.models import KnowledgeSignal

from knowledge.services import get_tolerance

from config import SDR


DATABASE = Path("knowledge/rf_knowledge.db")


class RFKnowledgeDatabase:

    # ---------------------------------------------------------

    def __init__(self, database=DATABASE):

        self.connection = sqlite3.connect(database)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    # ---------------------------------------------------------

    def close(self):

        self.connection.close()

    # ---------------------------------------------------------

    def commit(self):

        self.connection.commit()

    # ---------------------------------------------------------

    def initialize(self, schema="knowledge/schema.sql"):

        schema = Path(schema)

        self.connection.executescript(
            schema.read_text(encoding="utf-8")
        )

        self.commit()

    # ---------------------------------------------------------

    def count(self):

        return self.cursor.execute(

            "SELECT COUNT(*) FROM known_signals"

        ).fetchone()[0]

    # ---------------------------------------------------------

    def insert(self, signal: KnowledgeSignal):

        self.cursor.execute(

            """
            INSERT INTO known_signals (

                frequency,
                service,
                system,
                site,
                license,
                county,
                state

            )

            VALUES (?, ?, ?, ?, ?, ?, ?)

            """,

            (

                signal.frequency,
                signal.service,
                signal.system,
                signal.site,
                signal.license,
                signal.county,
                signal.state

            )

        )

    # ---------------------------------------------------------

    def import_csv(self, filename):

        imported = 0

        with open(filename, newline="", encoding="utf-8") as file:

            reader = csv.DictReader(file)

            for row in reader:

                signal = KnowledgeSignal.from_csv(row)

                self.insert(signal)

                imported += 1

        self.commit()

        return imported

    # ---------------------------------------------------------

    def lookup(self, frequency):

        rows = self.cursor.execute(
            """
            SELECT *
            FROM known_signals
            ORDER BY ABS(frequency - ?)
            LIMIT 25
            """,
            (frequency,)
        ).fetchall()

        if not rows:
            return None

        for row in rows:

            candidate = KnowledgeSignal.from_row(row)

            difference_hz = abs(
                frequency - candidate.frequency
            ) * 1_000_000

            tolerance_hz = get_tolerance(candidate.service)

            if difference_hz <= tolerance_hz:
                return candidate

        return None

    # ---------------------------------------------------------

