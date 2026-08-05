import statistics
from typing import List, Dict, Any

from app.qa.models import QAFinding, Severity

PHYSICAL_RANGES = {
    "salinity": (0.0, 40.0),
    "temperature": (-2.0, 40.0),
    "water_level": (-5.0, 5.0),
    "u_velocity": (-3.0, 3.0),
    "v_velocity": (-3.0, 3.0),
}

SPIKE_STD_MULTIPLIER = {
    "salinity": 4.0,
    "temperature": 4.0,
    "water_level": 4.0,
    "u_velocity": 4.0,
    "v_velocity": 4.0,
}

DRIFT_WINDOW_FRACTION = 0.1
DRIFT_THRESHOLD_STD_MULTIPLIER = 2.0
MAX_VELOCITY_MAGNITUDE = 3.5

# New: how much the spread (std dev) is allowed to grow between the start
# and end windows before we flag it as a possible instability signature.
AMPLITUDE_GROWTH_RATIO_THRESHOLD = 1.75


def _mean_std(values):
    if len(values) < 2:
        return (values[0] if values else 0.0, 0.0)
    return statistics.mean(values), statistics.stdev(values)


def check_missing_or_null(rows, simulation_id):
    findings = []
    fields = ["salinity", "temperature", "water_level", "u_velocity", "v_velocity"]
    for row in rows:
        for field in fields:
            val = row.get(field)
            if val is None:
                findings.append(QAFinding(
                    check_name="missing_data",
                    severity=Severity.CRITICAL,
                    message=f"Missing value for '{field}' at row_id {row.get('row_id')}",
                    simulation_id=simulation_id,
                    row_id=row.get("row_id"),
                ))
    return findings


def check_physical_ranges(rows, simulation_id):
    findings = []
    for row in rows:
        for field, (lo, hi) in PHYSICAL_RANGES.items():
            val = row.get(field)
            if val is None:
                continue
            if val < lo or val > hi:
                findings.append(QAFinding(
                    check_name="physical_range",
                    severity=Severity.CRITICAL,
                    message=f"'{field}' = {val} is outside physically plausible range [{lo}, {hi}] at row_id {row.get('row_id')}",
                    simulation_id=simulation_id,
                    row_id=row.get("row_id"),
                    value=val,
                ))
    return findings


def check_spikes(rows, simulation_id):
    findings = []
    fields = ["salinity", "temperature", "water_level", "u_velocity", "v_velocity"]
    for field in fields:
        series = [r.get(field) for r in rows if r.get(field) is not None]
        if len(series) < 3:
            continue
        _, std = _mean_std(series)
        if std == 0:
            continue
        threshold = SPIKE_STD_MULTIPLIER[field] * std
        for i in range(1, len(rows)):
            prev_val = rows[i - 1].get(field)
            curr_val = rows[i].get(field)
            if prev_val is None or curr_val is None:
                continue
            delta = abs(curr_val - prev_val)
            if delta > threshold:
                findings.append(QAFinding(
                    check_name="spike_discontinuity",
                    severity=Severity.WARNING,
                    message=f"'{field}' jumped by {delta:.3f} between row_id {rows[i-1].get('row_id')} and {rows[i].get('row_id')} (threshold: {threshold:.3f}). Possible instability or bad timestep.",
                    simulation_id=simulation_id,
                    row_id=rows[i].get("row_id"),
                    value=delta,
                    threshold=threshold,
                ))
    return findings


def check_velocity_magnitude(rows, simulation_id):
    findings = []
    for row in rows:
        u = row.get("u_velocity")
        v = row.get("v_velocity")
        if u is None or v is None:
            continue
        magnitude = (u ** 2 + v ** 2) ** 0.5
        if magnitude > MAX_VELOCITY_MAGNITUDE:
            findings.append(QAFinding(
                check_name="velocity_magnitude",
                severity=Severity.WARNING,
                message=f"Velocity magnitude {magnitude:.3f} m/s exceeds ceiling {MAX_VELOCITY_MAGNITUDE} m/s at row_id {row.get('row_id')}",
                simulation_id=simulation_id,
                row_id=row.get("row_id"),
                value=magnitude,
                threshold=MAX_VELOCITY_MAGNITUDE,
            ))
    return findings


def check_drift_stability(rows, simulation_id):
    findings = []
    fields = ["salinity", "temperature", "water_level"]
    n = len(rows)
    window = max(1, int(n * DRIFT_WINDOW_FRACTION))
    if n < window * 2:
        return findings
    for field in fields:
        series = [r.get(field) for r in rows if r.get(field) is not None]
        if len(series) < window * 2:
            continue
        _, std = _mean_std(series)
        if std == 0:
            continue
        start_mean = statistics.mean(series[:window])
        end_mean = statistics.mean(series[-window:])
        drift = abs(end_mean - start_mean)
        threshold = DRIFT_THRESHOLD_STD_MULTIPLIER * std
        if drift > threshold:
            findings.append(QAFinding(
                check_name="drift_stability",
                severity=Severity.INFO,
                message=f"'{field}' shifted by {drift:.3f} from start to end of run (threshold: {threshold:.3f}). Confirm this is physically expected rather than non-convergence.",
                simulation_id=simulation_id,
                value=drift,
                threshold=threshold,
            ))
    return findings


def check_amplitude_growth(rows, simulation_id):
    """
    Compares the SPREAD (std dev) of the start window vs the end window,
    rather than the mean. Catches growing oscillations / diverging runs
    that check_drift_stability misses, since a growing wobble can average
    out to the same mean while its variance still blows up.
    """
    findings = []
    fields = ["salinity", "temperature", "water_level", "u_velocity", "v_velocity"]
    n = len(rows)
    window = max(3, int(n * DRIFT_WINDOW_FRACTION))
    if n < window * 2:
        return findings

    for field in fields:
        series = [r.get(field) for r in rows if r.get(field) is not None]
        if len(series) < window * 2:
            continue

        start_window = series[:window]
        end_window = series[-window:]

        if len(set(start_window)) < 2 or len(set(end_window)) < 2:
            continue  # not enough variation to compute std meaningfully

        start_std = statistics.stdev(start_window)
        end_std = statistics.stdev(end_window)

        if start_std == 0:
            continue  # avoid divide-by-zero; a flat start window with growth is rare but possible — could add a separate absolute check later

        growth_ratio = end_std / start_std

        if growth_ratio > AMPLITUDE_GROWTH_RATIO_THRESHOLD:
            findings.append(QAFinding(
                check_name="amplitude_growth",
                severity=Severity.WARNING,
                message=f"'{field}' variability grew {growth_ratio:.2f}x from start to end of run "
                        f"(start std: {start_std:.3f}, end std: {end_std:.3f}). "
                        f"Possible numerical instability rather than a settling/tidal pattern.",
                simulation_id=simulation_id,
                value=growth_ratio,
                threshold=AMPLITUDE_GROWTH_RATIO_THRESHOLD,
            ))
    return findings


ALL_CHECKS = [
    check_missing_or_null,
    check_physical_ranges,
    check_spikes,
    check_velocity_magnitude,
    check_drift_stability,
    check_amplitude_growth,
]


def run_all_checks(rows, simulation_id):
    sorted_rows = sorted(rows, key=lambda r: r.get("time", 0))
    findings = []
    for check_fn in ALL_CHECKS:
        findings.extend(check_fn(sorted_rows, simulation_id))
    return findings