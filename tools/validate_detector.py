"""
Detector Validation Tool

Runs the complete detector pipeline and exports
one CSV row per detected RF signal.
"""

from pathlib import Path
import csv

import numpy as np

from core.planner import CoveragePlanner
from core.capture import SDRCapture
from core.observation import ObservationProcessor

from analysis.candidate_seeds import CandidateSeedFinder
from analysis.peak_finder import PeakFinder
from analysis.peak_profile import PeakProfiler
from analysis.profile_means import ProfileMeans
from analysis.signal_boundaries import SignalBoundaryEstimator
from analysis.signal_profile import SignalProfileExtractor
from analysis.region_merger import RegionMerger


class DetectorValidator:

    def __init__(self):

        self.receiver = SDRCapture()

        self.processor = ObservationProcessor()

        self.seed_finder = CandidateSeedFinder()

        self.peak_finder = PeakFinder()

        self.profiler = SignalProfileExtractor()

        self.merger = RegionMerger()

        self.boundaries = SignalBoundaryEstimator()


    def _write_header(

        self,

        writer

    ):

        writer.writerow(

            [

                "window",

                "timestamp",

                "window_center",

                "peak_frequency",

                "peak_power",

                "left_frequency",

                "right_frequency",

                "bandwidth",

                "left_distance",

                "right_distance",

                "background_median",

                "background_sigma",

                "seed_count",

                "peak_count"

            ]

        )

    def run(self):

        output_dir = Path(

            "data/calibration"

        )

        output_dir.mkdir(

            parents=True,

            exist_ok=True

        )

        output_file = (

            output_dir /

            "detector_validation.csv"

        )

        planner = CoveragePlanner()

        with open(

            output_file,

            "w",

            newline=""

        ) as f:

            writer = csv.writer(f)

            self._write_header(

                writer

            )

            for window in planner:

                print(

                    f"Window {window.index}/{window.total}"

                )

                observations = []

                for _ in range(

                    SDR.captures_per_window

                ):

                    capture = self.receiver.capture(

                        window.center_frequency

                    )

                    observations.append(

                        self.processor.process(

                            capture

                        )

                    )


                seeds = self.seed_finder.find(

                    observation

                )

                regions = self.merger.merge(

                    seeds

                )

                peaks = self.peak_finder.find(

                    observation,

                    regions

                )

                for peak in peaks:

                    region = next(

                        (

                            region

                            for region in regions

                            if (

                                region.start_bin <=

                                peak.bin_index <=

                                region.stop_bin

                            )

                        ),

                        None

                    )

                    if region is None:

                        continue

                    profile = self.profiler.extract(

                        observation,

                        region

                    )

                    boundary = self.boundaries.estimate(

                        observation,

                        profile,

                        peak

                    )

                    writer.writerow(

                        [

                            window.index,

                            capture.timestamp.isoformat(),

                            capture.center_frequency,

                            peak.frequency,

                            peak.power_db,

                            boundary.left_frequency,

                            boundary.right_frequency,

                            boundary.bandwidth,

                            boundary.left_distance,

                            boundary.right_distance,

                            observation.background.median_db,

                            observation.background.standard_deviation_db,

                            len(seeds),

                            len(peaks)

                        ]

                    )

        print()

        print(

            f"Saved validation results to {output_file}"

        )

if __name__ == "__main__":

    DetectorValidator().run()
