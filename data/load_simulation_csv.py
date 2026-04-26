import csv
from typing import List
from app.schemas import SimulationRow

def load_simulation_data(filename: str = "data/simulations.csv") -> List[SimulationRow]:
    rows: List[SimulationRow] = []

    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        # Enumerate adds row_id starting from 1
        for i, row in enumerate(reader, start=1):
            rows.append(
                SimulationRow(
                    row_id=i,  # unique ID per row
                    simulation_id=int(row["simulation_id"]),
                    time=float(row["time"]),
                    salinity=float(row["salinity"]),
                    temperature=float(row["temperature"]),
                    u_velocity=float(row["u_velocity"]),
                    v_velocity=float(row["v_velocity"]),
                    water_level=float(row["water_level"])
                )
            )

    print(f"Loaded {len(rows)} rows from {filename}")  # debug
    return rows