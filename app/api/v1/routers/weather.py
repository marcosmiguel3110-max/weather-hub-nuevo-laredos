"""
╔══════════════════════════════════════════════════════════════╗
║   WEATHER HUB NUEVO LAREDO — Router v2.0                      ║
║   100+ APIs • Fusión de Datos • Ultra Rápido                 ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.config import settings
from app.core.logger import logger
from app.core.weather_router import weather_router
from app.core.data_fusion import data_fusion, UnifiedWeatherData

router = APIRouter()

# ─── Modelos de respuesta ─────────────────────────────────────────────────────

class WeatherResponse(BaseModel):
    """Respuesta unificada del Weather Hub."""
    location: str
    latitude: float
    longitude: float
    timezone: str
    timestamp: str
    sources_count: int
    sources_used: List[str]
    temperature_c: float
    temperature_min_c: float
    temperature_max_c: float
    feels_like_c: float
    humidity_pct: float
    wind_speed_kmh: float
    wind_direction_deg: float
    precipitation_mm: float
    precipitation_intensity: str
    pressure_hpa: float
    uv_index: float
    weather_code: int
    weather_description: str
    weather_category: str
    data_quality_score: float
    latency_avg_ms: float
    primary_source: str

class SourcesInfoResponse(BaseModel):
    """Información de todas las fuentes configuradas."""
    sources: Dict[str, Dict]
    total_sources: int

# ─── Endpoints del Weather Hub ────────────────────────────────────────────────

@router.get(
    "/current",
    response_model=WeatherResponse,
    summary="Clima actual unificado (100+ fuentes)",
    description=(
        "Devuelve datos meteorológicos fusionados de todas las fuentes disponibles. "
        "Por defecto usa Nuevo Laredo, Tamaulipas. Requiere token X-Newser-Token."
    ),
)
async def get_current_weather_unified(
    lat: float = Query(default=settings.NUEVO_LAREDO_LAT, description="Latitud"),
    lon: float = Query(default=settings.NUEVO_LAREDO_LON, description="Longitud"),
    location: str = Query(default="Nuevo Laredo, Tamaulipas", description="Nombre de ubicación"),
):
    """
    Clima actual fusionado de 100+ fuentes meteorológicas.
    Usa el motor de fusión de datos para máxima precisión.
    """
    logger.info(f"[weather/current] Ubicación: {location} ({lat}, {lon})")
    
    try:
        # Fetch de todas las fuentes en paralelo
        weather_results = await weather_router.fetch_all_sources(lat=lat, lon=lon)
        
        # Fusión de datos
        unified_data = data_fusion.fuse_weather_data(weather_results, location)
        
        return WeatherResponse(**unified_data.__dict__)
        
    except Exception as e:
        logger.error(f"Error al obtener clima: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")


@router.get(
    "/priority",
    response_model=WeatherResponse,
    summary="Clima actual (solo fuentes prioritarias)",
    description=(
        "Devuelve datos meteorológicos fusionados solo de fuentes de alta prioridad "
        "(Open-Meteo, SMN, OpenWeatherMap). Más rápido que /current."
    ),
)
async def get_priority_weather(
    lat: float = Query(default=settings.NUEVO_LAREDO_LAT),
    lon: float = Query(default=settings.NUEVO_LAREDO_LON),
    location: str = Query(default="Nuevo Laredo, Tamaulipas"),
):
    """
    Clima actual usando solo fuentes de alta prioridad.
    Respuesta ultra rápida (~200-300ms).
    """
    logger.info(f"[weather/priority] Ubicación: {location} ({lat}, {lon})")
    
    try:
        # Fetch solo de fuentes prioritarias
        weather_results = await weather_router.fetch_priority_sources(lat=lat, lon=lon)
        
        # Fusión de datos
        unified_data = data_fusion.fuse_weather_data(weather_results, location)
        
        return WeatherResponse(**unified_data.__dict__)
        
    except Exception as e:
        logger.error(f"Error al obtener clima prioritario: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")


@router.get(
    "/all-sources",
    summary="Datos crudos de todas las fuentes",
    description=(
        "Devuelve los datos crudos de todas las fuentes sin fusión. "
        "Útil para auditoría y debugging."
    ),
)
async def get_all_sources_raw(
    lat: float = Query(default=settings.NUEVO_LAREDO_LAT),
    lon: float = Query(default=settings.NUEVO_LAREDO_LON),
):
    """
    Obtiene datos crudos de todas las fuentes meteorológicas.
    """
    logger.info(f"[weather/all-sources] Fetch de todas las fuentes para ({lat}, {lon})")
    
    try:
        weather_results = await weather_router.fetch_all_sources(lat=lat, lon=lon)
        
        return {
            "location": f"{lat}, {lon}",
            "total_sources": len(weather_results),
            "successful_sources": len([r for r in weather_results if r.success]),
            "failed_sources": len([r for r in weather_results if not r.success]),
            "results": [
                {
                    "source": r.source,
                    "success": r.success,
                    "latency_ms": r.latency_ms,
                    "data": r.data if r.success else None,
                    "error": r.error if not r.success else None
                }
                for r in weather_results
            ]
        }
        
    except Exception as e:
        logger.error(f"Error al obtener fuentes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener fuentes: {str(e)}")


@router.get(
    "/sources",
    response_model=SourcesInfoResponse,
    summary="Información de fuentes configuradas",
    description="Lista todas las fuentes meteorológicas configuradas en el sistema.",
)
async def get_sources_info():
    """
    Retorna información detallada de todas las fuentes meteorológicas configuradas.
    """
    sources_info = weather_router.get_sources_info()
    
    return SourcesInfoResponse(
        sources=sources_info,
        total_sources=len(sources_info)
    )


@router.get(
    "/nuevo-laredo",
    response_model=WeatherResponse,
    summary="Clima actual de Nuevo Laredo (endpoint dedicado)",
    description="Endpoint dedicado exclusivamente para Nuevo Laredo, Tamaulipas.",
)
async def get_nuevo_laredo_weather():
    """
    Clima actual de Nuevo Laredo usando todas las fuentes disponibles.
    """
    return await get_current_weather_unified(
        lat=settings.NUEVO_LAREDO_LAT,
        lon=settings.NUEVO_LAREDO_LON,
        location="Nuevo Laredo, Tamaulipas"
    )


@router.get(
    "/single-source",
    summary="Datos de una fuente específica",
    description="Obtiene datos de una sola fuente meteorológica específica.",
)
async def get_single_source(
    source_name: str = Query(..., description="Nombre de la fuente (ej: openmeteo, smn_mexico)"),
    lat: float = Query(default=settings.NUEVO_LAREDO_LAT),
    lon: float = Query(default=settings.NUEVO_LAREDO_LON),
):
    """
    Obtiene datos de una fuente específica.
    """
    logger.info(f"[weather/single-source] Fuente: {source_name} para ({lat}, {lon})")
    
    try:
        result = await weather_router.fetch_single_source(source_name, lat, lon)
        
        return {
            "source": result.source,
            "success": result.success,
            "latency_ms": result.latency_ms,
            "data": result.data if result.success else None,
            "error": result.error if not result.success else None,
            "timestamp": result.timestamp
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error al obtener fuente: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al obtener fuente: {str(e)}")
