"""
RF Observatory

Main application.
"""

import time
import sys
from datetime import datetime

from analysis.signal_builder import SignalBuilder
from config import SDR
from config import SCANNER

from core.planner import CoveragePlanner
from core.planner import ScanWindow
from core.capture import SDRCapture
from core.observation import ObservationProcessor
from core.atlas import SpectrumAtlas
from core.debug import debug

from analysis.rf_classifier import RFClassifier
from analysis.band_identifier import BandIdentifier
from analysis.detector import RFDetector
from analysis.occupancy import OccupancyAnalyzer

from storage.timeline import Timeline
from storage.database import RFDatabase

from knowledge.services import get_tolerance

from reports.report_generator import ReportGenerator

from datetime import datetime, UTC

from analysis.intelligence_engine import IntelligenceEngine
from analysis.candidate_seeds import CandidateSeedFinder
from analysis.region_merger import RegionMerger
from analysis.peak_finder import PeakFinder
from analysis.policy import PolicyCalibrator
from analysis.signal_merger import merge_signals

from storage.csv_export import export_signal_catalog

log = open(
    f"logs/audit_{datetime.now():%Y%m%d_%H%M%S}.txt",
    "w",
    buffering=1
)

class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)

    def flush(self):
        for s in self.streams:
            s.flush()

sys.stdout = Tee(sys.stdout, log)

class SpectrumAudit:

    def __init__(self):

        # Core pipeline

        self.planner = CoveragePlanner("FULL_SCAN")

        self.receiver = SDRCapture()

        self.processor = ObservationProcessor()

        self.seed_finder = CandidateSeedFinder()

        self.region_merger = RegionMerger()

        self.peak_finder = PeakFinder()

        self.signal_builder = SignalBuilder()

        self.calibrator = PolicyCalibrator()

        self.classifier = RFClassifier()

        self.identifier = BandIdentifier()

        self.atlas = SpectrumAtlas()

        self.timeline = Timeline()

        self.intelligence = IntelligenceEngine()

        self.database = RFDatabase()

        self.detector = RFDetector()

        self.occupancy = OccupancyAnalyzer()

        self.reporter = ReportGenerator()

        # Survey state

        self.total_windows = 0

        self.total_signals = 0

        self.all_identified_signals = []

        self.events = []

        self.known_signals = 0

    # -----------------------------------------------------

    def run(self):

        start_time = time.perf_counter()

        self.survey_id = self.database.start_survey(
            started=datetime.now(UTC),
            receiver="RTL-SDR",
            sample_rate=self.receiver.sdr.sample_rate,
            gain=self.receiver.sdr.gain,
            overlap=SDR.overlap,
            dwell=SDR.dwell_time
        )

        if SDR.debug_fixed_frequency:

            windows = [

                ScanWindow(

                    index=i + 1,
                    total=SDR.debug_windows,

                    center_frequency=SDR.debug_center_frequency,

                    capture_start=(
                        SDR.debug_center_frequency
                        - SDR.sample_rate / 2
                    ),

                    capture_stop=(
                        SDR.debug_center_frequency
                        + SDR.sample_rate / 2
                    ),

                    usable_start=(
                        SDR.debug_center_frequency
                        - (SDR.sample_rate * SCANNER.usable_bandwidth_fraction) / 2
                    ),

                    usable_stop=(
                        SDR.debug_center_frequency
                        + (SDR.sample_rate * SCANNER.usable_bandwidth_fraction) / 2
                    ),

                    capture_bandwidth=SDR.sample_rate,

                    usable_bandwidth=(
                        SDR.sample_rate
                        * SCANNER.usable_bandwidth_fraction
                    )

                )

                for i in range(SDR.debug_windows)

            ]

        else:

            windows = list(self.planner)

        self.total_windows = len(windows)

        print("\n" + "=" * 70)
        print("RF OBSERVATORY")
        print("=" * 70)
        print(f"Windows to Scan : {self.total_windows:,}\n")

        if SDR.debug_fixed_frequency:

            print(
                f"DEBUG MODE: "
                f"{SDR.debug_center_frequency/1e6:.6f} MHz "
                f"({SDR.debug_windows} captures)\n"
            )

        try:

            for window in windows:

                capture = self.receiver.capture(
                    window.center_frequency
                )

                observation = self.processor.process(
                    capture
                )

                self.atlas.update(
                    observation
                )

                seeds = self.seed_finder.find(

                    observation

                )

                regions = self.region_merger.merge(

                    seeds

                )

                peaks = self.peak_finder.find(

                    observation,

                    regions

                )

                signals = []

                for peak in peaks:

                    signals.append(

                        self.signal_builder.build(
                            observation,
                            peak,
                        )

                    )

                policy = self.calibrator.calibrate(

                    observation,

                    regions,

                    peaks

                )

                signals = self.classifier.classify(

                    observation,

                    signals,

                    policy

                )

                window_id = self.database.store_window(

                    survey_id=self.survey_id,

                    observation=observation,

                    policy=policy,

                    signals=signals

                )

                self.total_signals += len(signals)

                signals = merge_signals(

                    signals,

                    SDR.merge_distance_hz

                )


                identified = self.identifier.identify_many(
                    signals
                )

                self.all_identified_signals.extend(
                    identified
                )

                self.timeline.add_scan(
                    signals,
                    capture.timestamp
                )

                printed_known = set()

                for signal, identified_signal in zip(
                    signals,
                    identified
                ):

                    intelligence = self.intelligence.identify(signal)

                    emitter_id = self.database.store_signal(

                        signal

                    )

                    measurement = signal.measurement

                    if intelligence:

                        self.known_signals += 1

                        self.database.store_known_signal(

                            emitter_id,

                            intelligence,

                            measurement.timestamp

                        )
        
                        difference_hz = abs(
                            measurement.center_frequency / 1e6
                            - intelligence.frequency
                        ) * 1_000_000

                        tolerance_hz = get_tolerance(intelligence.service)

                        print(
                            f"[KNOWN] "
                            f"Emitter {emitter_id} | "
                            f"{measurement.center_frequency/1e6:.6f} MHz -> "
                            f"{intelligence.frequency:.6f} MHz | "
                            f"{intelligence.system} | "
                            f"Δ={difference_hz:.0f} Hz | "
                            f"Tolerance=±{tolerance_hz} Hz"
                        )

                    self.database.store_observation(
                        survey_id=self.survey_id,
                        window_id=window_id,
                        emitter_id=emitter_id,
                        signal=signal
                    )

                    self.database.store_allocations(
                        emitter_id,
                        identified_signal
                    )

                    self.database.store_fingerprint(
                        emitter_id,
                        signal
                    )

                self.events.extend(
                    self.detector.detect(
                        self.database,
                        signals
                    )
                )

                progress = (
                    100.0 *
                    window.index /
                    window.total
                )

                print(
                    f"\r"
                    f"{window.index:4d}/{window.total:<4d} "
                    f"{progress:6.2f}%  "
                    f"{window.center_frequency/1e6:9.3f} MHz  "
                    f"Signals: {self.total_signals:6d}",
                    end=""
                )

        finally:

            self.receiver.close()

        elapsed = time.perf_counter() - start_time

        self.database.finish_survey(
            survey_id=self.survey_id,
            finished=datetime.now(UTC),
            duration=elapsed,
            windows=self.total_windows,
            signals=self.total_signals
        )

        self.timeline.save()

        self.database.export_signal_catalog(

            self.survey_id,

            f"data/signal_catalog_{self.survey_id:04d}.csv"

        )

        report = self.reporter.generate(
            database=self.database,
            survey_id=self.survey_id,
            elapsed=elapsed
        )

        print()

        self.summary(elapsed)

        print(f"\nHTML Report : {report}")

        return report

    # -----------------------------------------------------

    def summary(self, elapsed):

        print("=" * 70)
        print("SURVEY COMPLETE")
        print("=" * 70)

        print(f"Duration         : {elapsed:.1f} sec")
        print(f"Windows          : {self.total_windows:,}")
        print(f"Signals          : {self.total_signals:,}")
        print(f"Known Signals    : {self.known_signals:,}")

        stats = self.database.database_summary()

        print(f"Known Emitters   : {stats['emitters']:,}")
        print(f"Observations     : {stats['observations']:,}")
        print(f"Allocation Records : {stats['allocations']:,}")
        print(f"Fingerprints     : {stats['fingerprints']:,}")
        print(f"Events           : {len(self.events):,}")

        print(f"Known Systems    : {self.known_signals:,}")

        print("=" * 70)

        print("\nTop Emitters")

        for emitter in self.database.top_emitters(20):

            print(
                f"{emitter['center_frequency']/1e6:10.6f} MHz"
                f"  Obs={emitter['observations']:4d}"
                f"  BW={emitter['average_bandwidth']:8.0f} Hz"
            )

        print()

        print("Strongest Emitters")

        for emitter in self.database.strongest_emitters(20):

            print(
                f"Emitter {emitter['signal_id']:4d}"
                f"  Peak={emitter['peak_snr']:6.2f} dB"
            )


def main():

    audit = SpectrumAudit()

    audit.run()


if __name__ == "__main__":

    main()
