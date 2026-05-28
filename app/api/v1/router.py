"""
Router principal v1 — gestiona todos los módulos.
Diseñado para crecer a 100+ endpoints sin saturar el servidor:
  · Cada módulo es un router independiente con su propio prefijo.
  · Lazy imports: los módulos pesados (IA) solo se cargan si son llamados.
  · Tags automáticos para documentación OpenAPI agrupada.
"""

from fastapi import APIRouter

from app.api.v1.routers.weather   import router as weather_router
from app.api.v1.routers.ai        import router as ai_router
from app.api.v1.routers.pipeline  import router as pipeline_router
from app.api.v1.routers.data      import router as data_router
from app.api.v1.routers.registry  import router as registry_router

api_router = APIRouter()

# ─── Módulos registrados ──────────────────────────────────────────────────────
#
#  Patrón: api_router.include_router(
#      <module>_router,
#      prefix="/<slug>",
#      tags=["<Nombre visible en /docs>"],
#  )
#
#  Para agregar el módulo #101: crea app/api/v1/routers/nuevo.py,
#  define `router = APIRouter()` con tus endpoints y regístralo aquí.
#  CERO cambios en main.py.

api_router.include_router(weather_router,  prefix="/weather",  tags=["🌩️ Meteorología"])
api_router.include_router(ai_router,       prefix="/ai",       tags=["🤖 IA / LLM"])
api_router.include_router(pipeline_router, prefix="/pipeline", tags=["🔗 Pipeline SDK"])
api_router.include_router(data_router,     prefix="/data",     tags=["📊 Datos"])
api_router.include_router(registry_router, prefix="/registry", tags=["📋 API Registry"])
