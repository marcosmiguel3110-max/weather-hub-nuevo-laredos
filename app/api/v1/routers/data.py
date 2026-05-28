"""Módulo de ingestión de datos en tiempo real."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, List

router = APIRouter()

class DataPoint(BaseModel):
    source: str
    payload: Dict[str, Any]
    timestamp: str = ""

@router.post("/ingest", summary="Ingerir datos en tiempo real")
async def ingest(point: DataPoint):
    # Aquí conectarías a TimescaleDB / InfluxDB / Supabase
    return {"status": "queued", "source": point.source}

@router.get("/sources", summary="Listar fuentes de datos activas")
async def list_sources():
    return {
        "sources": [
            {"id": "open-meteo",        "type": "meteorológica", "free": True},
            {"id": "openweathermap",     "type": "meteorológica", "free": True},
            {"id": "noaa",              "type": "meteorológica", "free": True},
            {"id": "smn-mexico",        "type": "gubernamental", "free": True},
            {"id": "nasa-power",        "type": "solar/agro",    "free": True},
            {"id": "inegi",             "type": "geodatos MX",   "free": True},
        ]
    }
