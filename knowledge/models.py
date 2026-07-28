"""
Knowledge Models
"""

from dataclasses import dataclass


@dataclass(slots=True)
class KnowledgeSignal:

    frequency: float

    service: str

    system: str

    site: str

    license: str

    county: str

    state: str

    # -------------------------------------------------

    @classmethod
    def from_csv(cls, row):

        return cls(

            frequency=float(row["Frequency"]),

            service=row["Service"],

            system=row["System"],

            site=row["Site"],

            license=row["License"],

            county=row["County"],

            state=row["State"]

        )

    # -------------------------------------------------

    @classmethod
    def from_row(cls, row):

        return cls(

            frequency=row["frequency"],

            service=row["service"],

            system=row["system"],

            site=row["site"],

            license=row["license"],

            county=row["county"],

            state=row["state"]

        )