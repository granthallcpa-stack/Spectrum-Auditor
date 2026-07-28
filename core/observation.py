"""
Spectrum Observation Engine

Transforms IQ samples into a calibrated spectrum observation.

Pipeline:

IQ Samples
    ↓
Window Function
    ↓
FFT
    ↓
Magnitude
    ↓
Power
    ↓
Normalized Power
    ↓
SpectrumSlice
"""

from dataclasses import dataclass

import numpy as np

from analysis.background_estimator import (
    BackgroundEstimator,
    BackgroundInput
)

from core.capture import Capture

from config import SDR


# ==========================================================
# Spectrum Slice
# ==========================================================

@dataclass(frozen=True, slots=True)
class SpectrumSlice:

    capture: Capture

    frequencies: np.ndarray

    magnitude: np.ndarray

    power_linear: np.ndarray

    power_db: np.ndarray

    relative_db: np.ndarray

    snr_db: np.ndarray

    confidence: np.ndarray

    background: object

    noise_floor: float

    average_power: float

    minimum_power: float

    peak_power: float

    peak_frequency: float

    dynamic_range: float

    bin_width: float

    window: str

    def peak(self):

        return (
            self.peak_frequency,
            self.peak_power
        )

    def power_at(self, frequency):

        index = np.argmin(
            np.abs(
                self.frequencies - frequency
            )
        )

        return self.relative_db[index]

    def nearest_bin(self, frequency):

        return int(
            np.argmin(
                np.abs(
                    self.frequencies - frequency
                )
            )
        )


# ==========================================================
# Processor
# ==========================================================

# ==========================================================
# Processor
# ==========================================================

class ObservationProcessor:

    def __init__(self):

        self.background_estimator = BackgroundEstimator()

        self.fft_size = SDR.fft_size

    def process(

        self,

        capture: Capture

    ):

        iq = capture.iq

        fft_size = self.fft_size

        frames = len(

            iq

        ) // fft_size

        #
        # Keep only complete FFT frames
        #

        iq = iq[

            :frames *

            fft_size

        ]

        iq_frames = iq.reshape(

            frames,

            fft_size

        )

        window = np.hanning(

            fft_size

        )

        power_sum = np.zeros(

            fft_size,

            dtype=float

        )

        #
        # Average multiple FFT power spectra
        #

        for frame in iq_frames:

            windowed = (

                frame *

                window

            )

            spectrum = np.fft.fftshift(

                np.fft.fft(

                    windowed

                )

            )

            magnitude = np.abs(

                spectrum

            )

            power_sum += (

                magnitude ** 2

            )

        power_linear = (

            power_sum /

            frames

        )

        magnitude = np.sqrt(

            power_linear

        )

        power_db = 10 * np.log10(

            power_linear +

            1e-20

        )

        #
        # Statistics
        #

        noise_floor = float(

            np.median(

                power_db

            )

        )

        average_power = float(

            np.mean(

                power_db

            )

        )

        minimum_power = float(

            np.min(

                power_db

            )

        )

        peak_index = int(

            np.argmax(

                power_db

            )

        )

        peak_power = float(

            power_db[

                peak_index

            ]

        )

        dynamic_range = (

            peak_power -

            noise_floor

        )

        relative_db = (

            power_db -

            peak_power

        )

        snr_db = (

            power_db -

            noise_floor

        )

        #
        # Frequency Axis
        #

        frequencies = np.fft.fftshift(

            np.fft.fftfreq(

                fft_size,

                d=1 /

                capture.sample_rate

            )

        )

        frequencies += (

            capture.center_frequency

        )

        peak_frequency = float(

            frequencies[

                peak_index

            ]

        )

        bin_width = (

            capture.sample_rate /

            fft_size

        )

        #
        # Confidence
        #

        x = np.linspace(

            -1,

            1,

            fft_size

        )

        confidence = (

            np.cos(

                x *

                np.pi /

                2

            ) ** 2

        )

        #
        # Background
        #

        background = self.background_estimator.estimate(

            BackgroundInput(

                power_db=power_db

            )

        )

        return SpectrumSlice(

            capture=capture,

            frequencies=frequencies,

            magnitude=magnitude,

            power_linear=power_linear,

            power_db=power_db,

            relative_db=relative_db,

            snr_db=snr_db,

            confidence=confidence,

            background=background,

            noise_floor=noise_floor,

            average_power=average_power,

            minimum_power=minimum_power,

            peak_power=peak_power,

            peak_frequency=peak_frequency,

            dynamic_range=dynamic_range,

            bin_width=bin_width,

            window="Hann"

        )


