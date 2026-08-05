from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.qa.checks import run_all_checks
from app.qa.models import QAReport, Severity
from data.load_simulation_csv import load_simulation_data


def _load_rows_as_dicts():
    return [dict(row) for row in load_simulation_data()]


router = APIRouter(prefix="/qa", tags=["qa"])


@router.get("/report", response_model=QAReport)
def get_qa_report(simulation_id: int = Query(..., description="Simulation run to check")):
    all_rows = _load_rows_as_dicts()
    rows = [r for r in all_rows if r.get("simulation_id") == simulation_id]

    if not rows:
        raise HTTPException(status_code=404, detail=f"No rows found for simulation_id {simulation_id}")

    findings = run_all_checks(rows, simulation_id)
    passed = not any(f.severity == Severity.CRITICAL for f in findings)

    return QAReport(
        simulation_id=simulation_id,
        rows_checked=len(rows),
        findings=findings,
        passed=passed,
    )


@router.get("/report/all", response_model=list[QAReport])
def get_qa_report_all():
    all_rows = _load_rows_as_dicts()
    sim_ids = sorted(set(r.get("simulation_id") for r in all_rows if r.get("simulation_id") is not None))

    reports = []
    for sim_id in sim_ids:
        rows = [r for r in all_rows if r.get("simulation_id") == sim_id]
        findings = run_all_checks(rows, sim_id)
        passed = not any(f.severity == Severity.CRITICAL for f in findings)
        reports.append(QAReport(
            simulation_id=sim_id,
            rows_checked=len(rows),
            findings=findings,
            passed=passed,
        ))
    return reports