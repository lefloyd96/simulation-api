from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from data.load_simulation_csv import load_simulation_data
from app.schemas import SimulationResponse, SimulationRow, SimulationSummary

router = APIRouter(tags=["Simulations"])

simulation_data = load_simulation_data()

@router.get("/simulations", response_model=SimulationResponse)
def get_simulations(sim_id: Optional[int] = None, row_id: Optional[int] = None):
    """
    Get simulation rows.
    - Can filter by simulation_id
    - Can filter by row_id
    - Can filter by both
    """
    results = simulation_data

    # Filter by simulation_id if provided
    if sim_id is not None:
        results = [row for row in results if row.simulation_id == sim_id]

    # Filter by row_id if provided
    if row_id is not None:
        results = [row for row in results if row.row_id == row_id]

    if row_id is not None and not results:
        raise HTTPException(status_code=404, detail=f"Row {row_id} not found")

    return {"count": len(results), "results": results}

@router.get("/simulations/summary", response_model=SimulationSummary)
def get_simulation_summary(sim_id: Optional[int] = Query(None, description="Filter by simulation/run ID")):
    """
    Returns summary statistics for numeric fields:
    - salinity
    - temperature
    - water_level
    - u_velocity
    - v_velocity
    Can filter by simulation_id if desired.
    """

    # Filter data by sim_id if provided
    data = simulation_data
    if sim_id is not None:
        data = [row for row in data if row.simulation_id == sim_id]

    if not data:
        raise HTTPException(status_code=404, detail="No data found for this simulation_id")

    # Collect each numeric field
    salinities = [row.salinity for row in data]
    temperatures = [row.temperature for row in data]
    water_levels = [row.water_level for row in data]
    u_velocities = [row.u_velocity for row in data]
    v_velocities = [row.v_velocity for row in data]

    # Helper function for min, max, mean
    def summarize(values):
        return {
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values)
        }

    return {
        "count": len(data),
        "salinity": summarize(salinities),
        "temperature": summarize(temperatures),
        "water_level": summarize(water_levels),
        "u_velocity": summarize(u_velocities),
        "v_velocity": summarize(v_velocities)
    }