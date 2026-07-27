"""
Quick local test runner — reads a CSV, runs the QA checks, prints results.
Use this to sanity-check the checks BEFORE wiring them into the FastAPI route,
so you're not debugging the API layer and the check logic at the same time.
"""

import csv
import sys

from app.qa.checks import run_all_checks


def load_rows(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {"row_id": int(row["row_id"]), "simulation_id": int(row["simulation_id"])}
            for field in ["time", "salinity", "temperature", "u_velocity", "v_velocity", "water_level"]:
                val = row[field]
                parsed[field] = float(val) if val not in ("", None) else None
            rows.append(parsed)
    return rows


def main(path):
    rows = load_rows(path)
    findings = run_all_checks(rows, simulation_id=rows[0]["simulation_id"])

    print(f"Checked {len(rows)} rows from {path}")
    print(f"Total findings: {len(findings)}\n")

    for f in findings:
        print(f"[{f.severity.value.upper():8}] {f.check_name:20} row_id={f.row_id}  {f.message}")

    if not findings:
        print("No findings — data passed all checks cleanly.")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/simulations_clean.csv"
    main(path)
