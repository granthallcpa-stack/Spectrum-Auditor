from pathlib import Path
import csv

from core.capture import SDRCapture
from analysis.spectrum import SpectrumAnalyzer
from planner import CoveragePlanner

from config import SDR
from config import SCANNER

OUTPUT = Path("calibration")

OUTPUT.mkdir(

    exist_ok=True

)

filename = OUTPUT / "calibration_peaks.csv"

csvfile = open(

    filename,

    "w",

    newline="",

    encoding="utf-8"

)

writer = csv.writer(

    csvfile

)

writer.writerow(

    [

        "window",

        "timestamp",

        "center_frequency",

        "start_frequency",

        "stop_frequency",

        "bandwidth",

        "peak_db",

        "noise_floor",

        "snr",

        "confidence"

    ]

)

receiver = SDRCapture()

planner = CoveragePlanner()

analyzer = SpectrumAnalyzer()

window = 0

for center_frequency in planner:

    capture = receiver.capture(

        center_frequency

    )

    spectrum = analyzer.process(

        capture

    )

    window += 1

for peak in spectrum.peaks:

    writer.writerow(

        [

            window,

            capture.timestamp.isoformat(),

            peak.center_frequency,

            peak.start_frequency,

            peak.stop_frequency,

            peak.bandwidth,

            peak.peak_db,

            spectrum.noise_floor,

            peak.snr,

            peak.confidence

        ]

    )
