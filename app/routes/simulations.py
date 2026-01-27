from fastapi import APIRouter
from data.load_simulation_csv import load_simulation_data
from app.schemas import SimulationResponse, SimulationRow, SimulationSummary

router = APIRouter()

simulation_data = load_simulation_data()

@router.get("/simulations", response_model=SimulationResponse)
def get_simulations(sim_id: int = None):
    if sim_id is not None:
        filtered = [row for row in simulation_data if row.simulation_id == sim_id]
        return {"count": len(filtered), "results": filtered}
    return {"count": len(simulation_data), "results": simulation_data}

@router.get("/simulations/summary", response_model=SimulationSummary)
def get_simulation_summary():
    salinities = [row.salinity for row in simulation_data]

    return {
        "count": len(salinities),
        "salinity_min": min(salinities),
        "salinity_max": max(salinities),
        "salinity_mean": sum(salinities) / len(salinities),
    }