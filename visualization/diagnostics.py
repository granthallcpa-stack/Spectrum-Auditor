"""
Spectrum Diagnostics

Visual inspection tools for SpectrumSlice objects.
"""

import matplotlib.pyplot as plt
import numpy as np


class SpectrumDiagnostics:

    def plot(self, spectrum):

        freq = spectrum.frequencies / 1e6

        plt.figure(figsize=(15, 10))

        # -------------------------------
        # Raw FFT
        # -------------------------------

        plt.subplot(311)

        plt.plot(
            freq,
            spectrum.power_db,
            linewidth=0.8
        )

        plt.title("Raw Power Spectrum")

        plt.ylabel("dB")

        plt.grid(True)

        # -------------------------------
        # Signal Above Noise
        # -------------------------------

        plt.subplot(312)

        plt.plot(
            freq,
            spectrum.snr_db,
            linewidth=0.8
        )

        plt.axhline(
            0,
            linestyle="--"
        )

        plt.title("Power Above Noise Floor")

        plt.ylabel("dB")

        plt.grid(True)

        # -------------------------------
        # Confidence
        # -------------------------------

        plt.subplot(313)

        plt.plot(
            freq,
            spectrum.confidence,
            linewidth=2
        )

        plt.title("Confidence Weight")

        plt.xlabel("Frequency (MHz)")

        plt.ylabel("Weight")

        plt.grid(True)

        plt.tight_layout()

        plt.show()
