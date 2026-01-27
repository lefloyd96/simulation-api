# Simulation Results API

A lightweight **FastAPI** backend that serves environmental simulation results from CSV files as a typed, validated JSON API.

This project is designed to be:

* Easy to extend with real model outputs (e.g. Delft3D, NetCDF)
* Frontend-ready (React, dashboards, data explorers)
* Resume- and portfolio-friendly

---

## Features

* **FastAPI** for high‑performance REST APIs
* **Pydantic** models for strict typing and validation
* **CSV-backed data source** (simple, transparent, reproducible)
* **Automatic Swagger documentation** (`/docs`)
* Clean, modular project structure

---

## Project Structure

```
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
```

---

## Running the API

### 1. Activate environment

```bash
conda activate sim-backend
```

### 2. Start the server

```bash
uvicorn app.main:app --reload
```

### 3. Open the API

* Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## API Endpoints

### `GET /health`

Returns service status.

```json
{ "status": "ok" }
```

---

### `GET /simulations`

Returns simulation results loaded from CSV.

```json
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
```

---

## Design Notes

* CSV is used as a **simple stand‑in for real model outputs**
* Pydantic ensures all numeric fields are correctly typed
* The API design is intentionally generic so that other data sources (NetCDF, databases, cloud storage) can be added later

---

## Future Enhancements (Optional)

* Filtering by simulation ID or time range
* Pagination for large datasets
* Upload endpoint for new CSV files
* NetCDF ingestion (e.g. Delft3D outputs)
* Dockerized deployment
* Frontend visualization (React, Plotly, Mapbox)

---

## Author

Built as a learning and portfolio project to demonstrate backend API design for scientific and environmental data.
