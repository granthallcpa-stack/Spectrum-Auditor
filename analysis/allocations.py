import csv
from pathlib import Path

from analysis.models import BandAllocation

CSV = Path("analysis/data/rf_bands.csv")

_ALLOCATIONS = None


def get_allocations():

    global _ALLOCATIONS

    if _ALLOCATIONS is None:

        _ALLOCATIONS = load_allocations()

    return _ALLOCATIONS


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
