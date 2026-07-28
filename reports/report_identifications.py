"""
JCRO Report Identifications
"""

from knowledge.export_known_signals import export_known_signals

# ---------------------------------------------------------

def build_known_signals(

    queries

):

    signals = queries.known_signals()

    rows = []

    for signal in signals:

        rows.append(

            f"""

<tr>

<td>{signal["frequency"]:.4f}</td>

<td>{signal["service"]}</td>

<td>{signal["system"]}</td>

<td>{signal["site"]}</td>

<td>{signal["county"]}</td>

<td>{signal["peak_snr"]:.2f}</td>

</tr>

"""

        )

    if not rows:

        rows.append(

            """

<tr>

<td colspan="6" style="text-align:center">

No known signals identified during this survey.

</td>

</tr>

"""

        )

    return f"""

<h2>

Known Signal Identifications

</h2>

<table>

<tr>

<th>Frequency (MHz)</th>

<th>Service</th>

<th>System</th>

<th>Site</th>

<th>County</th>

<th>Peak SNR (dB)</th>

</tr>

{''.join(rows)}

</table>

<hr>

"""


# ---------------------------------------------------------

def build_new_signal_identifications(

    queries

):

    signals = queries.new_signal_identifications()

    rows = []

    for signal in signals:

        rows.append(

            f"""

<tr>

<td>{signal["center_frequency"]/1e6:.4f}</td>

<td>{signal["service"]}</td>

<td>{signal["system"]}</td>

<td>{signal["site"]}</td>

<td>{signal["county"]}</td>

<td>{signal["peak_snr"]:.2f}</td>

</tr>

"""

        )

    if not rows:

        rows.append(

            """

<tr>

<td colspan="6" style="text-align:center">

No new signal identifications during this survey.

</td>

</tr>

"""

        )

    return f"""

<h2>

New Signal Identifications

</h2>

<p>

Signals identified for the first time during this survey.

</p>

<table>

<tr>

<th>Frequency (MHz)</th>

<th>Service</th>

<th>System</th>

<th>Site</th>

<th>County</th>

<th>Peak SNR (dB)</th>

</tr>

{''.join(rows)}

</table>

<hr>

"""


# ---------------------------------------------------------

def build_knowledge_identifications(

    queries

):

    signals = queries.knowledge_identifications()

    export_known_signals(
        signals,
        queries.survey_id
    )

    if not signals:

        return ""

    rows = []

    best_signals = {}

    for signal in signals:

        key = signal["frequency"]

        if (

            key not in best_signals

            or

            signal["current_peak_snr"] >

            best_signals[key]["current_peak_snr"]

        ):

            best_signals[key] = signal

    for signal in sorted(
        best_signals.values(),
        key=lambda s: s["frequency"]
    ):

        difference = signal["percent_difference"]

        row_style = ""
        difference_style = ""

        system = (signal["system"] or "").lower()

        keywords = (
            "city",
            "county",
            "state",
            "district",
            "fire",
            "rescue",
            "police",
            "sheriff",
            "ems",
            "emergency",
            "911",
            "9-1-1",
        )

        if any(keyword in system for keyword in keywords):

            row_style = ' style="background-color:#ffb347;"'

        current_peak = (
            f"{signal['current_peak_snr']:.2f}"
            if signal["current_peak_snr"] is not None
            else "—"
        )

        historical_peak = (
            f"{signal['historical_average_peak_snr']:.2f}"
            if signal["historical_average_peak_snr"] is not None
            else "—"
        )

        historical_bandwidth = (
            f"{signal['historical_average_bandwidth']:.0f}"
            if signal["historical_average_bandwidth"] is not None
            else "—"
        )

        current_bandwidth = (
            f"{signal['current_bandwidth']:.0f}"
            if signal["current_bandwidth"] is not None
            else "—"
        )

        difference_text = (
            f"{difference:+.1f}%"
            if difference is not None
            else "—"
        )

        if difference is not None:

            if difference > 20:

                difference_style = ' style="color:lime;font-weight:bold;"'

            elif difference < -20:

                difference_style = ' style="color:red;font-weight:bold;"'

        rows.append(
            f"""

    <tr{row_style}>

    <td>{signal["frequency"]:.4f}</td>

    <td>{signal["service"]}</td>

    <td>{signal["system"]}</td>

    <td>{signal["site"] or "—"}</td>

    <td>{signal["license"] or "—"}</td>

    <td>{signal["county"] or "—"}</td>

    <td>{historical_bandwidth}</td>

    <td>{current_bandwidth}</td>

    <td>{current_peak}</td>

    <td>{historical_peak}</td>

    <td{difference_style}>{difference_text}</td>

    </tr>

    """
        )

    return f"""

<h2>

Knowledge Database Identifications

</h2>

<p>

Signals successfully matched against the RF knowledge database.

</p>

<table>

<tr>

<th>Frequency (MHz)</th>

<th>Service</th>

<th>System</th>

<th>Site</th>

<th>License</th>

<th>County</th>

<th>Historical Avg BW (Hz)</th>

<th>Current BW (Hz)</th>

<th>Peak SNR (Current Survey)</th>

<th>Historical Avg Peak SNR (dB)</th>

<th>% Difference</th>

</tr>

{''.join(rows)}

</table>

<hr>

"""