Simulation Results API

A lightweight FastAPI backend that serves environmental simulation results from CSV files as a typed, validated JSON API.

This project is designed to be:

Easy to extend with real model outputs (e.g. Delft3D, NetCDF)

Frontend-ready (React, dashboards, data explorers)

Resume- and portfolio-friendly

Features

FastAPI for high-performance REST APIs

Pydantic models for strict typing and validation

CSV-backed data source (simple, transparent, reproducible)

Automatic Swagger documentation (/docs)

Clean, modular project structure

Project Structure
simulation-api/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── schemas.py           # Pydantic response models
│   ├── routes/
│   │   ├── health.py        # Health check endpoint
│   │   └── simulations.py  # Simulation data endpoints
│   └── data/
│       └── load_simulation_csv.py  # CSV loading logic
├── data/
│   └── simulations.csv      # Example simulation dataset
├── README.md
└── environment.yml / requirements.txt (optional)

Running the API (Local)
1. Activate environment
conda activate sim-backend

2. Start the server
uvicorn app.main:app --reload

3. Open the API

Swagger UI: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

API Endpoints
GET /health

Returns service status.

{ "status": "ok" }

GET /simulations

Returns simulation results loaded from a CSV file.

{
  "count": 200,
  "results": [
    {
      "simulation_id": 1,
      "time": 0.0,
      "salinity": 30.0,
      "temperature": 28.3,
      "u_velocity": 0.0,
      "v_velocity": 0.1,
      "water_level": 1.5
    }
  ]
}

GET /simulations/summary

Returns basic statistics across the dataset.

{
  "count": 200,
  "salinity_min": 29.8,
  "salinity_max": 30.4,
  "salinity_mean": 30.1
}

Running with Docker

You can run this API inside a Docker container to ensure a consistent, portable environment.

1. Build the Docker image
docker build -t simulation-api .

2. Run the container
docker run -p 8000:8000 simulation-api


This maps port 8000 inside the container to 8000 on your local machine.

3. Access the API

Open the Swagger UI in your browser:

http://127.0.0.1:8000/docs


Note: The Docker container loads simulation data from data/simulations.csv, which is bundled into the image at build time.

Design Notes

CSV is used as a simple stand-in for real model outputs

Pydantic ensures all numeric fields are correctly typed and validated

The API structure is intentionally generic, making it easy to:

Replace CSV with NetCDF

Add a database

Connect to cloud storage

Support real simulation pipelines

Future Enhancements (Optional)

Filtering by simulation ID or time range

Pagination for large datasets

Upload endpoint for new CSV files

NetCDF ingestion (e.g. Delft3D outputs)

Frontend visualization (React, Plotly, Mapbox)

Author

Built as a learning and portfolio project to demonstrate backend API design for scientific and environmental simulation data.
