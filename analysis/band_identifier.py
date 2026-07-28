"""
RF Band Identifier

Assigns RF observations to spectrum allocations.
"""

import csv
from pathlib import Path

from analysis.models import (
    BandAllocation,
    IdentifiedBand
)

from analysis.allocations import get_allocations


CSV = Path("analysis/data/rf_bands.csv")



class BandIdentifier:

    def __init__(self):

        self.allocations = get_allocations()

    # ---------------------------------------------------------

    @staticmethod
    def load_allocations():

        allocations = []

        with CSV.open(
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                allocations.append(

                    BandAllocation(

                        start_mhz=float(
                            row["Band Start (MHz)"]
                        ),

                        stop_mhz=float(
                            row["Band Stop (MHz)"]
                        ),

                        name=row["Band Name"]

                    )

                )

        return allocations

    # ---------------------------------------------------------

    def identify(self, signal):

        frequency = (
            signal.measurement.center_frequency
            / 1e6
        )

        matches = [

            allocation

            for allocation in self.allocations

            if allocation.start_mhz
            <= frequency
            <= allocation.stop_mhz

        ]

        return IdentifiedBand(

            signal=signal,

            allocations=matches

        )

    # ---------------------------------------------------------

    def identify_many(self, signals):

        return [

            self.identify(signal)

            for signal in signals

        ]