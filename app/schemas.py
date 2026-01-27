from pydantic import BaseModel
from typing import List

class SimulationRow(BaseModel):
    simulation_id: int
    time: float
    salinity: float
    temperature: float
    u_velocity: float
    v_velocity: float
    water_level: float

class SimulationResponse(BaseModel):
    count: int
    results: List[SimulationRow]