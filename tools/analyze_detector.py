"""
Detector Validation Analysis

Analyzes detector_validation.csv and reports
summary statistics for detector performance.
"""

from pathlib import Path

import pandas as pd

class DetectorAnalyzer:

    def __init__(self):

        self.file = (

            Path(

                "data/calibration"

            )

            /

            "detector_validation.csv"

        )

        self.df = pd.read_csv(

            self.file

        )

    def general_statistics(

        self

    ):

        print()

        print("=" * 60)

        print("GENERAL")

        print("=" * 60)

        print()

        print(

            f"Signals Detected : {len(self.df):,}"

        )

        print(

            f"Windows Scanned  : {self.df['window'].nunique():,}"

        )

        print(

            f"Signals/Window   : {len(self.df) / self.df['window'].nunique():.2f}"

        )

    def bandwidth_statistics(

        self

    ):

        bw = (

            self.df["bandwidth"]

            /

            1000.0

        )

        print()

        print("=" * 60)

        print("BANDWIDTH (kHz)")

        print("=" * 60)

        print()

        print(

            bw.describe(

                percentiles=[

                    .10,

                    .25,

                    .50,

                    .75,

                    .90

                ]

            )

        )

    def peak_statistics(

        self

    ):

        print()

        print("=" * 60)

        print("PEAK POWER")

        print("=" * 60)

        print()

        print(

            self.df[

                "peak_power"

            ].describe()

        )

    def background_statistics(

        self

    ):

        print()

        print("=" * 60)

        print("BACKGROUND DISPERSION")

        print("=" * 60)

        print()

        print(

            self.df[

                "background_sigma"

            ].describe()

        )

    def boundary_statistics(

        self

    ):

        difference = (

            self.df[

                "left_distance"

            ]

            -

            self.df[

                "right_distance"

            ]

        ).abs()

        print()

        print("=" * 60)

        print("BOUNDARY ASYMMETRY")

        print("=" * 60)

        print()

        print(

            difference.describe()

        )

    def run(

        self

    ):

        self.general_statistics()

        self.bandwidth_statistics()

        self.peak_statistics()

        self.background_statistics()

        self.boundary_statistics()

if __name__ == "__main__":

    DetectorAnalyzer().run()
