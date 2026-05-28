"""
API Registry — catálogo de todos los endpoints disponibles y planificados.
Sirve como documentación viva y discovery service.
"""

from fastapi import APIRouter, Query
from typing import List, Optional

router = APIRouter()

# ─── Catálogo maestro ─────────────────────────────────────────────────────────

REGISTRY: List[dict] = [
    # ── Meteorología (activos) ────────────────────────────────────────────
    {"id": "weather.current",      "module": "weather", "status": "active",  "path": "/v1/weather/current"},
    {"id": "weather.forecast",     "module": "weather", "status": "active",  "path": "/v1/weather/forecast"},
    {"id": "weather.bulk",         "module": "weather", "status": "active",  "path": "/v1/weather/bulk"},
    {"id": "weather.nuevo-laredo", "module": "weather", "status": "active",  "path": "/v1/weather/nuevo-laredo"},
    {"id": "weather.alerts",       "module": "weather", "status": "planned", "path": "/v1/weather/alerts"},
    {"id": "weather.historical",   "module": "weather", "status": "planned", "path": "/v1/weather/historical"},
    {"id": "weather.marine",       "module": "weather", "status": "planned", "path": "/v1/weather/marine"},
    {"id": "weather.air-quality",  "module": "weather", "status": "planned", "path": "/v1/weather/air-quality"},
    {"id": "weather.solar",        "module": "weather", "status": "planned", "path": "/v1/weather/solar"},
    {"id": "weather.agriculture",  "module": "weather", "status": "planned", "path": "/v1/weather/agriculture"},
    # ── IA / LLM (activos) ────────────────────────────────────────────────
    {"id": "ai.chat",              "module": "ai",      "status": "active",  "path": "/v1/ai/chat"},
    {"id": "ai.models",            "module": "ai",      "status": "active",  "path": "/v1/ai/models"},
    {"id": "ai.summarize",         "module": "ai",      "status": "planned", "path": "/v1/ai/summarize"},
    {"id": "ai.translate",         "module": "ai",      "status": "planned", "path": "/v1/ai/translate"},
    {"id": "ai.embed",             "module": "ai",      "status": "planned", "path": "/v1/ai/embed"},
    {"id": "ai.rag",               "module": "ai",      "status": "planned", "path": "/v1/ai/rag"},
    # ── Pipeline SDK ──────────────────────────────────────────────────────
    {"id": "pipeline.run",         "module": "pipeline","status": "active",  "path": "/v1/pipeline/run"},
    {"id": "pipeline.tasks",       "module": "pipeline","status": "active",  "path": "/v1/pipeline/tasks"},
    # ── Datos ─────────────────────────────────────────────────────────────
    {"id": "data.ingest",          "module": "data",    "status": "active",  "path": "/v1/data/ingest"},
    {"id": "data.sources",         "module": "data",    "status": "active",  "path": "/v1/data/sources"},
    {"id": "data.query",           "module": "data",    "status": "planned", "path": "/v1/data/query"},
    {"id": "data.export",          "module": "data",    "status": "planned", "path": "/v1/data/export"},
    # ── 80+ APIs planificadas ─────────────────────────────────────────────
    *[
        {"id": f"geo.{name}", "module": "geo", "status": "planned", "path": f"/v1/geo/{name}"}
        for name in ["reverse-geocode", "elevation", "timezone", "boundaries", "municipalities"]
    ],
    *[
        {"id": f"analytics.{name}", "module": "analytics", "status": "planned", "path": f"/v1/analytics/{name}"}
        for name in ["timeseries", "anomaly", "clustering", "correlation", "report"]
    ],
    *[
        {"id": f"notify.{name}", "module": "notify", "status": "planned", "path": f"/v1/notify/{name}"}
        for name in ["email", "sms", "webhook", "push", "alerts"]
    ],
]


@router.get("/", summary="Listar todos los endpoints del ecosistema")
async def list_registry(
    module: Optional[str] = Query(default=None, description="Filtrar por módulo"),
    status: Optional[str] = Query(default=None, description="active | planned"),
):
    results = REGISTRY
    if module:
        results = [r for r in results if r["module"] == module]
    if status:
        results = [r for r in results if r["status"] == status]

    active  = sum(1 for r in REGISTRY if r["status"] == "active")
    planned = sum(1 for r in REGISTRY if r["status"] == "planned")

    return {
        "total": len(REGISTRY),
        "active": active,
        "planned": planned,
        "showing": len(results),
        "apis": results,
    }
