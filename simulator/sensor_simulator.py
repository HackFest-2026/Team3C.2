import argparse
import random
import time
from datetime import datetime, timezone

import requests


API_URL = "http://127.0.0.1:8000/api/sensor-data"


SCENARIOS = {
    "normal": {
        "gas": (150, 300),
        "temperature": (25, 32),
        "distance": (60, 120),
        "vibration": (5, 20),
    },
    "gas_leak": {
        "gas": (700, 950),
        "temperature": (28, 38),
        "distance": (60, 120),
        "vibration": (5, 25),
    },
    "structural_hazard": {
        "gas": (150, 350),
        "temperature": (28, 40),
        "distance": (10, 30),
        "vibration": (65, 95),
    },
    "critical": {
        "gas": (800, 1000),
        "temperature": (50, 70),
        "distance": (10, 25),
        "vibration": (70, 100),
    },
}


def generate_sensor_data(scenario: str) -> dict:
    values = SCENARIOS[scenario]

    return {
        "device_id": "MINE-EDGE-01",
        "zone": "ZONE-A",
        "gas": round(random.uniform(*values["gas"]), 2),
        "temperature": round(random.uniform(*values["temperature"]), 2),
        "distance": round(random.uniform(*values["distance"]), 2),
        "vibration": round(random.uniform(*values["vibration"]), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def send_sensor_data(data: dict) -> None:
    try:
        response = requests.post(
            API_URL,
            json=data,
            timeout=5,
        )

        if response.status_code == 200:
            print(
                f"[SENT] "
                f"Gas={data['gas']:.1f} | "
                f"Temp={data['temperature']:.1f}°C | "
                f"Distance={data['distance']:.1f}cm | "
                f"Vibration={data['vibration']:.1f}"
            )
        else:
            print(
                f"[ERROR] Backend returned "
                f"HTTP {response.status_code}: {response.text}"
            )

    except requests.exceptions.RequestException as error:
        print(f"[ERROR] Could not connect to backend: {error}")


def main():
    parser = argparse.ArgumentParser(
        description="Mine Safety sensor simulator"
    )

    parser.add_argument(
        "--scenario",
        choices=SCENARIOS.keys(),
        default="normal",
        help="Sensor scenario to simulate",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=2,
        help="Seconds between sensor readings",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("       MINE SAFETY SENSOR SIMULATOR")
    print("=" * 60)
    print(f"Scenario : {args.scenario}")
    print(f"Interval : {args.interval} seconds")
    print(f"Backend  : {API_URL}")
    print("=" * 60)
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            sensor_data = generate_sensor_data(args.scenario)
            send_sensor_data(sensor_data)
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")


if __name__ == "__main__":
    main()