from pydantic import BaseModel
from typing import List

class SimulationRow(BaseModel):
    simulation_id: int
    row_id: int
    time: float
    salinity: float
    temperature: float
    u_velocity: float
    v_velocity: float
    water_level: float

class SimulationResponse(BaseModel):
    count: int
    results: List[SimulationRow]
class FieldSummary(BaseModel):
    min: float
    max: float
    mean: float
class SimulationSummary(BaseModel):
    count: int
    salinity: FieldSummary
    temperature: FieldSummary
    water_level: FieldSummary
    u_velocity: FieldSummary
    v_velocity: FieldSummary

class SimulationRunSummary(BaseModel):
    simulation_id: int
    row_count: int

