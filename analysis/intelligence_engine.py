"""
RF Intelligence Engine
"""

from knowledge.database import RFKnowledgeDatabase


class IntelligenceEngine:

    def __init__(self):

        self.database = RFKnowledgeDatabase()

    # -------------------------------------------------

    def identify(self, observation):

        measurement = observation.measurement

        frequency = measurement.center_frequency / 1e6

        result = self.database.lookup(frequency)

        if result:

            print(
                f"[KNOWN] "
                f"{frequency:.4f} MHz"
                f" -> "
                f"{result.system}"
            )

        return result

    # -------------------------------------------------

    def close(self):

        self.database.close()