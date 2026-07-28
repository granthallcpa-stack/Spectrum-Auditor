"""
RF Detector
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Detection:

    frequency: float

    message: str


class RFDetector:

    def detect(self, database, signals):

        detections = []

        for signal in signals:

            measurement = signal.measurement

            detections.append(

                Detection(

                    frequency=measurement.center_frequency,

                    message="Signal Observed"

                )

            )

        return detections
