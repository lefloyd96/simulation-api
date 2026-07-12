from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)

MOCK_AI = os.getenv("MOCK_AI", "true").lower() == "true"


class SimulationInterpretRequest(BaseModel):
    salinity: float
    temperature: float
    water_level: float
    u_velocity: float
    v_velocity: float


class SimulationInterpretResponse(BaseModel):
    interpretation: str


@router.post("/interpret", response_model=SimulationInterpretResponse)
def interpret_simulation(data: SimulationInterpretRequest):
    """
    Generate a plain-English interpretation of simulation values.
    """

    prompt = f"""
Interpret these environmental simulation values in clear, non-technical language.

Salinity: {data.salinity}
Temperature: {data.temperature}
Water level: {data.water_level}
U velocity: {data.u_velocity}
V velocity: {data.v_velocity}

Keep the response concise and avoid overstating certainty.
"""

    # Local development mode
    if MOCK_AI:
        return SimulationInterpretResponse(
            interpretation=(
                "Mock interpretation: The simulation values suggest generally stable "
                "coastal water conditions. Salinity and temperature are within a typical "
                "range, while the velocity components indicate relatively weak flow. "
                "Further review would depend on site-specific thresholds and model context."
            )
        )

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured."
        )

    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        return SimulationInterpretResponse(
            interpretation=response.output_text
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AI interpretation failed: {error}"
        )