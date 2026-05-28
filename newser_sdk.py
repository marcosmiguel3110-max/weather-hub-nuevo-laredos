"""
╔══════════════════════════════════════════════════════════════╗
║   NewserPipeline SDK — Cliente Python para desarrolladores   ║
║                                                              ║
║   Uso:                                                       ║
║     pip install requests                                     ║
║                                                              ║
║     from newser_sdk import NewserPipeline                    ║
║                                                              ║
║     # Conexión (igual que transformers de Hugging Face)      ║
║     pipe = NewserPipeline(                                   ║
║         task="weather-forecast",                             ║
║         base_url="https://tu-app.koyeb.app",                 ║
║         api_key="opcional",                                  ║
║     )                                                        ║
║                                                              ║
║     # Llamada simple                                         ║
║     resultado = pipe(lat=27.47, lon=-99.51, days=7)          ║
║                                                              ║
║     # O estilo keyword                                       ║
║     clima_actual = pipe.run(                                 ║
║         task="weather-current",                              ║
║         lat=27.4769, lon=-99.5152                            ║
║     )                                                        ║
╚══════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

try:
    import requests
except ImportError:
    raise ImportError("Instala el SDK con: pip install requests")


class NewserPipelineError(Exception):
    """Error al comunicarse con Newser Pro Cloud."""


class NewserPipeline:
    """
    Cliente unificado para Newser Pro Cloud.
    Funciona de manera análoga a `transformers.pipeline()` de Hugging Face:

        pipe = NewserPipeline(task="weather-forecast", base_url="...")
        result = pipe(lat=27.47, lon=-99.51, days=7)
    """

    def __init__(
        self,
        task: Optional[str] = None,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        self.task     = task
        self.base_url = base_url.rstrip("/")
        self.api_key  = api_key
        self.timeout  = timeout
        self._session = requests.Session()
        if api_key:
            self._session.headers.update({"X-API-Key": api_key})
        self._session.headers.update({"Content-Type": "application/json"})

    # ── Llamada directa: pipe(lat=27.47, ...) ────────────────────────────────

    def __call__(self, **inputs: Any) -> Any:
        if not self.task:
            raise NewserPipelineError("Especifica `task` al crear el pipeline.")
        return self.run(task=self.task, **inputs)

    # ── API pública ───────────────────────────────────────────────────────────

    def run(self, task: str, options: Optional[Dict] = None, **inputs: Any) -> Any:
        """Ejecuta cualquier tarea en el servidor."""
        payload = {"task": task, "inputs": inputs}
        if options:
            payload["options"] = options
        return self._post("/v1/pipeline/run", payload)

    def weather(
        self,
        lat: float,
        lon: float,
        days: int = 1,
        timezone: str = "auto",
    ) -> Dict:
        """Atajo para pronóstico meteorológico."""
        task = "weather-forecast" if days > 1 else "weather-current"
        return self.run(task=task, lat=lat, lon=lon, days=days,
                        options={"timezone": timezone})

    def chat(self, messages: list, model: Optional[str] = None, **kwargs) -> Dict:
        """Atajo para chat con LLM."""
        inputs: Dict[str, Any] = {"messages": messages}
        if model:
            inputs["model"] = model
        inputs.update(kwargs)
        return self.run(task="ai-chat", **inputs)

    def available_tasks(self) -> list:
        """Lista las tareas disponibles en el servidor."""
        resp = self._session.get(f"{self.base_url}/v1/pipeline/tasks",
                                 timeout=self.timeout)
        resp.raise_for_status()
        return resp.json().get("tasks", [])

    def health(self) -> Dict:
        """Verifica que el servidor esté online."""
        resp = self._session.get(f"{self.base_url}/health", timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    # ── Internos ──────────────────────────────────────────────────────────────

    def _post(self, path: str, payload: Dict) -> Any:
        url = f"{self.base_url}{path}"
        try:
            resp = self._session.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("outputs", data)
        except requests.exceptions.ConnectionError as e:
            raise NewserPipelineError(f"No se pudo conectar a {url}: {e}")
        except requests.exceptions.Timeout:
            raise NewserPipelineError(f"Timeout al llamar {url}")
        except requests.exceptions.HTTPError as e:
            raise NewserPipelineError(f"Error HTTP {e.response.status_code}: {e.response.text}")

    def __repr__(self) -> str:
        return f"NewserPipeline(task={self.task!r}, base_url={self.base_url!r})"


# ─── Ejemplo de uso ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Apunta a localhost mientras desarrollas
    pipe = NewserPipeline(
        task="weather-forecast",
        base_url="http://localhost:8000",
    )

    print("Estado del servidor:", pipe.health())
    print("Tareas disponibles:", pipe.available_tasks())

    # Pronóstico 7 días para Nuevo Laredo
    forecast = pipe(lat=27.4769, lon=-99.5152, days=7)
    print("Pronóstico:", json.dumps(forecast, indent=2, ensure_ascii=False))

    # Clima actual (atajo)
    actual = pipe.weather(lat=27.4769, lon=-99.5152)
    print("Clima actual:", json.dumps(actual, indent=2, ensure_ascii=False))
