# app/main.py
from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.simulations import router as sim_router

app = FastAPI(title="Simulation API")

app.include_router(health_router)
app.include_router(sim_router)