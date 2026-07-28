"""
Spectrum Audit Configuration

All project configuration is centralized here.

Changing hardware parameters, scan profiles, or processing
settings should only require editing this file.
"""

from dataclasses import dataclass
from pathlib import Path

# ============================================================
# Directories
# ============================================================

PROJECT_ROOT = Path(__file__).parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
DATABASE_DIR = DATA_DIR / "database"
EXPORT_DIR = DATA_DIR / "exports"

LOG_DIR = PROJECT_ROOT / "logs"
REPORT_DIR = PROJECT_ROOT / "reports"

DATABASE_FILE = DATABASE_DIR / "spectrum.db"


# ============================================================
# SDR Configuration
# ============================================================

@dataclass
class SDRConfig:

    sample_rate: float = 2.048e6

    gain: float | str = "auto"

    fft_size: int = 16384

    overlap: float = 0.2

    dwell_time: float = 0.20

    captures_per_window: int = 5

    merge_distance_hz: float = 2000

    merge_guard_band_hz: float = 2000

    debug_emitter_matching: bool = False

    #
    # Debug
    #

    debug_fixed_frequency: bool = False

    debug_center_frequency: float = 155e6

    debug_windows: int = 100

    debug_candidate_seeds: bool = False
    debug_peak_finder: bool = False
    debug_signal_boundaries: bool = False
    debug_region_merger: bool = False
    debug_emitter_matching: bool = True

    debug_match_lookup: bool = True
    debug_match_rejections: bool = False

# ============================================================
# Scan Profiles
# ============================================================

@dataclass
class ScanProfile:

    name: str

    start_freq: float

    stop_freq: float

    enabled: bool = True


SCAN_PROFILES = {

    "FM_BROADCAST": ScanProfile(
        "FM Broadcast",
        88e6,
        108e6
    ),

    "SERVICE_SCAN": ScanProfile(
        "Scan for Services",
        24e6,
        958e6
    ),

    "FULL_SCAN": ScanProfile(
        "Full RTL Scan",
        24e6,
        1766e6
    )
}


# ============================================================
# Signal Detection
# ============================================================

@dataclass
class DetectionConfig:

    minimum_bandwidth_hz: float = 1000.0

    maximum_gap_bins: int = 2


# ============================================================
# Runtime Configuration Objects
# ============================================================

SDR = SDRConfig()

DETECTION = DetectionConfig()


# ============================================================
# Create Required Directories
# ============================================================

for directory in (
    DATA_DIR,
    RAW_DIR,
    DATABASE_DIR,
    EXPORT_DIR,
    LOG_DIR,
    REPORT_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================
# Scanner Configuration
# ============================================================

@dataclass
class ScannerConfig:

    # Fraction of the sampled bandwidth that is considered usable.
    # We intentionally overlap captures to avoid relying on the
    # less-flat response near the edges.
    usable_bandwidth_fraction: float = 0.80

    # Fractional overlap between adjacent captures.
    overlap_fraction: float = 0.20

    # Pause after each retune (seconds)
    settle_time: float = 0.02


SCANNER = ScannerConfig()
