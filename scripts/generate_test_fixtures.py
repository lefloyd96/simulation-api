"""
Generates two datasets:

1. data/simulations_clean.csv  — same as your original, no faults.
   Running the QA report against this should produce ZERO critical/warning
   findings. If it does flag something, that's a false positive you need
   to fix (probably a threshold that's too tight).

2. data/simulations_faulty.csv — clean data with specific, known faults
   injected at known row_ids. Running the QA report against this should
   catch EXACTLY these faults. If it misses one, that's a false negative
   — the check isn't sensitive enough. If it flags things you didn't
   inject, investigate why (could be legitimate, could be a bug).

Keep a record of what was injected so you can compare against the QA
output directly (see INJECTED_FAULTS at the bottom).
"""

import csv
import math

FIELDNAMES = [
    "row_id",
    "simulation_id",
    "time",
    "salinity",
    "temperature",
    "u_velocity",
    "v_velocity",
    "water_level",
]


def generate_clean_rows(sim_id=1, n_steps=200):
    rows = []
    for t in range(n_steps):
        rows.append({
            "row_id": t + 1,
            "simulation_id": sim_id,
            "time": t,
            "salinity": 30 + 0.5 * math.sin(t / 10),
            "temperature": 28 + 0.3 * math.cos(t / 15),
            "u_velocity": 0.2 * math.sin(t / 5),
            "v_velocity": 0.1 * math.cos(t / 5),
            "water_level": 1.5 + 0.2 * math.sin(t / 12),
        })
    return rows


def inject_faults(rows):
    """
    Injects known faults into a copy of the clean rows.
    Row IDs below correspond to 1-indexed position (row_id == t+1).
    """
    rows = [dict(r) for r in rows]  # deep-ish copy

    # Fault 1: missing value — should trigger check_missing_or_null
    rows[19]["temperature"] = None  # row_id 20

    # Fault 2: physically impossible salinity — should trigger check_physical_ranges
    rows[49]["salinity"] = 55.0  # row_id 50, exceeds 0-40 psu bound

    # Fault 3: sudden velocity spike — should trigger check_spikes AND check_velocity_magnitude
    rows[99]["u_velocity"] = 4.5  # row_id 100, way outside the smooth sine pattern

    # Fault 4: growing oscillation in water_level from t=150 onward —
    # mimics numerical instability (amplitude growth instead of steady tidal cycle).
    # Should trigger check_drift_stability (and possibly check_spikes near the end).
    for i in range(150, 200):
        t = rows[i]["time"]
        growth = (t - 150) * 0.05
        rows[i]["water_level"] = 1.5 + (0.2 + growth) * math.sin(t / 12)

    return rows


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    clean_rows = generate_clean_rows()
    write_csv("data/simulations_clean.csv", clean_rows)

    faulty_rows = inject_faults(clean_rows)
    write_csv("data/simulations_faulty.csv", faulty_rows)

    print("Wrote data/simulations_clean.csv and data/simulations_faulty.csv")
    print()
    print("Injected faults (expected findings):")
    print("  row_id 20  -> missing temperature value")
    print("  row_id 50  -> salinity = 55.0 (out of physical range)")
    print("  row_id 100 -> u_velocity spike to 4.5 m/s")
    print("  row_id 150-200 -> growing water_level oscillation (instability pattern)")