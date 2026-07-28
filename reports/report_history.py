"""
JCRO Historical Tables
"""


def build_history_tables(

    queries

):

    #
    # Most Frequently Observed Emitters
    #

    most_observed_rows = []

    for signal in queries.most_observed_signals():

        most_observed_rows.append(

            f"""
<tr>

<td>{signal["center_frequency"]/1e6:.4f}</td>

<td>{signal["observations"]:,}</td>

<td>{signal["average_bandwidth"]:.0f}</td>

<td>{signal["peak_bandwidth"]:.0f}</td>

<td>{signal["first_seen"]}</td>

<td>{signal["average_snr"]:.2f}</td>

<td>{signal["allocation"] or "Unknown"}</td>

</tr>
"""

        )

    #
    # Historical Strongest Emitters
    #

    strongest_rows = []

    for signal in queries.historical_strongest_emitters():

        strongest_rows.append(

            f"""
<tr>

<td>{signal["center_frequency"]/1e6:.4f}</td>

<td>{signal["peak_snr"]:.2f}</td>

<td>{signal["allocations"] or "Unknown"}</td>

<td>{signal["service"] or "Unknown"}</td>

<td>{signal["bandwidth"]:.0f}</td>

<td>{signal["observed"]}</td>

</tr>
"""

        )

    return f"""

<h2>

Most Frequently Observed Emitters

</h2>

<table>

<tr>

<th>Frequency (MHz)</th>

<th>Observations</th>

<th>Average BW (Hz)</th>

<th>Peak BW (Hz)</th>

<th>First Seen</th>

<th>Average SNR (dB)</th>

<th>Allocation</th>

</tr>

{''.join(most_observed_rows)}

</table>

<hr>

<h2>

Historical Strongest Emitters

</h2>

<table>

<tr>

<th>Frequency (MHz)</th>

<th>Peak SNR (dB)</th>

<th>Allocation</th>

<th>Service</th>

<th>Bandwidth (Hz)</th>

<th>Observation Date</th>

</tr>

{''.join(strongest_rows)}

</table>

<hr>

"""