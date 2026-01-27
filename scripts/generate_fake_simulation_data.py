import csv
import math

output_file = "data/simulations.csv"

fieldnames = [
    "simulation_id",
    "time",
    "salinity",
    "temperature",
    "u_velocity",
    "v_velocity",
    "water_level"
]

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for sim_id in [1]:
        for t in range(0, 200):
            writer.writerow({
                "simulation_id": sim_id,
                "time": t,
                "salinity": 30 + 0.5 * math.sin(t / 10),
                "temperature": 28 + 0.3 * math.cos(t / 15),
                "u_velocity": 0.2 * math.sin(t / 5),
                "v_velocity": 0.1 * math.cos(t / 5),
                "water_level": 1.5 + 0.2 * math.sin(t / 12)
            })