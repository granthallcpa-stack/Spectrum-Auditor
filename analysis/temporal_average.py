"""
Temporal Spectrum Averager

Averages multiple power spectra collected
from the same frequency window.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class TemporalSpectrum:

    power_db: np.ndarray


class TemporalAverager:

    def average(

        self,

        observations

    ):

        stacked = np.stack(

            [

                observation.power_db

                for observation

                in observations

            ]

        )

        average_power = np.mean(

            stacked,

            axis=0

        )

        return TemporalSpectrum(

            power_db=average_power

        )
