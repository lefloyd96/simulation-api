from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter(tags=["health"])

DATA_DIR = Path("app/data/simulations")

@router.get("/health/live")
def liveness():
    return {"status": "alive"}

@router.get("/health/ready")
def readiness():
    if not DATA_DIR.exists():
        raise HTTPException(
            status_code=503,
            detail="Simulation data directory not found"
        )

    csv_files = list(DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise HTTPException(
            status_code=503,
            detail="No simulation CSV files available"
        )

    return {
    "status": "ready",
    "csv_count": len(csv_files),
    "data_path": str(DATA_DIR)
}
