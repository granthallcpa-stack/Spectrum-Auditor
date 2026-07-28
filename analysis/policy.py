"""
Detection Policy

Produces the operating policy for one observation.

A policy is not configuration—it is a calibrated description
of the RF environment that downstream components use for
signal acceptance.
"""

from dataclasses import dataclass

import numpy as np

from analysis.background_estimator import (
    BackgroundEstimator,
    BackgroundInput
)

@dataclass(slots=True)
class DetectionPolicy:

    noise_floor_db: float

    noise_sigma_db: float

    detection_threshold_db: float

    background_bins: int

    excluded_bins: int

    minimum_snr_db: float


class PolicyCalibrator:

    def __init__(self):

        self.estimator = BackgroundEstimator()

    def calibrate(

        self,

        observation,

        regions,

        peaks

    ):

        mask = np.ones(

            len(

                observation.power_db

            ),

            dtype=bool

        )

        for region in regions:

            mask[

                region.start_bin:

                region.stop_bin + 1

            ] = False

        background_bins = int(

            np.count_nonzero(

                mask

            )

        )

        excluded_bins = (

            len(

                mask

            )

            -

            background_bins

        )

        background_power = (

            observation.power_db[

                mask

            ]

        )

        background = self.estimator.estimate(

            BackgroundInput(

                power_db=

                    background_power

            )

        )

        #
        # Compute SNR for every detected peak.
        #

        snr_values = [

            peak.power_db -

            background.median_db

            for peak

            in peaks

        ]

        if snr_values:

            minimum_snr = min(

                snr_values

            )

        else:

            minimum_snr = 0.0

        return DetectionPolicy(

            noise_floor_db=

                background.median_db,

            noise_sigma_db=

                background.standard_deviation_db,

            detection_threshold_db=

                background.threshold_db,

            background_bins=

                background_bins,

            excluded_bins=

                excluded_bins,

            minimum_snr_db=

                minimum_snr

        )
