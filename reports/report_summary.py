"""
JCRO Report Summary
"""

from datetime import datetime


# ---------------------------------------------------------

def build_header(

    queries

):

    survey = queries.survey()

    started = (
        datetime
        .fromisoformat(survey["started"])
        .astimezone()

    )

    return f"""

<h1>

Jefferson County Radiological Observatory (JCRO)

</h1>

<h2>

Electromagnetic Spectrum Intelligence Report

</h2>

<hr>

<p><b>Experiment Number:</b> 1</p>

<p><b>Scan Date:</b> {started.strftime("%B %d, %Y")}</p>

<p><b>Scan Time:</b> {started.strftime("%I:%M:%S %p")}</p>

<p><b>Scan Number:</b> {survey["survey_id"]}</p>

<p><b>Receiver:</b> {survey["receiver"]}</p>

<p><b>Sample Rate:</b> {survey["sample_rate"]/1e6:.3f} MHz</p>

<hr>

"""


# ---------------------------------------------------------

# ---------------------------------------------------------

def executive_summary(

    queries

):

    summary = queries.survey_summary()

    known = queries.known_signal_count()

    unknown = queries.unknown_signal_count()

    allocations = queries.allocation_activity()

    strongest = queries.strongest_emitters(1)

    bandwidth = queries.bandwidth_statistics()

    allocation_summary = []

    for allocation in allocations[:5]:

        allocation_summary.append(

            f"{allocation['allocation']} ({allocation['signals']:,})"

        )

    if strongest:

        strongest_text = (

            f"{strongest[0]['center_frequency']/1e6:.4f} MHz "

            f"({strongest[0]['peak_snr']:.2f} dB SNR)"

        )

    else:

        strongest_text = "None"

    return f"""

<h2>

Executive Summary

</h2>

<p>

The Jefferson County Radiobiology Observatory (JCRO)
completed a calibrated spectrum survey consisting of
<b>{summary["windows"]:,}</b> observation windows collected
over <b>{summary["duration"]:.1f} seconds</b>.

</p>

<p>

The most active services observed during this survey were:

<b>{", ".join(allocation_summary)}</b>.

</p>

<p>

The strongest detected emitter occurred at
<b>{strongest_text}</b>. Across all observations, the
average signal bandwidth measured
<b>{bandwidth["average_bandwidth"]:.0f} Hz</b>.

</p>

<p>

The observatory recorded an average of
<b>{summary["average_signals"]:.2f}</b> signals per
observation window, providing a detailed characterization
of the RF environment during the survey period.

</p>

<hr>

"""


