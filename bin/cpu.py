#!/usr/bin/env python3
"""Print CPU usage and active cores: "<percent>% (<active>/<total>)".

Per-core counters are read from /proc/stat and compared against the previous
run's snapshot (cached in the state file), so no sampling sleep is needed.

A core counts as active when its busy share over the interval reaches the
active threshold (default 1%).

Kept deliberately lean: only builtin modules are imported.
"""

import os
import sys

PROC_STAT = "/proc/stat"

CACHE_HOME = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
STATE_DIR = os.path.join(CACHE_HOME, "dwmblocks")
STATE_PATH = os.path.join(STATE_DIR, "cpu")

USAGE = """usage: cpu.py [-a PERCENT] [-h]

Print CPU usage and active cores: "<percent>% (<active>/<total>)".

  -a, --active PERCENT  busy %% for a core to count as active
                        (default 1, env CPU_ACTIVE_THRESHOLD)
  -h, --help            show this help
"""


def fail(message):
    print(f"cpu.py: {message}", file=sys.stderr)
    print(USAGE, end="", file=sys.stderr)
    raise SystemExit(2)


def parse_args(argv):
    active = float(os.environ.get("CPU_ACTIVE_THRESHOLD", "1"))
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg in ("-h", "--help"):
            print(USAGE, end="")
            raise SystemExit(0)
        if arg in ("-a", "--active"):
            if index + 1 >= len(argv):
                fail(f"option {arg} requires a value")
            index += 1
            value = argv[index]
        elif arg.startswith("--active="):
            value = arg.split("=", 1)[1]
        else:
            fail(f"unknown argument: {arg}")
        try:
            active = float(value)
        except ValueError:
            fail(f"invalid number: {value}")
        index += 1
    return active


def read_counters():
    """Return [(idle, total), ...] for the aggregate and every core."""
    counters = []
    with open(PROC_STAT) as handle:
        for line in handle:
            if not line.startswith("cpu"):
                break
            fields = line.split()
            if fields[0] != "cpu" and not fields[0][3:].isdigit():
                continue
            values = list(map(int, fields[1:9]))
            counters.append((values[3] + values[4], sum(values)))
    return counters


def load_state():
    try:
        with open(STATE_PATH) as handle:
            text = handle.read()
    except OSError:
        return []
    try:
        numbers = list(map(int, text.split()))
    except ValueError:
        return []
    return list(zip(numbers[0::2], numbers[1::2]))


def save_state(counters):
    flat = []
    for idle, total in counters:
        flat.append(str(idle))
        flat.append(str(total))
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(STATE_PATH, "w") as handle:
            handle.write("\t".join(flat))
    except OSError:
        pass


def main():
    active_threshold = parse_args(sys.argv[1:])

    counters = read_counters()
    if not counters:
        return

    previous = load_state()
    save_state(counters)

    total_cores = len(counters) - 1  # exclude the aggregate line
    if len(previous) != len(counters):
        print(f"0% (0/{total_cores})")
        return

    delta_idle = counters[0][0] - previous[0][0]
    delta_total = counters[0][1] - previous[0][1]
    if delta_total <= 0:
        print(f"0% (0/{total_cores})")
        return
    usage = 100.0 * (1.0 - delta_idle / delta_total)

    active = 0
    for current, prev in zip(counters[1:], previous[1:]):
        core_total = current[1] - prev[1]
        if core_total <= 0:
            continue
        core_idle = current[0] - prev[0]
        if 100.0 * (1.0 - core_idle / core_total) >= active_threshold:
            active += 1

    print(f"{usage:.0f}% ({active}/{total_cores})")


if __name__ == "__main__":
    main()
