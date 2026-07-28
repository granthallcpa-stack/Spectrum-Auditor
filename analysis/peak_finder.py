"""
Peak Finder

Finds one or more significant peaks inside each candidate seed.
"""

from dataclasses import dataclass

import numpy as np

from scipy.signal import find_peaks

from core.debug import debug


@dataclass(slots=True)
class Peak:

    bin_index: int

    frequency: float

    power_db: float

    left_limit: int

    right_limit: int


class PeakFinder:

    def __init__(

        self,

        prominence_db: float = 2.0,

        minimum_distance: int = 16

    ):

        self.prominence_db = prominence_db

        self.minimum_distance = minimum_distance

    def find(

        self,

        spectrum,

        seeds

    ):

        power = spectrum.power_db

        frequencies = spectrum.frequencies

        all_peaks = []

        for seed in seeds:

            start = seed.start_bin

            stop = seed.stop_bin + 1

            local = power[start:stop]

            indices, _ = find_peaks(

                local,

                prominence=self.prominence_db,

                distance=self.minimum_distance

            )

            #
            # Fallback to old behaviour.
            #

            if len(indices) == 0:

                indices = np.array(

                    [

                        int(

                            np.argmax(local)

                        )

                    ]

                )

            #
            # Convert to absolute bins.
            #

            bins = np.sort(

                start + indices

            )

            #
            # Determine valley boundaries.
            #

            left_limits = [start]

            right_limits = []

            for i in range(

                len(bins) - 1

            ):

                left_peak = bins[i]

                right_peak = bins[i + 1]

                valley = (

                    left_peak +

                    np.argmin(

                        power[

                            left_peak:

                            right_peak + 1

                        ]

                    )

                )

                right_limits.append(

                    valley

                )

                left_limits.append(

                    valley

                )

            right_limits.append(

                stop - 1

            )

            if debug("debug_peak_finder") and stop - start > 100:

                print()

                print(

                    f"Large candidate: "

                    f"bins={start}-{stop-1} "

                    f"width={stop-start}"

                )

                print(

                    f"Detected {len(bins)} peak(s)"

                )

            for peak_bin, left, right in zip(

                bins,

                left_limits,

                right_limits

            ):

                if debug("debug_peak_finder") and stop - start > 100:

                    print(

                        f"    Peak "

                        f"{frequencies[peak_bin]/1e6:.6f} MHz"

                        f" "

                        f"slice={left}->{right}"

                    )

                all_peaks.append(

                    Peak(

                        bin_index=int(

                            peak_bin

                        ),

                        frequency=float(

                            frequencies[peak_bin]

                        ),

                        power_db=float(

                            power[peak_bin]

                        ),

                        left_limit=int(

                            left

                        ),

                        right_limit=int(

                            right

                        )

                    )

                )

        return sorted(

            all_peaks,

            key=lambda p: p.bin_index

        )
