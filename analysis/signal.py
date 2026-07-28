from dataclasses import dataclass

from analysis.envelope import Envelope
from analysis.peak_finder import Peak
from analysis.peak_profile import PeakProfile
from analysis.profile_means import SmoothedProfile
from analysis.signal_boundaries import SignalBoundary
from analysis.rf_measurement import RFMeasurement


@dataclass(slots=True)
class Signal:

    peak: Peak

    profile: PeakProfile | None = None

    boundary: SignalBoundary | None = None

    envelope: Envelope | None = None

    smoothed_profile: SmoothedProfile | None = None

    measurement: RFMeasurement | None = None