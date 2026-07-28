"""
Signal Merger

Combines detections that likely belong to the same RF emission.
"""

from copy import deepcopy


def merge_signals(

    signals,

    merge_distance_hz=2000

):

    if not signals:

        return []

    signals = sorted(

        signals,

        key=lambda signal: signal.measurement.center_frequency

    )

    merged = []

    current = deepcopy(

        signals[0]

    )

    count = 1

    current_measurement = current.measurement

    for signal in signals[1:]:

        measurement = signal.measurement

        if abs(

            measurement.center_frequency -

            current_measurement.center_frequency

        ) <= merge_distance_hz:

            #
            # Weighted center frequency
            #

            current_measurement.center_frequency = (

                current_measurement.center_frequency *

                count +

                measurement.center_frequency

            ) / (

                count + 1

            )

            #
            # Expand occupied spectrum
            #

            current_measurement.start_frequency = min(

                current_measurement.start_frequency,

                measurement.start_frequency

            )

            current_measurement.stop_frequency = max(

                current_measurement.stop_frequency,

                measurement.stop_frequency

            )

            current_measurement.bandwidth = (

                current_measurement.stop_frequency -

                current_measurement.start_frequency

            )

            #
            # Preserve strongest signal
            #

            current_measurement.peak_snr = max(

                current_measurement.peak_snr,

                measurement.peak_snr

            )

            #
            # Average confidence
            #

            current_measurement.confidence = (

                current_measurement.confidence *

                count +

                measurement.confidence

            ) / (

                count + 1

            )

            #
            # Lowest observed noise floor
            #

            current_measurement.noise_floor = min(

                current_measurement.noise_floor,

                measurement.noise_floor

            )

            count += 1

        else:

            merged.append(

                current

            )

            current = deepcopy(

                signal

            )

            current_measurement = current.measurement

            count = 1

    merged.append(

        current

    )

    return merged
