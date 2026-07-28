"""
RTL-SDR Capture Engine

Responsible only for talking to the hardware.
"""

from dataclasses import dataclass
from datetime import datetime, UTC
import time

import numpy as np
from rtlsdr import RtlSdr

from config import SDR
from config import SCANNER
from config import SDR


@dataclass(slots=True)
class Capture:

    timestamp: datetime

    center_frequency: float

    sample_rate: float

    gain: float | str

    iq: np.ndarray


class SDRCapture:

    def __init__(self):

        self.sdr = RtlSdr()

        self.sdr.sample_rate = SDR.sample_rate
        self.sdr.gain = SDR.gain

    def capture(
        self,
        center_frequency: float
    ) -> Capture:

        self.sdr.center_freq = center_frequency

        time.sleep(
            SCANNER.settle_time
        )

        frames = 32

        iq = self.sdr.read_samples(

        frames *

        SDR.fft_size

        )

        return Capture(

            timestamp=datetime.now(UTC),

            center_frequency=center_frequency,

            sample_rate=self.sdr.sample_rate,

            gain=self.sdr.gain,

            iq=iq
        )

    def close(self):

        self.sdr.close()
