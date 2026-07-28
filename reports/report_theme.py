"""
JCRO Report Theme
"""


def stylesheet():

    return """

html {

    background-color: #000000;

}

body {

    background-color: #000000;

    color: #FFFFFF;

    font-family: "Times New Roman", serif;

    font-size: 12pt;

    max-width: 1200px;

    margin: 50px auto;

    line-height: 1.55;

}

h1 {

    text-align: center;

    font-size: 30pt;

    margin-bottom: 4px;

}

h2 {

    text-align: center;

    font-size: 18pt;

    margin-top: 35px;

    margin-bottom: 15px;

}

h3 {

    text-align: left;

    font-size: 15pt;

}

hr {

    border: none;

    border-top: 2px solid white;

    margin-top: 25px;

    margin-bottom: 25px;

}

table {

    width: 100%;

    border-collapse: collapse;

    margin-top: 15px;

    margin-bottom: 25px;

}

th {

    border: 1px solid white;

    padding: 10px 14px;

    background-color: #111111;

    text-align: left;

    font-weight: bold;

}

td {

    border: 1px solid white;

    padding: 10px 14px;

    vertical-align: top;

}

tr:nth-child(even) {

    background-color: #090909;

}

tr:hover {

    background-color: #1a1a1a;

}

p {

    text-align: justify;

}

.footer {

    text-align: center;

    margin-top: 20px;

}

.report-title {

    text-align: center;

    font-size: 34pt;

    font-weight: bold;

}

.report-subtitle {

    text-align: center;

    font-size: 18pt;

}

.metric {

    font-weight: bold;

}

.value {

    text-align: right;

}

.frequency {

    font-family: Consolas, "Courier New", monospace;

}

@media print {

    html {

        background: white;

    }

    body {

        background: white;

        color: black;

        max-width: none;

        margin: 1in;

    }

    table {

        page-break-inside: avoid;

    }

    tr:hover {

        background: inherit;

    }

    th {

        background: #EEEEEE;

        color: black;

    }

    td {

        color: black;

    }

    hr {

        border-top: 2px solid black;

    }

}

"""
