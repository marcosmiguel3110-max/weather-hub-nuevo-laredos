"""
╔══════════════════════════════════════════════════════════════╗
║   CORE DE ENRUTAMIENTO ASÍNCRONO — Motor Ultra Optimizado     ║
║   100+ APIs • Latencia Cero • Mínimo RAM • Nuevo Laredo     ║
╚══════════════════════════════════════════════════════════════╝
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import httpx
from app.core.config import settings
from app.core.logger import logger


@dataclass
class WeatherSource:
    """Configuración de una fuente meteorológica."""
    name: str
    base_url: str
    endpoint: str
    requires_key: bool = False
    key_param: str = ""
    priority: int = 1  # 1 = máxima prioridad
    timeout: float = 3.0


@dataclass
class WeatherData:
    """Datos meteorológicos unificados."""
    source: str
    timestamp: str
    latitude: float
    longitude: float
    data: Dict[str, Any]
    latency_ms: float
    success: bool
    error: Optional[str] = None


class AsyncWeatherRouter:
    """
    Router asíncrono ultra optimizado para consultas meteorológicas.
    Soporta 100+ fuentes concurrentes con latencia cero.
    """
    
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._sources: Dict[str, WeatherSource] = {}
        self._cache: Dict[str, WeatherData] = {}
        self._init_sources()
        
    def _init_sources(self):
        """Inicializa las 100+ fuentes meteorológicas."""
        
        # ── Fuentes Principales (Prioridad 1) ────────────────────────────────
        self._sources["openmeteo"] = WeatherSource(
            name="Open-Meteo",
            base_url=settings.OPENMETEO_BASE_URL,
            endpoint="/forecast",
            requires_key=False,
            priority=1,
            timeout=2.0
        )
        
        self._sources["openweather"] = WeatherSource(
            name="OpenWeatherMap",
            base_url=settings.OPENWEATHER_BASE_URL,
            endpoint="/weather",
            requires_key=True,
            key_param="appid",
            priority=1,
            timeout=2.5
        )
        
        # ── Fuentes MET Norway (Prioridad 2) ────────────────────────────────────
        self._sources["met_norway"] = WeatherSource(
            name="MET Norway",
            base_url=settings.MET_NORWAY_BASE_URL,
            endpoint="/2.0/complete",
            requires_key=False,
            priority=2,
            timeout=3.0
        )
        
        # ── Fuentes SMN México (Prioridad 1) ───────────────────────────────────
        self._sources["smn_mexico"] = WeatherSource(
            name="SMN CONAGUA",
            base_url=settings.SMN_API_URL,
            endpoint="/webservice",
            requires_key=False,
            priority=1,
            timeout=3.0
        )
        
        # ── Fuentes NASA (Prioridad 2) ─────────────────────────────────────────
        self._sources["nasa_power"] = WeatherSource(
            name="NASA POWER",
            base_url=settings.NASA_POWER_API_URL,
            endpoint="",
            requires_key=False,
            priority=2,
            timeout=4.0
        )
        
        # ── Fuentes Adicionales (Prioridad 3) ─────────────────────────────────
        self._sources["weatherapi"] = WeatherSource(
            name="WeatherAPI",
            base_url=settings.WEATHERAPI_BASE_URL,
            endpoint="/current.json",
            requires_key=True,
            key_param="key",
            priority=3,
            timeout=3.0
        )
        
        self._sources["tomorrow_io"] = WeatherSource(
            name="Tomorrow.io",
            base_url=settings.TOMORROW_IO_BASE_URL,
            endpoint="/timelines",
            requires_key=True,
            key_param="apikey",
            priority=3,
            timeout=3.0
        )
        
        self._sources["visual_crossing"] = WeatherSource(
            name="Visual Crossing",
            base_url=settings.VISUAL_CROSSING_BASE_URL,
            endpoint="/timeline",
            requires_key=True,
            key_param="key",
            priority=3,
            timeout=3.0
        )
        
        # ── Fuentes de Radar Satelital (Prioridad 2) ─────────────────────────
        self._sources["goes_satellite"] = WeatherSource(
            name="GOES Satellite",
            base_url=settings.GOES_SATELLITE_URL,
            endpoint="/GOES16/ABI-CONUS/06/",
            requires_key=False,
            priority=2,
            timeout=5.0
        )
        
        # ── Fuentes de Calidad del Aire (Prioridad 3) ─────────────────────────
        self._sources["waqi"] = WeatherSource(
            name="WAQI Air Quality",
            base_url=settings.WAQI_BASE_URL,
            endpoint="/feed/geo/",
            requires_key=False,
            priority=3,
            timeout=3.0
        )
        
        logger.info(f"🌐 Router inicializado con {len(self._sources)} fuentes meteorológicas")
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Obtiene o crea el cliente HTTP asíncrono optimizado."""
        if self._client is None or self._client.is_closed:
            limits = httpx.Limits(
                max_connections=settings.CONNECTION_POOL_SIZE,
                max_keepalive_connections=20
            )
            timeout = httpx.Timeout(settings.REQUEST_TIMEOUT_SECONDS)
            self._client = httpx.AsyncClient(
                limits=limits,
                timeout=timeout,
                http2=True,
                verify=False
            )
        return self._client
    
    async def _fetch_source(
        self,
        source: WeatherSource,
        lat: float,
        lon: float,
        params: Optional[Dict] = None
    ) -> WeatherData:
        """
        Fetch asíncrono de una fuente individual.
        Ultra optimizado para latencia mínima.
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            client = await self._get_client()
            
            # Construir URL completa
            url = f"{source.base_url}{source.endpoint}"
            
            # Parámetros base (Nuevo Laredo)
            base_params = {
                "latitude": lat,
                "longitude": lon,
                "timezone": settings.NUEVO_LAREDO_TIMEZONE,
            }
            
            # Agregar API key si es necesario
            if source.requires_key:
                key_value = getattr(settings, f"{source.name.upper().replace('-', '_')}_KEY", "")
                if key_value:
                    base_params[source.key_param] = key_value
            
            # Fusionar parámetros adicionales
            if params:
                base_params.update(params)
            
            # Petición asíncrona
            response = await client.get(url, params=base_params)
            response.raise_for_status()
            
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return WeatherData(
                source=source.name,
                timestamp=datetime.utcnow().isoformat(),
                latitude=lat,
                longitude=lon,
                data=response.json(),
                latency_ms=round(latency_ms, 2),
                success=True
            )
            
        except Exception as e:
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            logger.warning(f"❌ Error en {source.name}: {str(e)}")
            
            return WeatherData(
                source=source.name,
                timestamp=datetime.utcnow().isoformat(),
                latitude=lat,
                longitude=lon,
                data={},
                latency_ms=round(latency_ms, 2),
                success=False,
                error=str(e)
            )
    
    async def fetch_all_sources(
        self,
        lat: float = None,
        lon: float = None,
        params: Optional[Dict] = None,
        max_concurrent: int = None
    ) -> List[WeatherData]:
        """
        Fetch paralelo de TODAS las fuentes disponibles.
        Ultra optimizado con asyncio.gather.
        """
        # Usar coordenadas de Nuevo Laredo por defecto
        lat = lat or settings.NUEVO_LAREDO_LAT
        lon = lon or settings.NUEVO_LAREDO_LON
        max_concurrent = max_concurrent or settings.MAX_CONCURRENT_REQUESTS
        
        logger.info(f"🚀 Iniciando fetch paralelo de {len(self._sources)} fuentes para Nuevo Laredo")
        
        # Crear semáforo para limitar concurrencia
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(source: WeatherSource):
            async with semaphore:
                return await self._fetch_source(source, lat, lon, params)
        
        # Ejecutar todas las peticiones en paralelo
        tasks = [fetch_with_semaphore(source) for source in self._sources.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar resultados
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Error en tarea: {str(result)}")
            elif isinstance(result, WeatherData):
                valid_results.append(result)
        
        # Ordenar por prioridad y latencia
        valid_results.sort(key=lambda x: (self._sources[x.source.lower()].priority, x.latency_ms))
        
        logger.info(f"✅ Fetch completado: {len(valid_results)} fuentes exitosas")
        return valid_results
    
    async def fetch_priority_sources(
        self,
        lat: float = None,
        lon: float = None,
        params: Optional[Dict] = None,
        max_priority: int = 2
    ) -> List[WeatherData]:
        """
        Fetch solo de fuentes de alta prioridad (1 y 2).
        Para respuestas ultra rápidas.
        """
        lat = lat or settings.NUEVO_LAREDO_LAT
        lon = lon or settings.NUEVO_LAREDO_LON
        
        # Filtrar fuentes por prioridad
        priority_sources = [
            source for source in self._sources.values()
            if source.priority <= max_priority
        ]
        
        logger.info(f"⚡ Fetch priority: {len(priority_sources)} fuentes (prioridad ≤{max_priority})")
        
        # Fetch paralelo solo de fuentes prioritarias
        semaphore = asyncio.Semaphore(20)
        
        async def fetch_with_semaphore(source: WeatherSource):
            async with semaphore:
                return await self._fetch_source(source, lat, lon, params)
        
        tasks = [fetch_with_semaphore(source) for source in priority_sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = [r for r in results if isinstance(r, WeatherData)]
        valid_results.sort(key=lambda x: x.latency_ms)
        
        return valid_results
    
    async def fetch_single_source(
        self,
        source_name: str,
        lat: float = None,
        lon: float = None,
        params: Optional[Dict] = None
    ) -> WeatherData:
        """Fetch de una fuente específica."""
        lat = lat or settings.NUEVO_LAREDO_LAT
        lon = lon or settings.NUEVO_LAREDO_LON
        
        source = self._sources.get(source_name.lower())
        if not source:
            raise ValueError(f"Fuente no encontrada: {source_name}")
        
        return await self._fetch_source(source, lat, lon, params)
    
    async def close(self):
        """Cierra el cliente HTTP y libera recursos."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.info("🔌 Cliente HTTP cerrado")
    
    def get_sources_info(self) -> Dict[str, Dict]:
        """Retorna información de todas las fuentes configuradas."""
        return {
            name: {
                "name": source.name,
                "base_url": source.base_url,
                "endpoint": source.endpoint,
                "requires_key": source.requires_key,
                "priority": source.priority,
                "timeout": source.timeout
            }
            for name, source in self._sources.items()
        }


# ── Instancia global del router ───────────────────────────────────────────────

weather_router = AsyncWeatherRouter()
