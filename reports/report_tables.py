"""
JCRO Report Tables
"""



def build_tables(

    queries

):

    html = []

    html.append(receiver_configuration_table(queries))

    html.append(survey_statistics_table(queries))

    html.append(build_environment(queries))

    html.append(bandwidth_statistics_table(queries))

    html.append(allocation_activity_table(queries))

    html.append(strongest_emitters_table(queries))


    return "\n".join(

        html

    )


# ---------------------------------------------------------

def receiver_configuration_table(

    queries

):

    receiver = queries.receiver_configuration()

    gain = (
        "Auto"
        if float(receiver["gain"]) == 0
        else f'{receiver["gain"]:.1f} dB'
    )

    overlap = (
        f'{receiver["overlap"]:.2f}'
        if receiver["overlap"] is not None
        else "N/A"
    )

    dwell = (
        f'{receiver["dwell"]:.2f} s'
        if receiver["dwell"] is not None
        else "N/A"
    )

    return f"""

<h2>

Receiver Configuration

</h2>

<table>

<tr><th>Parameter</th><th>Value</th></tr>

<tr><td>Receiver</td><td>{receiver["receiver"]}</td></tr>

<tr><td>Sample Rate</td><td>{receiver["sample_rate"]/1e6:.3f} MS/s</td></tr>

<tr><td>Gain</td><td>{gain}</td></tr>

<tr><td>FFT Overlap</td><td>{overlap}</td></tr>

<tr><td>Dwell Time</td><td>{dwell}</td></tr>

<tr><td>Started</td><td>{receiver["started"]}</td></tr>

<tr><td>Finished</td><td>{receiver["finished"]}</td></tr>

</table>

<hr>

"""

# ---------------------------------------------------------


def survey_statistics_table(

    queries

):

    summary = queries.survey_summary()

    known = summary["known_emitters"]

    unknown = summary["unknown_emitters"]

    return f"""

<h2>

Survey Statistics

</h2>

<table>

<tr><th>Metric</th><th>Value</th></tr>

<tr><td>Survey Duration</td><td>{summary["duration"]:.1f} sec</td></tr>

<tr><td>Observation Windows</td><td>{summary["windows"]:,}</td></tr>

<tr><td>Signals Detected</td><td>{summary["signals"]:,}</td></tr>

<tr><td>Known Signals</td><td>{known:,}</td></tr>

<tr><td>Unknown Signals</td><td>{unknown:,}</td></tr>

<tr><td>Average Signals / Window</td><td>{summary["average_signals"]:.2f}</td></tr>

<tr><td>Strongest Signal</td><td>{summary["strongest_signal"]:.2f} dB</td></tr>

</table>

<hr>

"""


# ---------------------------------------------------------


def bandwidth_statistics_table(

    queries

):

    bandwidth = queries.bandwidth_statistics()

    snr = queries.snr_statistics()

    return f"""

<h2>

Signal Statistics

</h2>

<table>

<tr><th>Measurement</th><th>Value</th></tr>

<tr><td>Average Bandwidth</td><td>{bandwidth["average_bandwidth"]:.0f} Hz</td></tr>

<tr><td>Minimum Bandwidth</td><td>{bandwidth["minimum_bandwidth"]:.0f} Hz</td></tr>

<tr><td>Maximum Bandwidth</td><td>{bandwidth["maximum_bandwidth"]:.0f} Hz</td></tr>

<tr><td>Observations</td><td>{bandwidth["observations"]:,}</td></tr>

<tr><td>Average Peak SNR</td><td>{snr["average_snr"]:.2f} dB</td></tr>

<tr><td>Maximum Peak SNR</td><td>{snr["maximum_snr"]:.2f} dB</td></tr>

</table>

<hr>

"""

# ---------------------------------------------------------

def allocation_activity_table(

    queries

):

    allocations = queries.allocation_activity()

    rows = []

    for allocation in allocations:

        rows.append(

            f"""

<tr>

<td>{allocation["allocation"]}</td>

<td>{allocation["signals"]:,}</td>

</tr>

"""

        )

    return f"""

<h2>

RF Allocation Activity

</h2>

<table>

<tr>

<th>Allocation</th>

<th>Signals</th>

</tr>

{''.join(rows)}

</table>

<hr>

"""

# ---------------------------------------------------------

def strongest_emitters_table(

    queries

):

    emitters = queries.strongest_emitters()

    rows = []

    for emitter in emitters:

        average = emitter["historical_average_peak_snr"]
        difference = emitter["percent_difference"]

        average_text = (

            f"{average:.2f}"

            if average is not None

            else "—"

        )

        difference_text = (

            f"{difference:+.1f}%"

            if difference is not None

            else "N/A"

        )

        style = ""

        if difference is not None:

            if difference > 20:

                style = ' style="color:lime;font-weight:bold;"'

            elif difference < -20:

                style = ' style="color:red;font-weight:bold;"'

        rows.append(

            f"""

<tr>

<td>{emitter["center_frequency"]/1e6:.4f}</td>

<td>{emitter["allocations"] or "Unknown"}</td>

<td>{emitter["bandwidth"]:.0f}</td>

<td>{emitter["peak_snr"]:.2f}</td>

<td>{average_text}</td>

<td{style}>{difference_text}</td>

</tr>

"""

        )

    return f"""

<h2>

Strongest Emitters

</h2>

<table>

<tr>

<th>Frequency (MHz)</th>

<th>Allocation</th>

<th>Bandwidth (Hz)</th>

<th>Peak SNR (dB)</th>

<th>15-Survey Avg (dB)</th>

<th>% Difference</th>

</tr>

{''.join(rows)}

</table>

<hr>

"""

# ---------------------------------------------------------


def build_environment(

    queries

):

    environment = queries.environment_summary()

    return f"""

<h2>

RF Environment

</h2>

<table>

<tr>

<th>Measurement</th>

<th>Value</th>

</tr>

<tr>

<td>Average Noise Floor</td>

<td>{environment["average_noise"]:.2f} dB</td>

</tr>

<tr>

<td>Minimum Noise Floor</td>

<td>{environment["minimum_noise"]:.2f} dB</td>

</tr>

<tr>

<td>Maximum Noise Floor</td>

<td>{environment["maximum_noise"]:.2f} dB</td>

</tr>

<tr>

<td>Average Noise Sigma</td>

<td>{environment["average_sigma"]:.2f} dB</td>

</tr>

<tr>

<td>Average Detection Threshold</td>

<td>{environment["average_threshold"]:.2f} dB</td>

</tr>

<tr>

<td>Average Signals / Window</td>

<td>{environment["average_signals"]:.2f}</td>

</tr>

<tr>

<td>Average Minimum SNR</td>

<td>{environment["average_minimum_snr"]:.2f} dB</td>

</tr>

<tr>

<td>Maximum Peak SNR</td>

<td>{environment["maximum_snr"]:.2f} dB</td>

</tr>

<tr>

<td>Average Median SNR</td>

<td>{environment["average_median_snr"]:.2f} dB</td>

</tr>

<tr>

<td>Busiest Observation Window</td>

<td>{environment["busiest_window"]:.0f}</td>

</tr>

<tr>

<td>Quietest Observation Window</td>

<td>{environment["quietest_window"]:.0f}</td>

</tr>

</table>

<hr>

"""