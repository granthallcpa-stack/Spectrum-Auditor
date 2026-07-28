"""
Signal Builder

Constructs a fully analyzed Signal from a detected Peak.
"""

from analysis.envelope import EnvelopeExtractor
from analysis.peak_profile import PeakProfiler
from analysis.profile_means import ProfileMeans
from analysis.signal import Signal
from analysis.signal_boundaries import SignalBoundaryEstimator


class SignalBuilder:

    def __init__(
        self,
        profiler: PeakProfiler | None = None,
        boundary_estimator: SignalBoundaryEstimator | None = None,
        envelope_extractor: EnvelopeExtractor | None = None,
        profile_means: ProfileMeans | None = None,
    ):

        self.profiler = profiler or PeakProfiler()

        self.boundary_estimator = (
            boundary_estimator
            or SignalBoundaryEstimator()
        )

        self.envelope_extractor = (
            envelope_extractor
            or EnvelopeExtractor()
        )

        self.profile_means = (
            profile_means
            or ProfileMeans()
        )

    def build(
        self,
        observation,
        peak,
    ) -> Signal:

        profile = self.profiler.measure(
            observation,
            peak,
        )

        boundary = self.boundary_estimator.estimate(
            observation,
            profile,
        )

        envelope = self.envelope_extractor.extract(
            profile,
        )

        smoothed = self.profile_means.measure(
            profile,
        )

        return Signal(
            peak=peak,
            profile=profile,
            boundary=boundary,
            envelope=envelope,
            smoothed_profile=smoothed,
        )
