"""
Survey CSV Export
"""

import csv
from pathlib import Path


def export_signal_catalog(

    signals,

    intelligence,

    survey_number

):

    output = Path(

        "data"

    )

    output.mkdir(

        exist_ok=True

    )

    filename = output / (

        f"signal_catalog_{survey_number:04d}.csv"

    )

    with open(

        filename,

        "w",

        newline="",

        encoding="utf-8"

    ) as file:

        writer = csv.writer(

            file

        )

        for signal in signals:

            measurement = signal.measurement

            result = intelligence.identify(

                signal

            )

            if result is None:

                known = "No"

                service = ""

                description = ""

            else:

                known = "Yes"

                service = result["service"]

                description = result["description"]

            writer.writerow(

                [

                    measurement.center_frequency / 1e6,

                    measurement.bandwidth,

                    measurement.peak_power,

                    measurement.peak_snr,

                    known,

                    service,

                    description

                ]

            )

    return filename
