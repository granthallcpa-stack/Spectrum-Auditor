"""
Signal Boundary Estimator

Determines where a signal returns to the local background
using the canonical PeakProfile.
"""

from dataclasses import dataclass

from core.debug import debug

@dataclass(slots=True)
class SignalBoundary:

    peak: object

    left_distance: int
    right_distance: int

    left_bin: int
    right_bin: int

    left_frequency: float
    right_frequency: float

    bandwidth: float


class SignalBoundaryEstimator:

    def __init__(
        self,
        boundary_drop_db: float = 18.0
    ):
        self.boundary_drop_db = boundary_drop_db

    def estimate(
        self,
        observation,
        profile
    ):

        assert (
            0 <= profile.peak_local_bin < len(profile.smoothed_db)
        ), "Peak lies outside PeakProfile."

        peak = profile.peak

        smoothed = profile.smoothed_db

        peak_local = profile.peak_local_bin

        threshold = (
            smoothed[peak_local]
            - self.boundary_drop_db
        )

        #
        # Expand left
        #

        left = peak_local
        left_steps = 0

        while (
            left > 0
            and
            smoothed[left] > threshold
        ):
            left -= 1
            left_steps += 1

        #
        # Expand right
        #

        right = peak_local
        right_steps = 0

        while (
            right < len(smoothed) - 1
            and
            smoothed[right] > threshold
        ):
            right += 1
            right_steps += 1

         #
        # Convert profile-relative bins back to FFT bins.
        #

        left_bin = profile.start_bin + left
        right_bin = profile.start_bin + right

        left_frequency = float(
            observation.frequencies[left_bin]
        )

        right_frequency = float(
            observation.frequencies[right_bin]
        )

        bandwidth = (
            right_frequency -
            left_frequency
        )

        if debug("debug_signal_boundaries"):

            print(
                f"Expanded:"
                f" Left={left_steps}"
                f" Right={right_steps}"
            )

            print(
                f"Boundary:"
                f" Peak={peak.frequency/1e6:.6f} MHz"
                f" Left={left_frequency/1e6:.6f}"
                f" Right={right_frequency/1e6:.6f}"
                f" BW={bandwidth:8.1f} Hz"
                f" Threshold={threshold:.1f} dB"
            )

        return SignalBoundary(

            peak=peak,

            left_distance=(
                peak.bin_index -
                left_bin
            ),

            right_distance=(
                right_bin -
                peak.bin_index
            ),

            left_bin=left_bin,
            right_bin=right_bin,

            left_frequency=left_frequency,
            right_frequency=right_frequency,

            bandwidth=bandwidth
        )