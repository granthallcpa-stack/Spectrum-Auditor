"""
Peak Profile

Measures how signal power decays away from the peak.

This module performs NO bandwidth estimation.
"""

from dataclasses import dataclass

import numpy as np

from scipy.ndimage import gaussian_filter1d

from analysis.peak_finder import Peak


@dataclass(slots=True)
class PeakProfile:

    peak: Peak

    start_bin: int
    stop_bin: int

    peak_local_bin: int

    bins: np.ndarray
    frequencies: np.ndarray

    power_db: np.ndarray
    smoothed_db: np.ndarray


class PeakProfiler:

    def __init__(

        self,

        max_distance: int = 1024,

        smoothing_sigma: float = 4.0

    ):

        self.max_distance = max_distance
        self.smoothing_sigma = smoothing_sigma

    def measure(

        self,

        spectrum,

        peak

    ):

        start_bin = max(

            peak.left_limit,

            peak.bin_index - self.max_distance

        )

        stop_bin = min(

            peak.right_limit,

            peak.bin_index + self.max_distance

        )

        bins = np.arange(

            start_bin,

            stop_bin + 1

        )

        window = slice(

            start_bin,

            stop_bin + 1

        )

        frequencies = spectrum.frequencies[window]

        power_db = spectrum.power_db[window]

        smoothed_db = gaussian_filter1d(

            power_db,

            sigma=self.smoothing_sigma

        )

        return PeakProfile(

            peak=peak,

            start_bin=start_bin,

            stop_bin=stop_bin,

            peak_local_bin=(

                peak.bin_index -

                start_bin

            ),

            bins=bins,

            frequencies=frequencies,

            power_db=power_db,

            smoothed_db=smoothed_db

        )