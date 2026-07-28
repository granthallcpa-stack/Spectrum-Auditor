"""
Signal Profile

Extracts a raw and smoothed power profile for one signal region.
"""

from dataclasses import dataclass

import numpy as np

from scipy.ndimage import gaussian_filter1d


@dataclass(slots=True)
class SignalProfile:

    start_bin: int

    stop_bin: int

    bins: np.ndarray

    power_db: np.ndarray

    smoothed_db: np.ndarray


class SignalProfileExtractor:

    def __init__(

        self,

        sigma: float = 4.0

    ):

        self.sigma = sigma

    def extract(

        self,

        spectrum,

        region

    ):

        bins = np.arange(

            region.start_bin,

            region.stop_bin + 1

        )

        power = spectrum.power_db[

            region.start_bin:

            region.stop_bin + 1

        ]

        smooth = gaussian_filter1d(

            power,

            self.sigma

        )

        return SignalProfile(

            start_bin=region.start_bin,

            stop_bin=region.stop_bin,

            bins=bins,

            power_db=power,

            smoothed_db=smooth

        )
