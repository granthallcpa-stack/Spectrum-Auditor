"""
JCRO Report Charts
"""

from pathlib import Path

import matplotlib.pyplot as plt

from matplotlib.ticker import StrMethodFormatter
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import ScalarFormatter
import numpy as np


class ReportCharts:

    # -------------------------------------------------

    def __init__(

        self,

        survey_id

    ):

        self.survey_id = survey_id

        self.output_directory = Path(

            "reports/output/charts"

        )

        self.output_directory.mkdir(

            parents=True,

            exist_ok=True

        )

    # -------------------------------------------------

    def filename(

        self,

        name

    ):

        return (

            self.output_directory /

            f"survey_{self.survey_id:06d}_{name}.png"

        )

    # -------------------------------------------------

    def save(

        self,

        name

    ):

        filename = self.filename(

            name

        )

        plt.tight_layout()

        plt.savefig(

            filename,

            dpi=300,

            bbox_inches="tight"

        )

        plt.close()

        return filename.name

    # -------------------------------------------------

    def style_chart(

        self,

        title,

        xlabel,

        ylabel,

        color="#d65f5f"
    ):

        ax = plt.gca()

        ax.set_axisbelow(True)

        fig = plt.gcf()

        #
        # Backgrounds
        #

        fig.patch.set_facecolor(

            "#1b1b1b"

        )

        ax.set_facecolor(

            "#2b2b2b"

        )

        #
        # Title / labels
        #

        ax.set_title(

            title,

            fontsize=18,

            weight="bold",

            color="white"

        )

        ax.set_xlabel(

            xlabel,

            fontsize=13,

            color="#dddddd"

        )

        ax.set_ylabel(

            ylabel,

            fontsize=13,

            color="#dddddd"

        )

        #
        # Ticks
        #

        ax.tick_params(

            axis="both",

            colors="white"

        )

        #
        # Disable scientific notation
        #

        

        #
        # Grid
        #

        ax.grid(

            axis="y",

            color="#555555",

            linestyle="--",

            alpha=0.25

        )

        #
        # Spines
        #

        ax.spines["top"].set_visible(False)

        ax.spines["right"].set_visible(False)

        ax.spines["left"].set_color("#888888")

        ax.spines["bottom"].set_color("#888888")

        plt.tight_layout()

        return color

    def allocation_activity(

        self,

        queries

    ):

        rows = queries.allocation_activity()

        if not rows:

            return None

        labels = []

        for row in rows:

            label = row["allocation"] or ""

            words = label.split()

            if len(words) > 5:

                label = " ".join(words[:6])

            labels.append(label)

        values = [

            row["signals"]

            for row in rows

        ]

        plt.figure(
            figsize=(11,6),
            dpi=200
        )

        color = self.style_chart(

            "RF Allocation Activity",

            "Signals",

            "Allocation",

            color="#4caf50"

        )

        plt.barh(

            labels,

            values,

            color=color,

            edgecolor="#dddddd",

            linewidth=0.3

        )

        ax = plt.gca()

        ax.set_xscale("log")

        ax.xaxis.set_major_formatter(
            StrMethodFormatter("{x:,.0f}")
        )

        plt.tight_layout()

        return self.save(

            "allocation_activity"

        )

    # -------------------------------------------------
    def snr_distribution(

        self,

        queries

    ):

        rows = queries.snr_values()

        if not rows:

            return None

        values = [

            row["peak_snr"]

            for row in rows

        ]

        plt.figure(
            figsize=(11,6),
            dpi=200
        )

        color = self.style_chart(

            "Peak SNR Distribution",

            "Peak SNR (dB)",

            "Observations (log scale)"

        )

        plt.hist(

            values,

            bins=40,

            color=color,

            edgecolor="#dddddd",

            linewidth=0.3

        )

        plt.yscale(

            "log"

        )

        ax = plt.gca()

        ax.xaxis.set_major_formatter(
            StrMethodFormatter("{x:.0f}")
        )

        ax.yaxis.set_major_formatter(
            ScalarFormatter()
        )

        ax.yaxis.get_major_formatter().set_scientific(False)
        ax.yaxis.get_major_formatter().set_useOffset(False)

        ax.tick_params(
            axis="y",
            which="both",
            colors="white"
        )

        for label in ax.get_yticklabels(which="both"):
            label.set_color("white")

        plt.tight_layout()

        return self.save(

            "snr_distribution"

        )
    # -------------------------------------------------

    def bandwidth_distribution(

        self,

        queries

    ):

        rows = queries.bandwidth_values()

        if not rows:

            return None

        values = [

            row["bandwidth"]

            for row in rows

            if row["bandwidth"] > 0

        ]

        plt.figure(
            figsize=(11,6),
            dpi=200
        )

        color = self.style_chart(

            "Bandwidth Distribution",

            "Bandwidth (Hz, log scale)",

            "Observations (log scale)"

        )

        if not values:
            return None

        bins = np.logspace(

            np.log10(min(values)),

            np.log10(max(values)),

            40

        )

        plt.hist(

            values,

            bins=bins,

            color=color,

            edgecolor="#dddddd",

            linewidth=0.3

        )

        plt.xscale(

            "log"

        )

        plt.yscale(

            "log"

        )

        ax = plt.gca()

        ax.xaxis.set_major_formatter(
            StrMethodFormatter("{x:,.0f}")
        )

        ax.yaxis.set_major_formatter(
            FuncFormatter(
                lambda x, _: f"{int(x):,}" if x >= 1 else f"{x:g}"
            )
        )

        ax.tick_params(
            axis="y",
            which="both",
            colors="white"
        )

        for label in ax.get_yticklabels(which="both"):
            label.set_color("white")

        plt.tight_layout()

        return self.save(

            "bandwidth_distribution"

        )

    # -------------------------------------------------

    def frequency_distribution(

        self,

        queries

    ):

        rows = queries.frequency_values()

        if not rows:

            return None

        values = [

            row["center_frequency"] / 1e6

            for row in rows

        ]

        plt.figure(
            figsize=(11,6),
            dpi=200
        )

        color = self.style_chart(

            "Spectrum Occupancy",

            "Frequency (MHz)",

            "Signals"

        )

        plt.hist(

            values,

            bins=75,

            color=color,

            edgecolor="#dddddd",

            linewidth=0.3

        )

        ax = plt.gca()

        ax.xaxis.set_major_formatter(
            StrMethodFormatter("{x:,.1f}")
        )

        ax.yaxis.set_major_formatter(
            StrMethodFormatter("{x:,.0f}")
        )

        plt.tight_layout()

        return self.save(

            "frequency_distribution"

        )


# -------------------------------------------------

    def historical_service_activity(

        self,

        queries

    ):

        rows = queries.historical_service_activity()

        if not rows:

            return None

        labels = [

            row["service"]

            for row in rows

        ]

        values = [

            row["signals"]

            for row in rows

        ]

        plt.figure(

            figsize=(11,6),

            dpi=200

        )

        color = self.style_chart(

            "Historical Service Activity",

            "Signals",

            "Service",

            color="#4caf50"

        )

        plt.barh(

            labels,

            values,

            color=color,

            edgecolor="#dddddd",

            linewidth=0.3

        )

        ax = plt.gca()

        ax.set_xscale("log")

        ax.xaxis.set_major_formatter(
            StrMethodFormatter("{x:,.0f}")
        )

        return self.save(

            "historical_service_activity"

        )


    # -------------------------------------------------

    def historical_snr_distribution(

        self,

        queries

    ):

        rows = queries.historical_snr_values()

        if not rows:

            return None

        values = [

            row["peak_snr"]

            for row in rows

        ]

        plt.figure(

            figsize=(11,6),

            dpi=200

        )

        color = self.style_chart(

            "Historical Peak SNR Distribution",

            "Peak SNR (dB)",

            "Observations (log scale)"

        )

        plt.hist(

            values,

            bins=40,

            color=color,

            edgecolor="#dddddd",

            linewidth=0.3

        )

        plt.yscale(

            "log"

        )

        ax = plt.gca()

        ax.xaxis.set_major_formatter(
            StrMethodFormatter("{x:.0f}")
        )

        ax.yaxis.set_major_formatter(
            FuncFormatter(
                lambda x, _: f"{int(x):,}" if x >= 1 else f"{x:g}"
            )
        )

        ax.tick_params(
            axis="y",
            which="both",
            colors="white"
        )

        for label in ax.get_yticklabels(which="both"):
            label.set_color("white")

        return self.save(

            "historical_snr_distribution"

        )

# -----------------------------------------------------


def build_charts(

    queries

):

    charts = ReportCharts(

        queries.survey()["survey_id"]

    )

    html = []

    chart_list = [

        (

            "RF Allocation Activity",

            charts.allocation_activity(

                queries

            )

        ),

        (

            "Peak SNR Distribution",

            charts.snr_distribution(

                queries

            )

        ),

        (

            "Bandwidth Distribution",

            charts.bandwidth_distribution(

                queries

            )

        ),

        (

            "Spectrum Occupancy",

            charts.frequency_distribution(

                queries

            )

        )

    ]

    for title, filename in chart_list:

        if filename is None:

            continue

        html.append(

            f"""

<h2>

{title}

</h2>

<p>

<img

src="charts/{filename}"

style="width:100%;max-width:1000px;">

</p>

<hr>

"""

        )

    return "\n".join(

        html

    )

def build_historical_charts(

    queries

):

    charts = ReportCharts(

        queries.survey()["survey_id"]

    )

    html = []

    chart_list = [

        (

            "Historical Service Activity",

            charts.historical_service_activity(

                queries

            )

        ),

        (

            "Historical Peak SNR Distribution",

            charts.historical_snr_distribution(

                queries

            )

        )

    ]

    for title, filename in chart_list:

        if filename is None:

            continue

        html.append(

            f"""

<h2>

{title}

</h2>

<p>

<img

src="charts/{filename}"

style="width:100%;max-width:1000px;">

</p>

<hr>

"""

        )

    return "\n".join(

        html

    )