"""
RF Signal Extractor

Extracts individual RF signals from a processed spectrum.

This module performs NO protocol or service identification.
It simply returns measured RF signals.
"""

import numpy as np

from analysis.rf_measurement import RFMeasurement

# ==========================================================
# RF Signal Extractor
# ==========================================================

class RFClassifier:

    def __init__(self):

        pass

    # ------------------------------------------------------

    def classify(

        self,

        observation,

        signals,

        policy

    ):


        for signal in signals:

            peak = signal.peak

            boundary = signal.boundary

            region = slice(

                boundary.left_bin,

                boundary.right_bin + 1

            )

            measurement = RFMeasurement(

                start_frequency=boundary.left_frequency,

                stop_frequency=boundary.right_frequency,

                center_frequency=(

                    boundary.left_frequency +

                    boundary.right_frequency

                ) / 2,

                peak_frequency=peak.frequency,

                bandwidth=boundary.bandwidth,

                peak_snr=(

                    peak.power_db -

                    policy.noise_floor_db

                ),

                noise_floor=policy.noise_floor_db,

                peak_power=peak.power_db,

                occupied_bins=(

                    boundary.right_bin -

                    boundary.left_bin +

                    1

                ),

                confidence=float(

                    np.mean(

                        observation.confidence[region]

                    )

                ),

                timestamp=observation.capture.timestamp

            )

            signal.measurement = measurement

        return signals