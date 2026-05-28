import time
import gc
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logger import logger
from app.core.security import verify_master_token
from app.core.weather_router import weather_router
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info(f"Weather Hub Nuevo Laredo starting in '{settings.ENVIRONMENT}'...")
        logger.info(f"Location: {settings.NUEVO_LAREDO_LAT}, {settings.NUEVO_LAREDO_LON}")
        logger.info(f"Security: X-Newser-Token activated")
        logger.info(f"RAM mode: {settings.MIN_RAM_MODE}")
        gc.collect()
        logger.info("Weather Hub ready")
        yield
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    finally:
        try:
            logger.info("Closing Weather Hub...")
            await weather_router.close()
            gc.collect()
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

def create_app() -> FastAPI:
    try:
        app = FastAPI(
            title="Weather Hub Nuevo Laredo API",
            description="Open Source weather routing engine. 59 APIs in real-time, master token security, optimized for free hosting. Exclusive focus: Nuevo Laredo, Tamaulipas.",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            lifespan=lifespan,
        )

        app.add_middleware(GZipMiddleware, minimum_size=500)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )

        @app.middleware("http")
        async def security_middleware(request: Request, call_next):
            try:
                public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico", "/sw.js"]
                if request.url.path in public_paths:
                    return await call_next(request)
                await verify_master_token(request)
                return await call_next(request)
            except Exception as e:
                logger.error(f"Security middleware error: {e}")
                raise

        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            try:
                start = time.perf_counter()
                response = await call_next(request)
                elapsed = time.perf_counter() - start
                response.headers["X-Process-Time-Ms"] = f"{elapsed * 1000:.2f}"
                response.headers["X-Powered-By"] = "Weather Hub Nuevo Laredo v2.0"
                return response
            except Exception as e:
                logger.error(f"Process time header error: {e}")
                raise

        @app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            try:
                logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": exc.detail, "status": exc.status_code},
                )
            except Exception as e:
                logger.error(f"HTTP exception handler error: {e}")
                raise
        
        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            try:
                logger.error(f"Unhandled error: {exc}", exc_info=True)
                gc.collect()
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal server error.", "type": type(exc).__name__},
                )
            except Exception as e:
                logger.error(f"Global exception handler error: {e}")
                raise

        app.include_router(api_router, prefix="/v1")

        @app.get("/", tags=["Health"])
        async def root():
            try:
                return {
                    "name": "Weather Hub Nuevo Laredo",
                    "version": "2.0.0",
                    "status": "online",
                    "location": "Nuevo Laredo, Tamaulipas",
                    "coordinates": {
                        "lat": settings.NUEVO_LAREDO_LAT,
                        "lon": settings.NUEVO_LAREDO_LON
                    },
                    "docs": "/docs",
                    "security": "X-Newser-Token required"
                }
            except Exception as e:
                logger.error(f"Root endpoint error: {e}")
                raise

        @app.get("/health", tags=["Health"])
        async def health():
            try:
                return {
                    "status": "ok",
                    "environment": settings.ENVIRONMENT,
                    "ram_mode": "minimal" if settings.MIN_RAM_MODE else "normal",
                    "location": "Nuevo Laredo, Tamaulipas"
                }
            except Exception as e:
                logger.error(f"Health endpoint error: {e}")
                raise

        return app
    except Exception as e:
        logger.error(f"App creation error: {e}")
        raise

app = create_app()
