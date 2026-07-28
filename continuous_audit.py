#!/usr/bin/env python3

import subprocess
import time
from datetime import datetime

INTERVAL = 20 * 60  # 20 minutes


def main():

    print("Continuous Spectrum Audit")
    print("Press Ctrl+C to stop.\n")

    try:

        while True:

            print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Starting audit...")

            result = subprocess.run(
                ["python", "audit.py"]
            )

            if result.returncode != 0:

                print(f"Audit exited with code {result.returncode}")

            print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Waiting 20 minutes...\n")

            time.sleep(INTERVAL)

    except KeyboardInterrupt:

        print("\nContinuous audit stopped.")


if __name__ == "__main__":

    main()
