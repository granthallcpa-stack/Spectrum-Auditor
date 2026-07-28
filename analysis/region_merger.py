"""
Region Merger

Merges nearby candidate regions into larger occupied
spectrum regions.
"""

from analysis.candidate_seeds import CandidateSeed

from core.debug import debug


class RegionMerger:

    def __init__(

        self,

        merge_distance: int = 4

    ):

        self.merge_distance = merge_distance

    def merge(

        self,

        regions

    ):

        if not regions:

            return []

        merged = [

            regions[0]

        ]

        for region in regions[1:]:

            previous = merged[-1]

            gap = (

                region.start_bin -

                previous.stop_bin -

                1

            )

            if gap <= self.merge_distance:

                if debug("debug_region_merger"):

                    print(
                        f"Merging:"
                        f" {previous.start_bin}-{previous.stop_bin}"
                        f" + "
                        f"{region.start_bin}-{region.stop_bin}"
                        f" Gap={gap}"
                    )

                merged[-1] = CandidateSeed(

                    start_bin=previous.start_bin,

                    stop_bin=region.stop_bin

                )

            else:

                merged.append(

                    region

                )

        return merged
