import csv
from pathlib import Path


def export_known_signals(
    signals,
    survey_id
):
    """
    Export all known signal matches for a survey to CSV.

    The CSV automatically includes every column returned by
    queries.knowledge_identifications(), so no changes are needed
    when new fields are added to the SQL query.
    """

    if not signals:
        return

    output_directory = Path("exports") / "known_signals"
    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = output_directory / f"survey_{survey_id:06d}.csv"

    rows = [
        dict(signal)
        for signal in signals
    ]

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(rows)