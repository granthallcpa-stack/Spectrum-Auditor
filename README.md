README.MD



Tested Systems:

Ubuntu 26.04 (tested)
Likely to work on most Linux Distros as long as you are using Python 3.12 and venv.


Before Running Your First Audit:


1. Python Framework:

Python 3.12 (Virtual Environment)

## Python 3.12 Setup

Spectrum Audit has been tested with **Python 3.12**.

### Ubuntu

Install Python 3.12 and the virtual environment package:

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv
```

Verify the installation:

```bash
python3.12 --version
```

Expected output:

```text
Python 3.12.x
```

## Create a Virtual Environment

From the project root:

```bash
python3.12 -m venv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Verify the Python version:

```bash
python --version
```

Expected output:

```text
Python 3.12.x
```

######################


2. RTL-SDR Framework

## Install RTL-SDR

### Option 1 (Recommended)

Install the RTL-SDR library from your distribution's package manager.

```bash
sudo apt update
sudo apt install rtl-sdr librtlsdr-dev
```

Verify the installation:

```bash
rtl_test
```

---

### Option 2: Build RTL-SDR from Source

Clone the official RTL-SDR repository:

```bash
git clone https://github.com/osmocom/rtl-sdr.git
cd rtl-sdr
```

Create a build directory:

```bash
mkdir build
cd build
```

Configure the project:

```bash
cmake .. -DINSTALL_UDEV_RULES=ON
```

Compile:

```bash
make -j$(nproc)
```

Install:

```bash
sudo make install
sudo ldconfig
```

(Optional) Install the udev rules:

```bash
sudo cp ../rtl-sdr.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Verify the installation:

```bash
rtl_test
```


## Build the Knowledge Database

Before running a spectrum survey, build the RF knowledge database:

```bash
python knowledge/build_database.py
```

This creates:

```
knowledge/rf_knowledge.db
```

The database only needs to be built once unless the RF knowledge source data is modified.


######################

3. Install Python Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs the required Python packages, including PyRTLSDR, NumPy, SciPy, Matplotlib, and other project dependencies.


______________________


Once these steps are completed return to project root and:

1. run an rtl_test. if this is successful, you can press ctrl ^ C and clear.

2. run your first audit by running python audit.py.

3. Once you have completed the audit you should see at the end an output directory where an html report of the comprehensive scan was made. There are three primary data storage locations:

	1. /data: these are csv reports that give you insights on your scan as well as previous scans.
	
	2. /exports/known_signals: these are csv exports on data surrounding known signals from the knowledge database.
	
	3. /reports: these output html reports that you can go through and see a summary of the scan collected.
