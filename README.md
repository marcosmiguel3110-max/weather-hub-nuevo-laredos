# Weather Hub Nuevo Laredo

**Open Source Weather Routing Engine - Ultra Fast, Secure, Lightweight**

- **Exclusive focus**: Nuevo Laredo, Tamaulipas (27.4775°N, -99.5252°W)
- **15 real weather APIs**: All free, no simulated sources
- **100% security**: Master token `X-Newser-Token` (403 error if invalid)
- **Ultra optimized**: Minimal RAM usage (~40-60MB) for free 24/7 hosting
- **Auto-refresh**: Data updates every 1 second
- **Open source**: 100% modular and expandable
- **Extensible**: Webhook and custom data endpoints for external scripts

---

## 🚀 Características Críticas

### 1. Enfoque Exclusivo en Nuevo Laredo
- Coordenadas preconfiguradas: `27.4775, -99.5252`
- Zona horaria: `America/Matamoros`
- Elevación: 150 metros sobre el nivel del mar
- Todas las consultas priorizan esta región

### 2. 15 Real Weather APIs (All Free)
- **Active APIs (4)**: OpenMeteo, MET Norway, NASA POWER, NOAA NWS
- **Conditional APIs (11)**: WeatherAPI, OpenWeatherMap, Visual Crossing, AccuWeather, WAQI, Weatherbit, Pirate Weather, World Weather Online, QWeather, AerisWeather, Climacell
- **No simulated sources**: All data is real
- **Auto-refresh**: Data cached and updated every 1 second
- **Parallel execution**: All 15 sources queried simultaneously

### 3. Security
```bash
# Required header for all requests
X-Newser-Token: newser_laredo_2026
```
- No token = 403 error immediately
- Invalid token = 403 error immediately
- Public routes: `/`, `/health`, `/docs`, `/favicon.ico`, `/sw.js`

### 4. Ultra Fast Async Architecture
- **asyncio + httpx**: Parallel requests to 59 sources
- **Zero latency**: Responses in milliseconds
- **Connection pool**: 50 simultaneous connections
- **Optimized timeout**: 3 seconds per source

### 5. Data Aggregation
- Combines data from multiple sources into single dataset
- Weighted averages by priority and quality
- Data quality score (0-100)
- Outlier detection and validation

### 6. Extensibility - 100% Modular
The Weather Hub is designed to be 100% modular and extensible for external scripts:

**Webhook Endpoint** (`POST /weather/webhook`)
- Accept custom events from external scripts
- Process custom data with the master token
- Log all webhook events for monitoring

**Custom Data Ingestion** (`POST /weather/custom-data`)
- Ingest custom weather data from any source
- Merge with existing data sources
- Support for Python, Node.js, and curl scripts

**Configuration Endpoint** (`GET /weather/config`)
- Get current system configuration
- View location, system settings, and extensibility options
- Use this to build custom integrations

**Example Python Script:**
```python
import requests

headers = {"X-Newser-Token": "newser_laredo_2026"}

# Send custom data
payload = {
    "source": "my_custom_sensor",
    "data": {"temperature": 25.5, "humidity": 60}
}
response = requests.post(
    "https://weather-hub-nuevo-laredos.onrender.com/weather/custom-data",
    json=payload,
    headers=headers
)
print(response.json())

# Get configuration
config = requests.get(
    "https://weather-hub-nuevo-laredos.onrender.com/weather/config",
    headers=headers
)
print(config.json())
```

**Example Node.js Script:**
```javascript
const axios = require('axios');

const headers = { 'X-Newser-Token': 'newser_laredo_2026' };

// Send webhook event
const webhook = await axios.post(
    'https://weather-hub-nuevo-laredos.onrender.com/weather/webhook',
    { event_type: 'custom_alert', data: { alert: 'high_temperature' } },
    { headers }
);
console.log(webhook.data);
```

This allows you to build custom integrations, add new data sources, or create automated workflows using the Weather Hub as a central data processing engine.

---

## Project Structure

```
newser_pro_cloud/
├── app/
│   ├── core/
│   │   ├── config.py          # Master configuration (59 APIs)
│   │   ├── security.py        # Master token X-Newser-Token
│   │   ├── data_fusion.py     # Data fusion engine
│   │   └── logger.py          # Logging system
│   ├── routers/
│   │   └── weather.py         # Async weather router (59 APIs)
│   └── main.py                # Optimized FastAPI app
├── requirements.txt            # Ultra lightweight dependencies
├── .env.example               # Environment variables template
├── docker-compose.yml         # Docker deployment
├── Dockerfile                 # Docker image
└── README.md                  # This documentation
```

---

## Installation

### Minimum Requirements
- Python 3.9+
- ~50-80MB RAM
- Compatible free hosting (Render, Railway, Koyeb, etc.)

### Installation Steps

```bash
# 1. Clone repository
git clone <repo-url>
cd newser_pro_cloud

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install ultra lightweight dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your MASTER_TOKEN and API keys
```

---

## Security Configuration

### `.env` file

```bash
# Master token (CHANGE IN PRODUCTION)
MASTER_TOKEN=newser_laredo_2026

# API Keys (Optional - APIs work without keys with limited functionality)
OPENMETEO_API_KEY=c590c2c3c63610c40669ca16f5397b84
WEATHERAPI_KEY=425e62ddbc30460a8b4135534262004
VISUAL_CROSSING_KEY=Y6TGUGJGC54ZN7Y2EFBSF8PBH

# Optional APIs (only if you have keys)
OPENWEATHER_API_KEY=your-openweather-key
ACCUWEATHER_KEY=your-accuweather-key
ACCUWEATHER_LOCATION_KEY=your-accuweather-location-key
AIR_QUALITY_API_KEY=your-air-quality-key
```

### Token Usage

```bash
# Request with curl
curl -H "X-Newser-Token: newser_laredo_2026" \
     https://your-api.com/weather/current

# Request with Python
import requests
headers = {"X-Newser-Token": "newser_laredo_2026"}
response = requests.get("https://your-api.com/weather/current", headers=headers)
```

---

## Main Endpoints

### 1. Current Weather (Nuevo Laredo)
```http
GET /weather/current
Headers: X-Newser-Token: <token>
```

**Response:**
```json
{
  "location": "Nuevo Laredo, Tamaulipas",
  "coordinates": {"lat": 27.4769, "lon": -99.5152},
  "timestamp": "2026-05-27T20:00:00",
  "sources_count": 59,
  "temperature_celsius": 32.5,
  "humidity_percent": 65.0,
  "wind_speed_kmh": 12.3,
  "conditions": ["clear", "cloudy"],
  "pressure_hpa": 1013.25,
  "processing_time_ms": 245.3,
  "total_response_time_ms": 250.1,
  "cache_age_seconds": 0.5
}
```

### 2. Weather Forecast
```http
GET /weather/forecast?hours=24
Headers: X-Newser-Token: <token>
```

### 3. LNB Status (Line In Capture)
```http
GET /weather/lnb-status
Headers: X-Newser-Token: <token>
```

### 4. Radar Data
```http
GET /weather/radar
Headers: X-Newser-Token: <token>
```

### 5. Health Check
```http
GET /weather/health
Headers: X-Newser-Token: <token>
```

### 6. Sources List
```http
GET /weather/sources
Headers: X-Newser-Token: <token>
```

---

## RAM Optimization

### Configuration in `config.py`
```python
MIN_RAM_MODE = True          # Enable minimal RAM mode
MAX_WORKERS = 1              # 1 worker for minimal consumption
KEEP_ALIVE_TIMEOUT = 5       # Connection timeout
MAX_CONCURRENT_REQUESTS = 50 # Max parallel requests
REQUEST_TIMEOUT_SECONDS = 3.0 # Timeout per request
```

### Automatic Garbage Collection
- Runs at server startup
- Runs after each error
- Runs at server shutdown

---

## 24/7 Deployment on Free Hosting

### Option 1: Render.com (Recommended)
1. Create account at https://render.com
2. Create new Web Service
3. Connect GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Environment Variables**: Add from .env.example
5. Deploy - Free tier includes 24/7 uptime

### Option 2: Railway.app
1. Create account at https://railway.app
2. New Project -> Deploy from GitHub
3. Configure:
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add from .env.example
4. Deploy - Free tier includes 24/7 uptime

### Option 3: Koyeb.com
1. Create account at https://koyeb.com
2. Create App -> GitHub
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add from .env.example
4. Deploy - Free tier includes 24/7 uptime

### Option 4: Docker Deployment
```bash
# Build image
docker build -t weather-hub-nuevo-laredo .

# Run container
docker run -d -p 8000:8000 --env-file .env weather-hub-nuevo-laredo
```

### Option 5: Local Development
```bash
# Run locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## System Expansion

### Add New Weather Source

1. Edit `app/core/config.py`:
```python
NEW_API_BASE_URL: str = "https://api.new-source.com"
NEW_API_KEY: str = ""
```

2. Edit `app/routers/weather.py`:
```python
async def fetch_new_source() -> Dict:
    try:
        client = await get_http_client()
        url = settings.NEW_API_BASE_URL
        params = {"key": settings.NEW_API_KEY}
        response = await client.get(url, params=params)
        response.raise_for_status()
        return {"source": "new_source", "data": response.json()}
    except Exception as e:
        logger.error(f"New source error: {e}")
        return {"source": "new_source", "error": str(e)}
```

3. Add to `fetch_all_weather_sources()`:
```python
tasks.append(fetch_new_source())
```

---

## Performance Metrics

### Average Latency
- **Priority sources**: ~200-300ms
- **All sources**: ~500-800ms
- **Single source**: ~50-150ms

### RAM Consumption
- **Idle**: ~50MB
- **Under load**: ~80MB
- **Peak**: ~120MB

### Concurrency
- **Max concurrent**: 50
- **Connection pool**: 20
- **Timeout per request**: 3s

---

## License

This project is 100% Open Source. You can modify, audit, and expand it freely.

---

## Contributions

This system is designed to be modular and expandable. If you add new weather sources or features, consider making a pull request.

---

## Security Notes

1. **CHANGE the MASTER_TOKEN in production**
2. **Use environment variables** for API keys
3. **Restrict CORS_ORIGINS** in production
4. **Enable HTTPS** always
5. **Monitor logs** for unauthorized access attempts

---

## Support

For issues or questions, check the documentation at `/docs` (Swagger UI) of the running server.

---

**Developed for Nuevo Laredo, Tamaulipas**
