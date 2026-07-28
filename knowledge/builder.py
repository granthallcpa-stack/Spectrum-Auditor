"""
Knowledge Base Builder
"""

from knowledge.models import KnowledgeSignal


def build_site(

    *,

    frequencies,

    service,

    system,

    site,

    license,

    county,

    state

):

    records = []

    for frequency in frequencies:

        records.append(

            KnowledgeSignal(

                frequency=frequency,

                service=service,

                system=system,

                site=site,

                license=license,

                county=county,

                state=state

            )

        )

    return records