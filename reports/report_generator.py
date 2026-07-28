"""
JCRO Report Generator

Assembles the complete HTML laboratory report.
"""

from pathlib import Path
from datetime import datetime

from reports.report_theme import stylesheet
from reports.report_queries import ReportQueries

from reports.report_summary import (
    build_header,
    executive_summary,
)

from reports.report_tables import (
    build_tables,
    build_environment,
)

from reports.report_charts import (

    build_charts,

    build_historical_charts,

)

from reports.report_footer import build_footer


from reports.report_history import (
    build_history_tables,
)

from reports.report_identifications import (

    build_knowledge_identifications,

    build_new_signal_identifications,

)


class ReportGenerator:

    def __init__(self):

        self.output_directory = Path(
            "reports/output"
        )

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

    # -------------------------------------------------

    def generate(

        self,

        database,

        survey_id,

        elapsed

    ):

        queries = ReportQueries(

            database,

            survey_id

        )

        html = [

            "<!DOCTYPE html>",

            "<html>",

            "<head>",

            "<meta charset='utf-8'>",

            "<title>JCRO Report</title>",

            "<style>",

            stylesheet(),

            "</style>",

            "</head>",

            "<body>",

            build_header(
                queries
            ),

            executive_summary(
                queries
            ),

            build_tables(
                queries
            ),

            build_knowledge_identifications(
                queries
            ),

            build_new_signal_identifications(
                queries
            ),

            build_charts(
                queries
            ),

            build_history_tables(
                queries
            ),

            build_historical_charts(
                queries
            ),

            build_footer(
                queries
            ),

            "</body>",

            "</html>",

        ]

        document = "\n".join(html)

        filename = (

            self.output_directory /

            f"survey_{survey_id:06d}.html"

        )

        filename.write_text(

            document,

            encoding="utf-8"

        )

        return str(
            filename
        )
