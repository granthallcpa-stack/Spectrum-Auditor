"""
Candidate Region Finder

Finds contiguous regions that exceed the estimated
background threshold.

This module performs NO signal classification.
"""

from dataclasses import dataclass

from scipy.ndimage import gaussian_filter1d

import numpy as np

from core.debug import debug

@dataclass(slots=True)
class CandidateSeed:

    start_bin: int

    stop_bin: int


class CandidateSeedFinder:

    def __init__(

        self,

        high_sigma: float = 3.0,

        low_sigma: float = 1.5

    ):

        self.high_sigma = high_sigma

        self.low_sigma = low_sigma


    def find(self, spectrum):

        power = gaussian_filter1d(

            spectrum.power_db,

            sigma=3

        )

        raw_power = spectrum.power_db

        high_threshold = (

            spectrum.background.median_db +

            self.high_sigma *

            spectrum.background.standard_deviation_db

        )

        low_threshold = (

            spectrum.background.median_db +

            self.low_sigma *

            spectrum.background.standard_deviation_db

        )

        regions = []

        visited = np.zeros(

            len(power),

            dtype=bool

        )

        for index in range(

            len(power)

        ):

            if visited[index]:

                continue

            if power[index] < high_threshold:

                continue

            left = index

            while (

                left > 0

                and

                power[left - 1] >= low_threshold

            ):

                left -= 1

            right = index

            while (

                right < len(power) - 1

                and

                power[right + 1] >= low_threshold

            ):

                right += 1

            width = right - left + 1

            segment = power[left:right + 1]

            minimum = np.min(segment)

            minimum_bin = left + np.argmin(segment)

            if debug("debug_candidate_seeds"):

                print(
                    f"Minimum    : {minimum:.2f} dB"
                )

                print(
                    f"Min Bin    : {minimum_bin}"
                )

                if width > 100:

                    print()

                    print("=" * 80)

                    print("Profile:")

                    for i in range(left, right + 1):

                        if i % 10 == 0:

                            print(
                                f"{i:6d}"
                                f" {power[i]:6.2f}"
                            )

                    print("LARGE CANDIDATE")

                    print("=" * 80)

                    print(
                        f"Bins        : {left} -> {right}"
                    )

                    print(
                        f"Width       : {width} bins"
                    )

                    print(
                        f"Peak Bin    : {index}"
                    )

                    print(
                        f"Peak Power  : {power[index]:.2f} dB"
                    )

                    print(
                        f"Raw Peak    : {raw_power[index]:.2f} dB"
                    )

                    print(
                        f"Smooth Gain : {power[index] - raw_power[index]:.2f} dB"
                    )

                    print(
                        f"Left Edge   : {power[left]:.2f} dB"
                    )

                    print(
                        f"Right Edge  : {power[right]:.2f} dB"
                    )

                    print(
                        f"High Thresh : {high_threshold:.2f} dB"
                    )

                    print(
                        f"Low Thresh  : {low_threshold:.2f} dB"
                    )

                    print(
                        f"Median Noise: {spectrum.background.median_db:.2f} dB"
                    )

                    print(
                        f"Noise Std   : {spectrum.background.standard_deviation_db:.2f} dB"
                    )

                    print("=" * 80)

            visited[
                left:right + 1
            ] = True

            regions.append(
                CandidateSeed(
                    start_bin=left,
                    stop_bin=right
                )
            )

        return regions