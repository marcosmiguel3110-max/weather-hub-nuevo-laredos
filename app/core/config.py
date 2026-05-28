from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "Newser Pro Cloud - Weather Hub Nuevo Laredo"
    ENVIRONMENT: str = "production"
    SECRET_KEY: str = "change-this-in-production-use-openssl-rand-hex-32"
    DEBUG: bool = False

    MASTER_TOKEN: str = "newser_laredo_2026"
    
    CORS_ORIGINS: List[str] = ["*"]

    NUEVO_LAREDO_LAT: float = 27.4775
    NUEVO_LAREDO_LON: float = -99.5252
    NUEVO_LAREDO_TIMEZONE: str = "America/Matamoros"
    NUEVO_LAREDO_ELEVATION: float = 150.0

    OPENMETEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    OPENMETEO_API_KEY: str = "c590c2c3c63610c40669ca16f5397b84"
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    
    MET_NORWAY_BASE_URL: str = "https://api.met.no/weatherapi/locationforecast"
    
    SMN_BASE_URL: str = "https://smn.conagua.gob.mx"
    SMN_API_URL: str = "https://smn.conagua.gob.mx/webservices/index.php"
    
    NASA_POWER_API_URL: str = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    WEATHERAPI_KEY: str = "425e62ddbc30460a8b4135534262004"
    WEATHERAPI_BASE_URL: str = "https://api.weatherapi.com/v1"
    
    ACCUWEATHER_KEY: str = ""
    ACCUWEATHER_BASE_URL: str = "https://dataservice.accuweather.com"
    ACCUWEATHER_LOCATION_KEY: str = ""
    
    TOMORROW_IO_KEY: str = ""
    TOMORROW_IO_BASE_URL: str = "https://api.tomorrow.io/v4"
    
    VISUAL_CROSSING_KEY: str = "Y6TGUGJGC54ZN7Y2EFBSF8PBH"
    VISUAL_CROSSING_BASE_URL: str = "https://weather.visualcrossing.com"
    
    GOES_SATELLITE_URL: str = "https://cdn.star.nesdis.noaa.gov"
    EUMETSAT_URL: str = "https://eumetview.eumetsat.int"
    
    AIR_QUALITY_API_KEY: str = ""
    WAQI_BASE_URL: str = "https://api.waqi.info"
    
    METEOALARM_URL: str = "https://www.meteoalarm.eu"
    
    MAX_CONCURRENT_REQUESTS: int = 50
    REQUEST_TIMEOUT_SECONDS: float = 3.0
    CONNECTION_POOL_SIZE: int = 20
    ENABLE_CACHING: bool = True
    CACHE_TTL_SECONDS: int = 300
    
    MIN_RAM_MODE: bool = True
    MAX_WORKERS: int = 1
    KEEP_ALIVE_TIMEOUT: int = 5
    
    LOG_LEVEL: str = "INFO"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
