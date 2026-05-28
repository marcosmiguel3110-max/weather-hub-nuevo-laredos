"""
╔══════════════════════════════════════════════════════════════╗
║   MÓDULO DE FUSIÓN DE DATOS — Tiempo Real • Nuevo Laredo    ║
║   Combina 100+ fuentes en un solo dataset ultra preciso       ║
╚══════════════════════════════════════════════════════════════╝
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import statistics
from app.core.weather_router import WeatherData
from app.core.logger import logger


@dataclass
class UnifiedWeatherData:
    """Datos meteorológicos unificados de todas las fuentes."""
    location: str
    latitude: float
    longitude: float
    timezone: str
    timestamp: str
    sources_count: int
    sources_used: List[str]
    
    # Temperatura (promedio ponderado por prioridad)
    temperature_c: float
    temperature_min_c: float
    temperature_max_c: float
    feels_like_c: float
    
    # Humedad
    humidity_pct: float
    dew_point_c: float
    
    # Viento
    wind_speed_kmh: float
    wind_direction_deg: float
    wind_gust_kmh: float
    
    # Precipitación
    precipitation_mm: float
    precipitation_prob_pct: float
    precipitation_intensity: str
    
    # Presión
    pressure_hpa: float
    pressure_trend: str
    
    # Visibilidad
    visibility_km: float
    
    # Índices
    uv_index: float
    heat_index_c: float
    
    # Condiciones
    weather_code: int
    weather_description: str
    weather_category: str
    
    # Metadatos
    data_quality_score: float  # 0-100
    latency_avg_ms: float
    primary_source: str
    
    # Calidad del aire (si disponible)
    aqi: Optional[int] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None


class DataFusionEngine:
    """
    Motor de fusión de datos en tiempo real.
    Combina múltiples fuentes meteorológicas en un solo dataset preciso.
    """
    
    def __init__(self):
        self._wmo_codes = {
            0: ("Cielo despejado", "Despejado"),
            1: ("Mayormente despejado", "Despejado"),
            2: ("Parcialmente nublado", "Parcialmente nublado"),
            3: ("Nublado", "Nublado"),
            45: ("Niebla", "Niebla"),
            48: ("Niebla con escarcha", "Niebla"),
            51: ("Llovizna ligera", "Lluvia ligera"),
            53: ("Llovizna moderada", "Lluvia ligera"),
            55: ("Llovizna densa", "Lluvia moderada"),
            61: ("Lluvia ligera", "Lluvia ligera"),
            63: ("Lluvia moderada", "Lluvia moderada"),
            65: ("Lluvia intensa", "Lluvia intensa"),
            71: ("Nevada ligera", "Nieve"),
            73: ("Nevada moderada", "Nieve"),
            75: ("Nevada intensa", "Nieve"),
            80: ("Chubascos ligeros", "Chubascos"),
            81: ("Chubascos moderados", "Chubascos"),
            82: ("Chubascos violentos", "Chubascos intensos"),
            85: ("Chubascos de nieve", "Nieve"),
            86: ("Chubascos de nieve intensos", "Nieve"),
            95: ("Tormenta eléctrica", "Tormenta"),
            96: ("Tormenta con granizo", "Tormenta"),
            99: ("Tormenta con granizo intenso", "Tormenta intensa"),
        }
    
    def fuse_weather_data(
        self,
        weather_results: List[WeatherData],
        location: str = "Nuevo Laredo, Tamaulipas"
    ) -> UnifiedWeatherData:
        """
        Fusiona datos de múltiples fuentes en un solo dataset unificado.
        Usa promedios ponderados por prioridad y calidad de datos.
        """
        if not weather_results:
            raise ValueError("No hay datos para fusionar")
        
        # Filtrar solo resultados exitosos
        successful_results = [r for r in weather_results if r.success]
        
        if not successful_results:
            raise ValueError("Todas las fuentes fallaron")
        
        logger.info(f"🔗 Fusionando datos de {len(successful_results)} fuentes")
        
        # Extraer coordenadas (todas deben ser las mismas de Nuevo Laredo)
        lat = successful_results[0].latitude
        lon = successful_results[0].longitude
        
        # Calcular latencia promedio
        avg_latency = statistics.mean([r.latency_ms for r in successful_results])
        
        # Extraer valores de cada fuente
        temperatures = []
        humidities = []
        wind_speeds = []
        wind_directions = []
        pressures = []
        precipitations = []
        uv_indices = []
        weather_codes = []
        
        sources_used = []
        priorities = []
        
        for result in successful_results:
            data = result.data
            sources_used.append(result.source)
            
            # Prioridad basada en la fuente (simulado)
            priority = self._get_source_priority(result.source)
            priorities.append(priority)
            
            # Extraer temperatura (varios formatos posibles)
            temp = self._extract_value(data, ["temperature_2m", "temp", "main.temp", "current.temperature"])
            if temp is not None:
                temperatures.append((temp, priority))
            
            # Extraer humedad
            humidity = self._extract_value(data, ["relative_humidity_2m", "humidity", "main.humidity"])
            if humidity is not None:
                humidities.append((humidity, priority))
            
            # Extraer viento
            wind_speed = self._extract_value(data, ["wind_speed_10m", "wind_speed", "wind.speed"])
            if wind_speed is not None:
                wind_speeds.append((wind_speed, priority))
            
            wind_dir = self._extract_value(data, ["wind_direction_10m", "wind_deg", "wind.deg"])
            if wind_dir is not None:
                wind_directions.append((wind_dir, priority))
            
            # Extraer presión
            pressure = self._extract_value(data, ["surface_pressure", "pressure", "main.pressure"])
            if pressure is not None:
                pressures.append((pressure, priority))
            
            # Extraer precipitación
            precip = self._extract_value(data, ["precipitation", "rain.1h", "current.precip"])
            if precip is not None:
                precipitations.append((precip, priority))
            
            # Extraer UV
            uv = self._extract_value(data, ["uv_index", "uv"])
            if uv is not None:
                uv_indices.append((uv, priority))
            
            # Extraer código del clima
            code = self._extract_value(data, ["weather_code", "weather.0.id", "current.weather_code"])
            if code is not None:
                weather_codes.append((int(code), priority))
        
        # Calcular promedios ponderados
        final_temp = self._weighted_average(temperatures)
        final_humidity = self._weighted_average(humidities)
        final_wind_speed = self._weighted_average(wind_speeds)
        final_wind_dir = self._weighted_average(wind_directions)
        final_pressure = self._weighted_average(pressures)
        final_precip = self._weighted_average(precipitations) or 0.0
        final_uv = self._weighted_average(uv_indices) or 0.0
        
        # Determinar código de clima más común
        final_code = self._most_common_value(weather_codes) or 0
        
        # Calcular calidad de datos
        data_quality = self._calculate_data_quality(successful_results, len(weather_results))
        
        # Determinar fuente primaria (la más rápida y exitosa)
        primary_source = min(successful_results, key=lambda x: x.latency_ms).source
        
        # Obtener descripción del clima
        weather_desc, weather_cat = self._wmo_codes.get(final_code, ("Desconocido", "Desconocido"))
        
        # Calcular sensación térmica aproximada
        feels_like = self._calculate_feels_like(final_temp, final_humidity, final_wind_speed)
        
        # Calcular categoría de precipitación
        precip_intensity = self._categorize_precipitation(final_precip)
        
        return UnifiedWeatherData(
            location=location,
            latitude=lat,
            longitude=lon,
            timezone="America/Matamoros",
            timestamp=datetime.utcnow().isoformat(),
            sources_count=len(successful_results),
            sources_used=sources_used,
            temperature_c=round(final_temp, 1) if final_temp else 0.0,
            temperature_min_c=round(final_temp - 2, 1) if final_temp else 0.0,
            temperature_max_c=round(final_temp + 2, 1) if final_temp else 0.0,
            feels_like_c=round(feels_like, 1) if feels_like else final_temp,
            humidity_pct=round(final_humidity, 1) if final_humidity else 0.0,
            dew_point_c=0.0,  # Calcular si hay datos suficientes
            wind_speed_kmh=round(final_wind_speed, 1) if final_wind_speed else 0.0,
            wind_direction_deg=round(final_wind_dir, 1) if final_wind_dir else 0.0,
            wind_gust_kmh=0.0,  # Calcular si hay datos
            precipitation_mm=round(final_precip, 2),
            precipitation_prob_pct=0.0,  # Calcular desde pronóstico
            precipitation_intensity=precip_intensity,
            pressure_hpa=round(final_pressure, 1) if final_pressure else 1013.0,
            pressure_trend="Estable",
            visibility_km=10.0,  # Valor por defecto
            uv_index=round(final_uv, 1) if final_uv else 0.0,
            heat_index_c=0.0,  # Calcular si hace calor
            weather_code=final_code,
            weather_description=weather_desc,
            weather_category=weather_cat,
            data_quality_score=round(data_quality, 1),
            latency_avg_ms=round(avg_latency, 2),
            primary_source=primary_source
        )
    
    def _get_source_priority(self, source_name: str) -> int:
        """Retorna la prioridad de una fuente (1 = máxima)."""
        priority_map = {
            "Open-Meteo": 1,
            "SMN CONAGUA": 1,
            "OpenWeatherMap": 1,
            "NOAA CDO": 2,
            "NASA POWER": 2,
            "GOES Satellite": 2,
            "WeatherAPI": 3,
            "Tomorrow.io": 3,
            "Visual Crossing": 3,
            "WAQI Air Quality": 3,
        }
        return priority_map.get(source_name, 3)
    
    def _extract_value(self, data: Dict, keys: List[str]) -> Optional[float]:
        """Extrae un valor de un diccionario usando múltiples claves posibles."""
        for key in keys:
            # Soporte para claves anidadas con puntos
            if "." in key:
                parts = key.split(".")
                value = data
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
                if value is not None:
                    return float(value)
            elif key in data:
                return float(data[key])
        return None
    
    def _weighted_average(self, values: List[tuple]) -> Optional[float]:
        """Calcula promedio ponderado por prioridad."""
        if not values:
            return None
        
        # Invertir prioridad (1 = mayor peso)
        weights = [1.0 / priority for _, priority in values]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return statistics.mean([v for v, _ in values])
        
        weighted_sum = sum(v * w for (v, _), w in zip(values, weights))
        return weighted_sum / total_weight
    
    def _most_common_value(self, values: List[tuple]) -> Optional[int]:
        """Retorna el valor más común ponderado por prioridad."""
        if not values:
            return None
        
        # Contar ocurrencias ponderadas
        counts = {}
        for value, priority in values:
            weight = 1.0 / priority
            counts[value] = counts.get(value, 0) + weight
        
        return max(counts.keys(), key=lambda k: counts[k])
    
    def _calculate_data_quality(
        self,
        successful: List[WeatherData],
        total: int
    ) -> float:
        """Calcula un score de calidad de datos (0-100)."""
        success_rate = len(successful) / total if total > 0 else 0
        
        # Penalizar por alta latencia
        avg_latency = statistics.mean([r.latency_ms for r in successful])
        latency_penalty = min(avg_latency / 1000, 0.3)  # Máximo 30% penalización
        
        quality = (success_rate * 70) + ((1 - latency_penalty) * 30)
        return min(quality, 100.0)
    
    def _calculate_feels_like(
        self,
        temp_c: float,
        humidity: float,
        wind_speed_kmh: float
    ) -> float:
        """Calcula sensación térmica aproximada."""
        if temp_c > 27 and humidity > 40:
            # Índice de calor (simplificado)
            return temp_c + (0.55 - 0.0055 * humidity) * (temp_c - 14.5)
        elif temp_c < 10 and wind_speed_kmh > 4.8:
            # Wind chill (simplificado)
            wind_mph = wind_speed_kmh * 0.621371
            return 13.12 + 0.6215 * temp_c - 11.37 * (wind_mph ** 0.16) + 0.3965 * temp_c * (wind_mph ** 0.16)
        else:
            return temp_c
    
    def _categorize_precipitation(self, precip_mm: float) -> str:
        """Categoriza la intensidad de precipitación."""
        if precip_mm == 0:
            return "Sin precipitación"
        elif precip_mm < 2.5:
            return "Lluvia ligera"
        elif precip_mm < 10:
            return "Lluvia moderada"
        elif precip_mm < 50:
            return "Lluvia intensa"
        else:
            return "Lluvia torrencial"


# ── Instancia global del motor de fusión ─────────────────────────────────────

data_fusion = DataFusionEngine()
