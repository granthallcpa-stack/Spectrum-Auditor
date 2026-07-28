"""
Background Estimator

Estimates the statistical background of a spectrum.

This module performs NO signal classification.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class BackgroundInput:

    power_db: np.ndarray

@dataclass(slots=True)
class BackgroundModel:

    median_db: float

    standard_deviation_db: float

    threshold_db: float

    background_mask: np.ndarray


class BackgroundEstimator:

    def __init__(self, sigma_multiplier: float = 3.0):

        self.sigma_multiplier = sigma_multiplier

    def estimate(self, spectrum):

        power = np.asarray(

            spectrum.power_db

        )

        power = power[

            np.isfinite(

                power

            )

        ]

        power = power[np.isfinite(power)]

        median = float(

            np.median(power)

        )

        mad = float(

            np.median(

                np.abs(

                    power - median

                )

            )

        )

        sigma = (

            1.4826 *

            mad

        )

        threshold = (

            median +

            (self.sigma_multiplier * sigma)

        )

        background_mask = (

            power < threshold

        )

        return BackgroundModel(

            median_db=median,

            standard_deviation_db=sigma,

            threshold_db=threshold,

            background_mask=background_mask

        )
