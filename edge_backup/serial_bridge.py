
import json
import time

import requests
import serial

# Change COM3 if your ESP32 uses another port.
SERIAL_PORT = "COM3"
BAUD_RATE = 115200
API_URL = "http://127.0.0.1:8000/api/sensor-data"


def main():
    print(f"Connecting to ESP32 on {SERIAL_PORT}...")

    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as esp32:
            # Opening the serial connection may reset the ESP32.
            time.sleep(2)
            print("Serial connected. Waiting for sensor readings...")

            while True:
                line = esp32.readline().decode(
                    "utf-8", errors="replace"
                ).strip()

                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    print("Ignoring non-JSON serial output:", line)
                    continue

                if data.get("type") != "sensor":
                    print("Status:", data)
                    continue

                print("Sensor reading:", data)

                try:
                    response = requests.post(
                        API_URL,
                        json=data,
                        timeout=3,
                    )

                    if response.ok:
                        print("Backend accepted reading:", response.status_code)
                    else:
                        print(
                            "API rejected reading:",
                            response.status_code,
                            response.text[:500],
                        )

                except requests.RequestException as exc:
                    print("Backend connection failed:", exc)

    except serial.SerialException as exc:
        print("Could not open ESP32 serial port:", exc)
        print("Check the COM port and close Arduino Serial Monitor.")


if __name__ == "__main__":
    main()
