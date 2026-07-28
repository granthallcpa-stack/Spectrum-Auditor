"""
Analysis Models
"""

from dataclasses import dataclass


@dataclass(slots=True)
class BandAllocation:

    start_mhz: float

    stop_mhz: float

    name: str


@dataclass(slots=True)
class IdentifiedBand:

    signal: object

    allocations: list[BandAllocation]
