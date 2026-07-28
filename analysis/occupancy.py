"""
Spectrum Occupancy Analysis
"""

from dataclasses import dataclass


@dataclass(slots=True)
class OccupancyResult:

    center_frequency: float

    observations: int

    occupancy: float


class OccupancyAnalyzer:

    def analyze(self, database):

        rows = database.occupancy()

        if not rows:

            return []

        maximum = max(

            row["observations"]

            for row in rows

        )

        emitters = {

            row["signal_id"]: row

            for row in database.top_emitters(
                limit=100000
            )

        }

        results = []

        for row in rows:

            emitter = emitters.get(
                row["signal_id"]
            )

            if emitter is None:

                continue

            results.append(

                OccupancyResult(

                    center_frequency=emitter["center_frequency"],

                    observations=row["observations"],

                    occupancy=(
                        row["observations"] /
                        maximum
                    )

                )

            )

        results.sort(

            key=lambda r: r.occupancy,

            reverse=True

        )

        return results
