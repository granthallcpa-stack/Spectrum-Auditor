"""
RF Coverage Planner

Generates scan windows that provide complete RF coverage.

This module contains NO SDR code.
"""

from dataclasses import dataclass
from math import ceil

from config import SDR
from config import SCANNER
from config import SCAN_PROFILES


@dataclass(slots=True)
class ScanWindow:

    index: int
    total: int

    center_frequency: float

    capture_start: float
    capture_stop: float

    usable_start: float
    usable_stop: float

    capture_bandwidth: float
    usable_bandwidth: float


class CoveragePlanner:

    def __init__(self, profile="FULL_SCAN"):

        if profile not in SCAN_PROFILES:
            raise ValueError(f"Unknown profile: {profile}")

        self.profile = SCAN_PROFILES[profile]

        self.capture_bw = SDR.sample_rate
        self.usable_bw = (
            SDR.sample_rate *
            SCANNER.usable_bandwidth_fraction
        )

        self.span = (
            self.profile.stop_freq -
            self.profile.start_freq
        )

        self.nominal_step = (
            self.usable_bw *
            (1.0 - SCANNER.overlap_fraction)
        )

        if self.span <= self.usable_bw:
            self.total = 1
        else:
            self.total = (
                ceil(
                    (self.span - self.usable_bw)
                    / self.nominal_step
                )
                + 1
            )

        if self.total == 1:
            self.actual_step = 0
        else:
            self.actual_step = (
                self.span - self.usable_bw
            ) / (self.total - 1)

    def __len__(self):
        return self.total

    def __iter__(self):

        usable_half = self.usable_bw / 2
        capture_half = self.capture_bw / 2

        for i in range(self.total):

            center = (
                self.profile.start_freq +
                usable_half +
                (i * self.actual_step)
            )

            yield ScanWindow(

                index=i + 1,

                total=self.total,

                center_frequency=center,

                capture_start=center - capture_half,
                capture_stop=center + capture_half,

                usable_start=center - usable_half,
                usable_stop=center + usable_half,

                capture_bandwidth=self.capture_bw,
                usable_bandwidth=self.usable_bw,
            )

    def summary(self):

        print()
        print("Coverage Planner")
        print("-------------------------")
        print(f"Profile      : {self.profile.name}")
        print(f"Start        : {self.profile.start_freq/1e6:.3f} MHz")
        print(f"Stop         : {self.profile.stop_freq/1e6:.3f} MHz")
        print(f"Capture BW   : {self.capture_bw/1e6:.3f} MHz")
        print(f"Usable BW    : {self.usable_bw/1e6:.3f} MHz")
        print(f"Step         : {self.actual_step/1e6:.3f} MHz")
        print(f"Windows      : {self.total}")
        print()
