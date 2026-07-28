"""
Signal Database
"""

from dataclasses import dataclass
from datetime import datetime
import numpy as np


@dataclass(slots=True)
class SignalHistory:

    center_frequency: float

    observations: int = 0

    first_seen: datetime | None = None
    last_seen: datetime | None = None

    peak_snr: float = -np.inf
    average_snr: float = 0.0

    peak_bandwidth: float = 0.0
    average_bandwidth: float = 0.0

    average_noise_floor: float = 0.0

    def update(self, signal):

        measurement = signal.measurement

        self.observations += 1

        if self.first_seen is None:
            self.first_seen = measurement.timestamp

        self.last_seen = measurement.timestamp

        self.average_snr += (
            measurement.peak_snr - self.average_snr
        ) / self.observations

        self.average_bandwidth += (
            measurement.bandwidth - self.average_bandwidth
        ) / self.observations

        self.average_noise_floor += (
            measurement.noise_floor - self.average_noise_floor
        ) / self.observations

        self.peak_snr = max(
            self.peak_snr,
            measurement.peak_snr
        )

        self.peak_bandwidth = max(
            self.peak_bandwidth,
            measurement.bandwidth
        )


class SignalDatabase:

    def __init__(self, frequency_tolerance=1000):

        self.frequency_tolerance = frequency_tolerance

        self.signals = {}

    def _key(self, frequency):

        return round(
            frequency /
            self.frequency_tolerance
        )

    def update(self, signal):

        measurement = signal.measurement

        key = self._key(
            measurement.center_frequency
        )

        history = self.signals.get(key)

        if history is None:

            history = SignalHistory(
                center_frequency=measurement.center_frequency
            )

            self.signals[key] = history

        history.update(signal)

    def __len__(self):

        return len(self.signals)

    def strongest(self, n=20):

        return sorted(
            self.signals.values(),
            key=lambda s: s.peak_snr,
            reverse=True
        )[:n]

    def busiest(self, n=20):

        return sorted(
            self.signals.values(),
            key=lambda s: s.observations,
            reverse=True
        )[:n]
