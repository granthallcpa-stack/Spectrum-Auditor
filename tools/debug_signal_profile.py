"""
Signal Profile Debugger

Displays the raw and smoothed power profile
for the first detected signal region.
"""

import matplotlib.pyplot as plt

import pandas as pd

from core.capture import SDRCapture
from core.observation import ObservationProcessor

from analysis.candidate_seeds import CandidateSeedFinder
from analysis.region_merger import RegionMerger
from analysis.signal_profile import SignalProfileExtractor


receiver = SDRCapture()

processor = ObservationProcessor()

finder = CandidateSeedFinder()

merger = RegionMerger()

extractor = SignalProfileExtractor()


capture = receiver.capture(

    104.7e6

)

observation = processor.process(

    capture

)

regions = merger.merge(

    finder.find(

        observation

    )

)

if not regions:

    raise RuntimeError(

        "No candidate regions found."

    )

region = regions[0]

profile = extractor.extract(

    observation,

    region

)


center = (

    region.start_bin +

    region.stop_bin

) / 2


x = (

    profile.bins -

    center

) * observation.bin_width / 1000


plt.figure(

    figsize=(12,6)

)

plt.plot(

    x,

    profile.power_db,

    linewidth=1,

    label="Raw"

)

plt.plot(

    x,

    profile.smoothed_db,

    linewidth=2,

    label="Smoothed"

)

plt.title(

    "Signal Profile"

)

plt.xlabel(

    "Offset (kHz)"

)

plt.ylabel(

    "Power (dB)"

)

plt.grid(

    True

)

plt.legend()

plt.show()
