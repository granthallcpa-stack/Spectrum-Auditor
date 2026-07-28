"""
Spectrum Profiler

Profiles the RF environment without performing
signal detection or classification.

Outputs:

    data/calibration/windows.csv
"""

from pathlib import Path
import csv

from core.capture import SDRCapture
from core.observation import ObservationProcessor
from core.planner import CoveragePlanner

from config import SDR


OUTPUT = Path(

    "data/calibration"

)

OUTPUT.mkdir(

    parents=True,

    exist_ok=True

)


class SpectrumProfiler:

    def __init__(self):

        self.receiver = SDRCapture()

        self.processor = ObservationProcessor()

        self.planner = CoveragePlanner()

    def run(self):

        filename = (

            OUTPUT /

            "windows.csv"

        )

        with open(

            filename,

            "w",

            newline="",

            encoding="utf-8"

        ) as csvfile:

            writer = csv.writer(

                csvfile

            )

            writer.writerow(

                [

                    "window",

                    "capture_start",

                    "capture_stop",

                    "usable_start",

                    "usable_stop",

                    "timestamp",

                    "center_frequency",

                    "noise_floor",

                    "average_power",

                    "minimum_power",

                    "peak_power",

                    "peak_frequency",

                    "dynamic_range",

                    "bin_width",

                    "fft_size",

                    "sample_rate",

                    "gain"

                ]

            )

            total = len(

                self.planner

            )

            for window in self.planner:

                capture = self.receiver.capture(

                    window.center_frequency

                )

                observation = self.processor.process(

                    capture

                )

                writer.writerow(

                    [

                        window.index,

                        window.capture_start,

                        window.capture_stop,

                        window.usable_start,

                        window.usable_stop,

                        capture.timestamp.isoformat(),

                        capture.center_frequency,

                        observation.noise_floor,

                        observation.average_power,

                        observation.minimum_power,

                        observation.peak_power,

                        observation.peak_frequency,

                        observation.dynamic_range,

                        observation.bin_width,

                        SDR.fft_size,

                        capture.sample_rate,

                        capture.gain

                    ]

                )

                csvfile.flush()

                print(

                    f"\r"

                    f"{window}/{total}"

                    f" "

                    f"{window.index / total:6.2%}"

                    f" "

                    f"{window.center_frequency / 1e6:9.3f} MHz",

                    end=""

                )

        self.receiver.close()

        print()

        print()

        print(

            "Spectrum profile complete."

        )

        print(

            f"Saved: {filename}"

        )


def main():

    profiler = SpectrumProfiler()

    profiler.run()


if __name__ == "__main__":

    main()
