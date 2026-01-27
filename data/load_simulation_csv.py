import csv
from typing import List
from app.schemas import SimulationRow

def load_simulation_data(filename: str = r"C:\Users\lefloyd\simulation-api\data\simulations.csv") -> List[SimulationRow]:
    rows = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(
                SimulationRow(
                    simulation_id=int(row["simulation_id"]),
                    time=float(row["time"]),
                    salinity=float(row["salinity"]),
                    temperature=float(row["temperature"]),
                    u_velocity=float(row["u_velocity"]),
                    v_velocity=float(row["v_velocity"]),
                    water_level=float(row["water_level"])
                )
            )
    print(f"Loaded {len(rows)} rows from {filename}")  # for debugging
    return rows