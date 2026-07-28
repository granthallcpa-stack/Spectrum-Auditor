"""
RF Measurement

Physical measurements of a detected RF signal.

This module contains no detection or classification logic.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class RFMeasurement:

    start_frequency: float
    stop_frequency: float

    center_frequency: float
    peak_frequency: float

    bandwidth: float

    peak_snr: float
    noise_floor: float
    peak_power: float

    occupied_bins: int

    confidence: float

    timestamp: datetime
