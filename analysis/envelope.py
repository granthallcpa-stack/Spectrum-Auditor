"""
Signal Envelope Extraction

Produces a simplified envelope from a PeakProfile.

The envelope is represented as distance from the peak
rather than separate left/right arrays.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class Envelope:

    peak: object

    offsets: np.ndarray

    power_db: np.ndarray

    block_size: int


class EnvelopeExtractor:

    def __init__(

        self,

        block_size: int = 16

    ):

        self.block_size = block_size

    def extract(

        self,

        profile

    ):

        peak = profile.peak_local_bin

        power = profile.power_db

        offsets = []

        envelope = []

        for start in range(

            0,

            len(power),

            self.block_size

        ):

            stop = min(

                start + self.block_size,

                len(power)

            )

            block = power[start:stop]

            if len(block) == 0:

                continue

            center = (

                start +

                stop - 1

            ) / 2.0

            offsets.append(

                center - peak

            )

            envelope.append(

                float(

                    np.percentile(

                        block,

                        90

                    )

                )

            )

        return Envelope(

            peak=profile.peak,

            offsets=np.asarray(offsets),

            power_db=np.asarray(envelope),

            block_size=self.block_size

        )
