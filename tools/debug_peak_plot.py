"""
Peak Spectrum Debugger

Plots the processed spectrum around a known frequency.
"""

import matplotlib.pyplot as plt

from core.capture import SDRCapture
from core.observation import ObservationProcessor


receiver = SDRCapture()

processor = ObservationProcessor()


capture = receiver.capture(

    104.7e6

)

observation = processor.process(

    capture

)

center_frequency = 104.7e6

window_khz = 250

x = []

y = []

for frequency, power in zip(

    observation.frequencies,

    observation.power_db

):

    offset = (

        frequency -

        center_frequency

    ) / 1000

    if abs(

        offset

    ) <= window_khz:

        x.append(

            offset

        )

        y.append(

            power

        )

plt.figure(

    figsize=(12,6)

)

plt.plot(

    x,

    y,

    linewidth=1

)

plt.axvline(

    0,

    color="red",

    linestyle="--",

    linewidth=2,

    label="104.7 MHz"

)

plt.title(

    "Spectrum Around 104.7 MHz"

)

plt.xlabel(

    "Frequency Offset (kHz)"

)

plt.ylabel(

    "Power (dB)"

)

plt.grid(

    True

)

plt.legend()

plt.show()
