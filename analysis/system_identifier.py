"""
System Identifier

Matches observed RF signals against known frequency databases.
"""

from dataclasses import dataclass

from knowledge.public_safety import PUBLIC_SAFETY


@dataclass(slots=True)
class IdentifiedSystem:

    signal: object

    service: str

    system: str

    site: str

    channel: str

    county: str

    state: str

    protocol: str

    confidence: float


class SystemIdentifier:

    def __init__(self):

        self.known_systems = []

        self.known_systems.extend(PUBLIC_SAFETY)

    # --------------------------------------------------

    def identify(self, signal):

        measurement = signal.measurement

        for known in self.known_systems:

            if abs(

                measurement.center_frequency -

                known.frequency

            ) <= known.tolerance:

                return IdentifiedSystem(

                    signal=signal,

                    service=known.service,

                    system=known.system,

                    site=known.site,

                    channel=known.channel,

                    county=known.county,

                    state=known.state,

                    protocol=known.protocol,

                    confidence=known.confidence

                )

        return None

    # --------------------------------------------------

    def identify_many(self, signals):

        identified = []

        for signal in signals:

            match = self.identify(signal)

            if match is not None:

                identified.append(match)

        return identified
