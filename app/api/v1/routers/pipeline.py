"""
╔══════════════════════════════════════════════════════════════╗
║   PIPELINE CONNECTOR — Estilo Hugging Face transformers      ║
║                                                              ║
║   Uso desde cualquier app externa:                           ║
║                                                              ║
║   from newser_sdk import NewserPipeline                      ║
║                                                              ║
║   pipe = NewserPipeline(                                     ║
║       task="weather-forecast",                               ║
║       api_key="npc_...",                                     ║
║       base_url="https://tu-app.koyeb.app",                   ║
║   )                                                          ║
║   result = pipe(lat=27.47, lon=-99.51, days=7)               ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from enum import Enum

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logger import logger

router = APIRouter()

# ─── Tareas disponibles ───────────────────────────────────────────────────────

class PipelineTask(str, Enum):
    WEATHER_CURRENT    = "weather-current"
    WEATHER_FORECAST   = "weather-forecast"
    WEATHER_BULK       = "weather-bulk"
    AI_CHAT            = "ai-chat"
    AI_SUMMARIZE       = "ai-summarize"
    DATA_INGEST        = "data-ingest"
    DATA_QUERY         = "data-query"

# ─── Modelos ──────────────────────────────────────────────────────────────────

class PipelineRequest(BaseModel):
    task: PipelineTask = Field(..., description="Tarea a ejecutar")
    inputs: Dict[str, Any] = Field(
        ...,
        description="Parámetros de la tarea (dependen del task)",
        examples=[
            {"lat": 27.4769, "lon": -99.5152, "days": 7},
        ],
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Opciones adicionales: timezone, model, etc.",
    )

class PipelineResponse(BaseModel):
    task: str
    status: str = "ok"
    outputs: Any
    meta: Dict[str, Any] = {}

# ─── Dispatcher ───────────────────────────────────────────────────────────────

async def _dispatch(task: PipelineTask, inputs: Dict, options: Dict) -> Any:
    """
    Enruta la petición del pipeline al módulo correcto.
    Agregar un nuevo task = agregar un case aquí.
    """
    from app.api.v1.routers.weather import (
        fetch_current_openmeteo,
        fetch_forecast_openmeteo,
    )

    tz = options.get("timezone", settings.DEFAULT_TIMEZONE)

    if task == PipelineTask.WEATHER_CURRENT:
        return await fetch_current_openmeteo(
            lat=float(inputs.get("lat", settings.DEFAULT_LAT)),
            lon=float(inputs.get("lon", settings.DEFAULT_LON)),
            timezone=tz,
        )

    elif task == PipelineTask.WEATHER_FORECAST:
        return await fetch_forecast_openmeteo(
            lat=float(inputs.get("lat", settings.DEFAULT_LAT)),
            lon=float(inputs.get("lon", settings.DEFAULT_LON)),
            days=int(inputs.get("days", 7)),
            timezone=tz,
        )

    # ── Placeholder para AI tasks ────────────────────────────────────────────
    elif task == PipelineTask.AI_CHAT:
        return {
            "reply": "[IA no configurada — conecta el módulo AI en app/api/v1/routers/ai.py]",
            "model": inputs.get("model", settings.DEFAULT_MODEL),
        }

    else:
        raise HTTPException(status_code=501, detail=f"Task '{task}' aún no implementado.")


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/run",
    response_model=PipelineResponse,
    summary="Ejecutar cualquier tarea en formato unificado",
    description=(
        "Punto de entrada único tipo transformers-pipeline. "
        "Envía una tarea y sus inputs — el servidor se encarga del resto."
    ),
)
async def run_pipeline(
    request: PipelineRequest,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
):
    logger.info(f"[pipeline/run] task={request.task}")

    # Validación de API key simple (expandir con DB en producción)
    # if x_api_key != settings.SECRET_KEY:
    #     raise HTTPException(status_code=401, detail="API key inválida.")

    options = request.options or {}
    outputs = await _dispatch(request.task, request.inputs, options)

    # Serializar si es un modelo Pydantic
    if hasattr(outputs, "model_dump"):
        outputs = outputs.model_dump()

    return PipelineResponse(
        task=request.task,
        outputs=outputs,
        meta={"version": "1.0.0"},
    )


@router.get(
    "/tasks",
    summary="Listar todas las tareas disponibles",
)
async def list_tasks():
    return {
        "tasks": [t.value for t in PipelineTask],
        "usage": {
            "endpoint": "POST /v1/pipeline/run",
            "body": {
                "task": "weather-forecast",
                "inputs": {"lat": 27.47, "lon": -99.51, "days": 7},
            },
        },
    }
