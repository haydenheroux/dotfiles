#!/usr/bin/env python3
"""Print the CPU temperature and the last idle baseline: "<cur>C (<goal>C)".

The goal is the lowest temperature seen during an idle stretch (CPU busy
below the idle threshold) that lasted at least the minimum idle time. Once
frozen, the goal only changes when a later idle stretch beats (undercuts) it.

Kept deliberately lean: only builtin modules are imported and the resolved
sensor path is cached in the state file so hwmon is not rescanned each run.
"""

import os
import sys
import time

HWMON = "/sys/class/hwmon"
THERMAL = "/sys/class/thermal"
PROC_STAT = "/proc/stat"

# hwmon drivers exposing a CPU package temperature, in order of preference.
CPU_DRIVERS = ("k10temp", "coretemp", "zenpower")
CPU_LABELS = ("Tctl", "Package id 0")

MIN_DELTA_TICKS = 100  # ignore intervals too short to measure

CACHE_HOME = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
STATE_DIR = os.path.join(CACHE_HOME, "dwmblocks")
STATE_PATH = os.path.join(STATE_DIR, "temp")

USAGE = """usage: temp.py [-t PERCENT] [-s SECONDS] [-h]

Print the CPU temperature and the last idle baseline: "<current>C (<goal>C)".

  -t, --threshold PERCENT  busy %% at or below which the CPU counts as idle
                           (default 10, env TEMP_IDLE_THRESHOLD)
  -s, --seconds SECONDS    minimum idle seconds before a baseline freezes
                           (default 120, env TEMP_IDLE_SECONDS)
  -h, --help               show this help
"""


def fail(message):
    print(f"temp.py: {message}", file=sys.stderr)
    print(USAGE, end="", file=sys.stderr)
    raise SystemExit(2)


def parse_args(argv):
    """Resolve the idle threshold and minimum idle seconds (flags > env)."""
    threshold = float(os.environ.get("TEMP_IDLE_THRESHOLD", "10"))
    seconds = float(os.environ.get("TEMP_IDLE_SECONDS", "120"))

    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg in ("-h", "--help"):
            print(USAGE, end="")
            raise SystemExit(0)

        if arg in ("-t", "--threshold"):
            if index + 1 >= len(argv):
                fail(f"option {arg} requires a value")
            index += 1
            value = argv[index]
        elif arg.startswith("--threshold="):
            value = arg.split("=", 1)[1]
        elif arg in ("-s", "--seconds"):
            if index + 1 >= len(argv):
                fail(f"option {arg} requires a value")
            index += 1
            value = argv[index]
        elif arg.startswith("--seconds="):
            value = arg.split("=", 1)[1]
        else:
            fail(f"unknown argument: {arg}")

        try:
            number = float(value)
        except ValueError:
            fail(f"invalid number: {value}")

        if arg in ("-t", "--threshold") or arg.startswith("--threshold="):
            threshold = number
        else:
            seconds = number

        index += 1

    return threshold, seconds


def read_text(path):
    with open(path) as handle:
        return handle.read().strip()


def find_sensor():
    """Locate the sysfs file holding the CPU package temperature."""
    try:
        entries = os.listdir(HWMON)
    except OSError:
        return None

    by_name = {}
    for entry in entries:
        base = os.path.join(HWMON, entry)
        try:
            by_name.setdefault(read_text(os.path.join(base, "name")), base)
        except OSError:
            pass

    for driver in CPU_DRIVERS:
        base = by_name.get(driver)
        if not base:
            continue
        try:
            files = sorted(os.listdir(base))
        except OSError:
            continue
        for name in files:
            if not (name.startswith("temp") and name.endswith("_input")):
                continue
            label = ""
            try:
                label = read_text(os.path.join(base, name[:-6] + "_label"))
            except OSError:
                pass
            if not label or label in CPU_LABELS:
                return os.path.join(base, name)
    return None


def thermal_temp():
    """Fallback: average the ACPI thermal zones."""
    try:
        zones = [z for z in os.listdir(THERMAL) if z.startswith("thermal_zone")]
    except OSError:
        return None
    total = count = 0
    for zone in zones:
        try:
            total += int(read_text(os.path.join(THERMAL, zone, "temp")))
            count += 1
        except (OSError, ValueError):
            pass
    return total / count / 1000.0 if count else None


def cpu_temp(sensor):
    """Return (celsius, sensor_path); path is None for the thermal fallback."""
    if sensor:
        try:
            return int(read_text(sensor)) / 1000.0, sensor
        except (OSError, ValueError):
            pass
    sensor = find_sensor()
    if sensor:
        try:
            return int(read_text(sensor)) / 1000.0, sensor
        except (OSError, ValueError):
            return None, None
    return thermal_temp(), None


def cpu_ticks():
    """Return (idle, total) jiffies from the aggregate cpu line."""
    with open(PROC_STAT) as handle:
        for line in handle:
            if line.startswith("cpu "):
                fields = line.split()[1:9]
                return int(fields[3]) + int(fields[4]), sum(map(int, fields))
    raise RuntimeError("no aggregate cpu line in /proc/stat")


def load_state():
    try:
        with open(STATE_PATH) as handle:
            fields = handle.read().rstrip("\n").split("\t")
    except OSError:
        return {}
    if len(fields) != 7:
        return {}

    def number(value, cast):
        return cast(value) if value else None

    return {
        "sensor": fields[0] or None,
        "goal": number(fields[1], float),
        "run_min": number(fields[2], float),
        "idle_since": number(fields[3], float),
        "busy": fields[4] == "1",
        "idle": int(fields[5]),
        "total": int(fields[6]),
    }


def save_state(state):
    line = "\t".join(
        (
            state["sensor"] or "",
            repr(state["goal"]) if state["goal"] is not None else "",
            repr(state["run_min"]) if state["run_min"] is not None else "",
            repr(state["idle_since"]) if state["idle_since"] is not None else "",
            "1" if state["busy"] else "0",
            str(state["idle"]),
            str(state["total"]),
        )
    )
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(STATE_PATH, "w") as handle:
            handle.write(line)
    except OSError:
        pass


def main():
    idle_threshold, min_idle_seconds = parse_args(sys.argv[1:])

    state = load_state()
    now = time.time()

    temperature, sensor = cpu_temp(state.get("sensor"))
    if temperature is None:
        return
    idle, total = cpu_ticks()

    goal = state.get("goal")
    run_min = state.get("run_min")
    idle_since = state.get("idle_since")
    busy = state.get("busy", False)

    # Average CPU usage over the interval since the previous run.
    is_idle = None
    prev_idle = state.get("idle")
    prev_total = state.get("total")
    if prev_idle is not None and prev_total is not None:
        delta_total = total - prev_total
        if delta_total >= MIN_DELTA_TICKS:
            delta_idle = idle - prev_idle
            is_idle = 100.0 * (1.0 - delta_idle / delta_total) <= idle_threshold

    if is_idle is None:
        # First run, or interval too short: keep the current classification.
        if not busy:
            if idle_since is None:
                idle_since, run_min = now, temperature
            else:
                run_min = min(run_min, temperature)
    elif is_idle:
        if busy or idle_since is None:
            idle_since, run_min = now, temperature
        else:
            run_min = min(run_min, temperature)
        busy = False
    else:
        busy = True
        idle_since = run_min = None

    # Freeze the stretch's minimum once it has been idle long enough, but
    # only if it beats the existing baseline.
    if not busy and idle_since is not None and now - idle_since >= min_idle_seconds:
        if goal is None or run_min < goal:
            goal = run_min

    if goal is None:
        goal = temperature

    save_state(
        {
            "sensor": sensor,
            "goal": goal,
            "run_min": run_min,
            "idle_since": idle_since,
            "busy": busy,
            "idle": idle,
            "total": total,
        }
    )

    print(f"{temperature:.2f}\u00b0C ({goal:.2f}\u00b0C)")


if __name__ == "__main__":
    main()
