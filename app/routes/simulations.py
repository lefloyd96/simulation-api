from fastapi import APIRouter
from data.load_simulation_csv import load_simulation_data
from app.schemas import SimulationResponse, SimulationRow

router = APIRouter()

simulation_data = load_simulation_data()

@router.get("/simulations", response_model=SimulationResponse)
def get_simulations(sim_id: int = None):
    if sim_id is not None:
        filtered = [row for row in simulation_data if row.simulation_id == sim_id]
        return {"count": len(filtered), "results": filtered}
    return {"count": len(simulation_data), "results": simulation_data}