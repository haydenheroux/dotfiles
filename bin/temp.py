#!/usr/bin/env python3

def read_int(path: str) -> int:
    with open(path) as file:
        content = file.read().strip()
        return int(content)


def main() -> None:
    measurements = [
        read_int(f"/sys/class/thermal/thermal_zone{n}/temp") for n in range(0, 4)
    ]
    if measurements:
        average_measurement = sum(measurements) / len(measurements)
        temperature_celsius = average_measurement / 1000
        print(f"{temperature_celsius:.2f}°C")


if __name__ == "__main__":
    main()
