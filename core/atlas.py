"""
RF Spectrum Atlas

Maintains a continuously improving statistical map of the RF spectrum.

Each AtlasCell represents one 500 Hz frequency cell.
"""

from dataclasses import dataclass
from datetime import datetime

import numpy as np


# ==========================================================
# Configuration
# ==========================================================

GRID_SIZE = 500.0      # Hz


# ==========================================================
# Atlas Cell
# ==========================================================

@dataclass(slots=True)
class AtlasCell:

    frequency: float

    observation_count: int = 0

    # Confidence-weighted statistics
    weighted_power_sum: float = 0.0
    confidence_sum: float = 0.0
    average_power: float = 0.0

    # Running statistics (Welford)
    mean: float = 0.0
    m2: float = 0.0
    variance: float = 0.0
    standard_deviation: float = 0.0

    # Extremes
    peak_power: float = -np.inf
    minimum_power: float = np.inf
    peak_confidence: float = 0.0

    last_seen: datetime | None = None

    # ------------------------------------------------------

    def update(
        self,
        power: float,
        confidence: float,
        timestamp: datetime
    ):

        self.observation_count += 1

        # --------------------------------------
        # Confidence-weighted average
        # --------------------------------------

        self.weighted_power_sum += power * confidence
        self.confidence_sum += confidence

        if self.confidence_sum > 0:

            self.average_power = (
                self.weighted_power_sum /
                self.confidence_sum
            )

        # --------------------------------------
        # Welford Online Variance
        # --------------------------------------

        delta = power - self.mean

        self.mean += (
            delta /
            self.observation_count
        )

        delta2 = power - self.mean

        self.m2 += delta * delta2

        if self.observation_count > 1:

            self.variance = (
                self.m2 /
                (self.observation_count - 1)
            )

            self.standard_deviation = np.sqrt(
                self.variance
            )

        # --------------------------------------
        # Peak Tracking
        # --------------------------------------

        score = power * confidence

        if self.observation_count == 1:

            self.peak_power = power
            self.peak_confidence = confidence

        else:

            current_score = (
                self.peak_power *
                self.peak_confidence
            )

            if score > current_score:

                self.peak_power = power
                self.peak_confidence = confidence

        self.minimum_power = min(
            self.minimum_power,
            power
        )

        self.last_seen = timestamp


# ==========================================================
# Spectrum Atlas
# ==========================================================

class SpectrumAtlas:

    def __init__(self):

        self.cells = {}

    # ------------------------------------------------------

    def _cell_frequency(
        self,
        frequency: float
    ):

        return (
            round(frequency / GRID_SIZE)
            * GRID_SIZE
        )

    # ------------------------------------------------------

    def update(self, spectrum):

        timestamp = spectrum.capture.timestamp

        for freq, power, confidence in zip(
            spectrum.frequencies,
            spectrum.snr_db,
            spectrum.confidence
        ):

            key = self._cell_frequency(freq)

            cell = self.cells.get(key)

            if cell is None:

                cell = AtlasCell(
                    frequency=key
                )

                self.cells[key] = cell

            cell.update(
                power=float(power),
                confidence=float(confidence),
                timestamp=timestamp
            )

    # ------------------------------------------------------

    def __len__(self):

        return len(self.cells)

    # ------------------------------------------------------

    def cell(self, frequency):

        key = self._cell_frequency(frequency)

        return self.cells.get(key)

    # ------------------------------------------------------

    def frequencies(self):

        return np.array(
            sorted(self.cells.keys())
        )

    # ------------------------------------------------------

    def average_power(self):

        frequencies = []
        powers = []

        for frequency in sorted(self.cells):

            frequencies.append(frequency)

            powers.append(
                self.cells[frequency].average_power
            )

        return (
            np.array(frequencies),
            np.array(powers)
        )

    # ------------------------------------------------------

    def strongest(self, n=10):

        return sorted(

            self.cells.values(),

            key=lambda c: (
                c.peak_power *
                c.peak_confidence
            ),

            reverse=True

        )[:n]

    # ------------------------------------------------------

    def quietest(self, n=10):

        return sorted(

            self.cells.values(),

            key=lambda c: c.average_power

        )[:n]

    # ------------------------------------------------------

    def most_variable(self, n=10):

        return sorted(

            self.cells.values(),

            key=lambda c: c.standard_deviation,

            reverse=True

        )[:n]
