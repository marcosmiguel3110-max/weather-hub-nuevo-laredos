# 🌩️ Newser Pro Cloud — Guía de Despliegue Gratuito 24/7
## Para Nuevo Laredo, Tamaulipas y el mundo

---

## ⚡ RESUMEN: Stack 100% Gratuito Recomendado

| Componente       | Servicio         | Plan Gratis                  | Requiere tarjeta |
|------------------|------------------|------------------------------|------------------|
| API Server       | **Koyeb**        | 1 instancia permanente       | ❌ No            |
| Base de datos    | **Supabase**     | 500 MB PostgreSQL            | ❌ No            |
| Cache Redis      | **Upstash**      | 256 MB Redis serverless      | ❌ No            |
| Object Storage   | **Cloudflare R2**| 10 GB/mes gratis             | ✅ Sí (sin cobro)|
| Modelos IA       | **HF Spaces**    | CPU gratuito permanente      | ❌ No            |
| Dominio HTTPS    | Incluido en todos| SSL automático               | ❌ No            |

---

## 🟢 OPCIÓN 1: Koyeb (Recomendado — más simple, permanente)

### Pasos

```bash
# 1. Crea cuenta en https://koyeb.com — NO pide tarjeta

# 2. Instala la CLI de Koyeb (opcional, también puedes usar el dashboard web)
curl -fsSL https://cli.koyeb.com/install.sh | bash

# 3. Conecta tu cuenta
koyeb login

# 4. Clona o sube tu proyecto a GitHub

# 5. Despliega desde GitHub (el método más fácil)
#    En el dashboard de Koyeb:
#    New App → Deploy from GitHub → selecciona tu repo
#    Build method: Dockerfile
#    Port: 8000
#    Health check: /health
```

### Variables de entorno en Koyeb
En el dashboard → tu app → Settings → Environment Variables, agrega:
```
ENVIRONMENT=production
SECRET_KEY=<genera-uno-con: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=<tu-url-de-supabase>
OPENMETEO_BASE_URL=https://api.open-meteo.com/v1
DEFAULT_LAT=27.4769
DEFAULT_LON=-99.5152
DEFAULT_TIMEZONE=America/Matamoros
```

### Tu URL pública
Koyeb te da automáticamente:
`https://newser-pro-cloud-<tuusuario>.koyeb.app`

---

## 🟣 OPCIÓN 2: Hugging Face Spaces (Para módulo IA)

```bash
# 1. Crea cuenta en https://huggingface.co

# 2. New Space → SDK: Docker → Hardware: CPU Basic (gratis)

# 3. Crea app.py en la raíz (HF espera este archivo)
# El Dockerfile ya está listo, solo agrega este archivo:
```

```python
# app.py (solo necesario para HF Spaces)
import subprocess
subprocess.run(["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"])
```

```bash
# 4. En README.md del Space agrega:
# ---
# title: Newser Pro Cloud
# sdk: docker
# app_port: 7860
# ---

# 5. git push → HF construye y despliega automáticamente
```

---

## 🔵 OPCIÓN 3: Render (Alternativa con sleep en capa gratis)

> ⚠️ Render pone en "sleep" apps inactivas en el plan gratuito.
> Para que estén 24/7, necesitas un ping cada 14 minutos.
> Usa https://cron-job.org (gratis) para hacerlo.

```bash
# render.yaml (crea este archivo en la raíz)
```

```yaml
services:
  - type: web
    name: newser-pro-cloud
    runtime: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: DEFAULT_LAT
        value: "27.4769"
      - key: DEFAULT_LON
        value: "-99.5152"
    healthCheckPath: /health
```

---

## 🗄️ Configurar Supabase (Base de datos gratuita)

```bash
# 1. Crea cuenta en https://supabase.com — sin tarjeta
# 2. New Project → elige región: us-east-1 (más cercana a Nuevo Laredo)
# 3. Settings → Database → Connection String → URI (Transaction Pooler)
#    postgresql+asyncpg://postgres.<ref>:<password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres
# 4. Copia la URL completa y ponla en DATABASE_URL de tu hosting
```

---

## ⚡ Configurar Upstash Redis (Cache gratuita)

```bash
# 1. https://upstash.com → Create Database
# 2. Tipo: Redis, Región: us-east-1
# 3. Copia la URL: rediss://:<password>@<host>.upstash.io:6379
# 4. Ponla en REDIS_URL de tu hosting
```

---

## 🧪 Probar localmente antes de desplegar

```bash
# Clonar / entrar al proyecto
cd newser_pro_cloud

# Crear entorno virtual
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt

# Copiar configuración
cp .env.example .env
# Editar .env con tus valores

# Crear __init__.py vacíos necesarios
touch app/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/api/v1/routers/__init__.py
touch app/core/__init__.py
touch app/modules/__init__.py

# Arrancar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Abrir en navegador:
# http://localhost:8000/docs       ← Documentación interactiva
# http://localhost:8000/health     ← Health check
# http://localhost:8000/v1/weather/nuevo-laredo ← Clima Nuevo Laredo
```

---

## 📡 Probar la API con curl

```bash
# Clima actual Nuevo Laredo
curl "http://localhost:8000/v1/weather/nuevo-laredo"

# Pronóstico 7 días
curl "http://localhost:8000/v1/weather/forecast?lat=27.4769&lon=-99.5152&days=7"

# Pipeline unificado (estilo Hugging Face)
curl -X POST "http://localhost:8000/v1/pipeline/run" \
  -H "Content-Type: application/json" \
  -d '{"task":"weather-forecast","inputs":{"lat":27.4769,"lon":-99.5152,"days":3}}'

# Registry de todas las APIs
curl "http://localhost:8000/v1/registry/"
```

---

## 🐍 Usar el SDK Python desde otra app

```python
# En otra aplicación (o notebook Jupyter):
# pip install requests

from newser_sdk import NewserPipeline

# Conectar al servidor (local o en la nube)
pipe = NewserPipeline(
    task="weather-forecast",
    base_url="https://newser-pro-cloud-tuusuario.koyeb.app",
)

# Verificar que el servidor está vivo
print(pipe.health())

# Pronóstico para Nuevo Laredo
forecast = pipe(lat=27.4769, lon=-99.5152, days=7)
print(forecast)

# Clima actual para cualquier ciudad
monterrey = pipe.weather(lat=25.6866, lon=-100.3161)
print(monterrey)

# Chat con LLM (cuando configures HF_TOKEN)
respuesta = pipe.chat([
    {"role": "user", "content": "¿Cómo interpreto el índice UV de 8?"}
])
print(respuesta)
```

---

## 🗂️ Estructura final del proyecto

```
newser_pro_cloud/
├── app/
│   ├── main.py                   ← Entrada principal FastAPI
│   ├── core/
│   │   ├── config.py             ← Configuración central
│   │   └── logger.py             ← Logger estructurado
│   ├── api/
│   │   └── v1/
│   │       ├── router.py         ← Router maestro (registra todos los módulos)
│   │       └── routers/
│   │           ├── weather.py    ← 🌩️ Meteorología (ACTIVO)
│   │           ├── ai.py         ← 🤖 IA / LLM (ACTIVO)
│   │           ├── pipeline.py   ← 🔗 SDK Pipeline (ACTIVO)
│   │           ├── data.py       ← 📊 Datos (ACTIVO)
│   │           └── registry.py   ← 📋 Catálogo de APIs (ACTIVO)
│   └── modules/                  ← Lógica de negocio reutilizable
├── newser_sdk.py                 ← SDK Python para desarrolladores externos
├── requirements.txt
├── Dockerfile
├── .env.example
└── DEPLOYMENT.md                 ← Este archivo
```

---

## 🚀 Roadmap de expansión (próximos módulos)

### Fase 2 (mes 1-2)
- [ ] `weather.py` → agregar datos históricos desde ERA5
- [ ] `weather.py` → alertas tempranas (SMN CONAGUA)
- [ ] `data.py` → TimescaleDB para series de tiempo
- [ ] Auth con API keys en base de datos

### Fase 3 (mes 3-4)
- [ ] Módulo `analytics.py` → detección de anomalías climáticas
- [ ] Módulo `geo.py` → geocodificación inversa (lat/lon → municipio)
- [ ] WebSockets para datos en tiempo real

### Fase 4 (mes 5-6)
- [ ] Modelo GLM ligero en producción (Qwen 1.5B cuantizado)
- [ ] RAG meteorológico (pregunta en español → datos del clima)
- [ ] Dashboard de monitoreo (Grafana Cloud gratuito)
