"""
Frequency Scan Planner

This module does NOT communicate with the SDR.

Its only responsibility is deciding which center
frequencies should be visited.
"""

from dataclasses import dataclass

from config import SDR
from config import SCANNER
from config import SCAN_PROFILES


@dataclass
class ScanStep:

    center_frequency: float

    lower_frequency: float

    upper_frequency: float

    index: int

    total_steps: int


class FrequencyScanner:

    def __init__(self, profile_name="FULL_SCAN"):

        if profile_name not in SCAN_PROFILES:
            raise ValueError(f"Unknown profile: {profile_name}")

        profile = SCAN_PROFILES[profile_name]

        self.profile = profile

        usable_bandwidth = (
            SDR.sample_rate *
            SCANNER.usable_bandwidth_fraction
        )

        self.step_size = (
            usable_bandwidth *
            (1.0 - SCANNER.overlap_fraction)
        )

        self.centers = []

        center = (
            profile.start_freq +
            usable_bandwidth / 2
        )

        while center <= (
            profile.stop_freq -
            usable_bandwidth / 2
        ):

            self.centers.append(center)

            center += self.step_size

    def __len__(self):

        return len(self.centers)

    def __iter__(self):

        total = len(self.centers)

        for index, center in enumerate(self.centers):

            yield ScanStep(

                center_frequency=center,

                lower_frequency=center -
                SDR.sample_rate / 2,

                upper_frequency=center +
                SDR.sample_rate / 2,

                index=index + 1,

                total_steps=total
            )

    def summary(self):

        print()

        print("Scan Profile")

        print("----------------------")

        print("Profile:", self.profile.name)

        print(
            "Range:",
            f"{self.profile.start_freq/1e6:.3f}",
            "to",
            f"{self.profile.stop_freq/1e6:.3f} MHz"
        )

        print(
            "Sample Rate:",
            SDR.sample_rate / 1e6,
            "MHz"
        )

        print(
            "Step Size:",
            self.step_size / 1e6,
            "MHz"
        )

        print(
            "Centers:",
            len(self.centers)
        )

        print()
