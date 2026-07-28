"""
Profile Smoothing

Computes a moving average across a PeakProfile.

The result is represented as distance from the peak,
not separate left/right arrays.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class SmoothedProfile:

    peak: object

    offsets: np.ndarray

    power_db: np.ndarray


class ProfileMeans:

    def __init__(

        self,

        window_size: int = 9

    ):

        self.window_size = window_size

    def measure(

        self,

        profile

    ):

        power = np.asarray(

            profile.power_db,

            dtype=float

        )

        if len(power) == 0:

            return SmoothedProfile(

                peak=profile.peak,

                offsets=np.asarray([]),

                power_db=np.asarray([])

            )

        kernel = np.ones(

            self.window_size,

            dtype=float

        ) / self.window_size

        smoothed = np.convolve(

            power,

            kernel,

            mode="same"

        )

        offsets = (

            np.arange(

                len(power)

            )

            - profile.peak_local_bin

        )

        return SmoothedProfile(

            peak=profile.peak,

            offsets=offsets,

            power_db=smoothed

        )
