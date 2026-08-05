"""
QA / anomaly-detection checks for environmental simulation output.

Each check function takes a list of row dicts for a SINGLE simulation_id,
sorted by time, and returns a list of QAFinding objects. Keep checks
deterministic and explainable — no LLM calls here. This is the part
a consultancy needs to trust.
"""

import statistics
from typing import List, Dict, Any

from app.qa.models import QAFinding, Severity


# ---------------------------------------------------------------------------
# Configuration — tune these against real Delft3D output / site knowledge.
# Treat this as the encoded version of your own modeling judgment.
# ---------------------------------------------------------------------------

PHYSICAL_RANGES = {
    "salinity": (0.0, 40.0),          # psu
    "temperature": (-2.0, 40.0),      # deg C
    "water_level": (-5.0, 5.0),       # m, site-dependent — override per project
    "u_velocity": (-3.0, 3.0),        # m/s, adjust for site
    "v_velocity": (-3.0, 3.0),        # m/s, adjust for site
}

# Max allowed change between consecutive timesteps before flagging a spike.
# Expressed as multiples of the variable's own standard deviation across the run.
SPIKE_STD_MULTIPLIER = {
    "salinity": 4.0,
    "temperature": 4.0,
    "water_level": 4.0,
    "u_velocity": 4.0,
    "v_velocity": 4.0,
}

# Fraction of the run (start/end) used to check for drift / non-convergence
DRIFT_WINDOW_FRACTION = 0.1
DRIFT_THRESHOLD_STD_MULTIPLIER = 2.0

# Velocity magnitude ceiling for a generic coastal/estuarine setting.
MAX_VELOCITY_MAGNITUDE = 3.5  # m/s — override per site


def _mean_std(values: List[float]) -> tuple[float, float]:
    if len(values) < 2:
        return (values[0] if values else 0.0, 0.0)
    return statistics.mean(values), statistics.stdev(values)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_missing_or_null(rows: List[Dict[str, Any]], simulation_id: int) -> List[QAFinding]:
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


def check_physical_ranges(rows: List[Dict[str, Any]], simulation_id: int) -> List[QAFinding]:
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
                    message=f"'{field}' = {val} is outside physically plausible range [{lo}, {hi}] "
                            f"at row_id {row.get('row_id')}",
                    simulation_id=simulation_id,
                    row_id=row.get("row_id"),
                    value=val,
                ))
    return findings


def check_spikes(rows: List[Dict[str, Any]], simulation_id: int) -> List[QAFinding]:
    """Flag sudden discontinuities between consecutive timesteps."""
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
                    message=f"'{field}' jumped by {delta:.3f} between row_id "
                            f"{rows[i-1].get('row_id')} and {rows[i].get('row_id')} "
                            f"(threshold: {threshold:.3f}). Possible instability or bad timestep.",
                    simulation_id=simulation_id,
                    row_id=rows[i].get("row_id"),
                    value=delta,
                    threshold=threshold,
                ))
    return findings


def check_velocity_magnitude(rows: List[Dict[str, Any]], simulation_id: int) -> List[QAFinding]:
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
                message=f"Velocity magnitude {magnitude:.3f} m/s exceeds ceiling "
                        f"{MAX_VELOCITY_MAGNITUDE} m/s at row_id {row.get('row_id')}",
                simulation_id=simulation_id,
                row_id=row.get("row_id"),
                value=magnitude,
                threshold=MAX_VELOCITY_MAGNITUDE,
            ))
    return findings


def check_drift_stability(rows: List[Dict[str, Any]], simulation_id: int) -> List[QAFinding]:
    """
    Compare the start and end windows of the run. A large, unexplained shift
    can indicate the model hasn't reached a stable/expected state, or that
    something diverges rather than settles.
    """
    findings = []
    fields = ["salinity", "temperature", "water_level"]
    n = len(rows)
    window = max(1, int(n * DRIFT_WINDOW_FRACTION))
    if n < window * 2:
        return findings  # run too short to assess drift meaningfully

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
                message=f"'{field}' shifted by {drift:.3f} from start to end of run "
                        f"(threshold: {threshold:.3f}). Confirm this drift is physically "
                        f"expected (e.g. tidal cycle) rather than non-convergence.",
                simulation_id=simulation_id,
                value=drift,
                threshold=threshold,
            ))
    return findings


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

ALL_CHECKS = [
    check_missing_or_null,
    check_physical_ranges,
    check_spikes,
    check_velocity_magnitude,
    check_drift_stability,
]


def run_all_checks(rows: List[Dict[str, Any]], simulation_id: int) -> List[QAFinding]:
    """Run every registered check against one simulation's rows (sorted by time)."""
    sorted_rows = sorted(rows, key=lambda r: r.get("time", 0))
    findings: List[QAFinding] = []
    for check_fn in ALL_CHECKS:
        findings.extend(check_fn(sorted_rows, simulation_id))
    return findings