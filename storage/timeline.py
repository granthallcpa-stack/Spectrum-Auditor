"""
Timeline Engine

Persistent historical record of every detected RF signal.
"""

from pathlib import Path
from datetime import UTC
import pandas as pd


TIMELINE_DIR = Path("data/timeline")
TIMELINE_DIR.mkdir(parents=True, exist_ok=True)


class Timeline:

    def __init__(self):

        self.records = []

    # -----------------------------------------------------

    def add_scan(self, signals, timestamp):

        for signal in signals:

            measurement = signal.measurement

            self.records.append({

                "timestamp": timestamp,

                "center_frequency": measurement.center_frequency,

                "start_frequency": measurement.start_frequency,

                "stop_frequency": measurement.stop_frequency,

                "bandwidth": measurement.bandwidth,

                "peak_snr": measurement.peak_snr,

                "confidence": measurement.confidence,

            })

    # -----------------------------------------------------

    def dataframe(self):

        return pd.DataFrame(self.records)

    # -----------------------------------------------------

    def save(self):

        if not self.records:

            return None

        df = self.dataframe()

        filename = (

            TIMELINE_DIR /

            f"{df['timestamp'].max():%Y%m%d_%H%M%S}.parquet"

        )

        df.to_parquet(

            filename,

            index=False

        )

        return filename

    # -----------------------------------------------------

    @staticmethod

    def load(path):

        return pd.read_parquet(path)
