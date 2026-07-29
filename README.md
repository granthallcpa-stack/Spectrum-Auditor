<img width="1068" height="654" alt="screen2" src="https://github.com/user-attachments/assets/19e36820-8ffa-41e4-bbe2-53d0e8d41100" />


*This project is open source. No license is required to use or remake.

Note to reader:

* This system is modeled on a sample of the Jefferson County, AL licensed radio spectrum. I am aware that most users are not from this geographical area. However, with that being said the scanner should work fine.

If you are interested in upgrading this system for personal use catered to your specific area, please contact me directly at granthall.cpa@gmail.com and include in your email:

1. The geographic area which you are looking to identify.

2. Whether use will be for personal, business, or for government.

3. How you intend to use this system to better understand your RF Environment.





###############





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

NOTE: Most Linux Distros do not not hold python 3.12 in apt, if you get an error saying "PACKAGE NOT FOUND", try this instead based on your distro:

Ubuntu:

```bash
sudo apt update
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.12 python3.12-venv python3.12-dev
```

Kali:

```bash
sudo apt install -y \
build-essential \
zlib1g-dev \
libncurses5-dev \
libgdbm-dev \
libnss3-dev \
libssl-dev \
libreadline-dev \
libffi-dev \
libsqlite3-dev \
libbz2-dev \
liblzma-dev \
libexpat1-dev \
tk-dev \
uuid-dev \

cd /tmp

wget https://www.python.org/ftp/python/3.12.11/Python-3.12.11.tgz

tar -xf Python-3.12.11.tgz

cd Python-3.12.11

./configure --enable-optimizations

make -j"$(nproc)"

sudo make altinstall

python3.12 --version
```

Verify the installation:

```bash
python3.12 --version
```

Expected output:

```text
Python 3.12.x
```

## Create Spectrum Auditor

From the project root:

```bash
git clone https://github.com/granthallcpa-stack/Spectrum-Auditor.git
cd ~/Spectrum-Auditor
```

Activate the virtual environment:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
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
python -m knowledge.build_database
```

This creates:

```
knowledge/rf_knowledge.db
```

The database only needs to be built once unless the RF knowledge source data is modified.


######################


______________________


Once these steps are completed return to project root and:

1. run an rtl_test. if this is successful, you can press ctrl ^ C and clear.

2. run your first audit by running

```
python audit.py.
```
or if you want to run continuous scans (runs every 20 minutes). you can run:

```
python continuous_audit.py.
```

5. Once you have completed the audit you should see at the end an output directory where an html report of the comprehensive scan was made. There are three primary data storage locations:

	1. /data: these are csv reports that give you insights on your scan as well as previous scans.
	
	2. /exports/known_signals: these are csv exports on data surrounding known signals from the knowledge database.
	
	3. /reports: these output html reports that you can go through and see a summary of the scan collected.


<img width="1391" height="851" alt="screen" src="https://github.com/user-attachments/assets/2b607c0b-e084-4752-953f-dc3b79dbba10" />
