"""
Módulo AI/LLM — Integración con Hugging Face y modelos ligeros.
Diseñado para correr en CPU con modelos cuantizados (GGUF/ONNX).
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logger import logger

router = APIRouter()

# ─── Modelos de request/response ─────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    max_tokens: int = Field(default=512, le=2048)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    stream: bool = False

class ChatResponse(BaseModel):
    model: str
    message: ChatMessage
    usage: Dict[str, int] = {}

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000)
    language: str = "es"
    max_sentences: int = Field(default=3, ge=1, le=10)

# ─── Carga lazy del modelo (solo cuando se llama, no al arrancar) ─────────────

_pipeline_cache: Dict[str, Any] = {}

async def _get_hf_pipeline(task: str = "text-generation"):
    """
    Carga el modelo de HF solo la primera vez (lazy loading).
    Ahorra RAM en hosting gratuito.
    """
    if task in _pipeline_cache:
        return _pipeline_cache[task]

    if not settings.HF_TOKEN:
        return None

    try:
        from transformers import pipeline  # type: ignore
        logger.info(f"[AI] Cargando modelo {settings.DEFAULT_MODEL} para task={task}...")
        pipe = pipeline(
            task,
            model=settings.DEFAULT_MODEL,
            device=-1 if settings.USE_CPU_ONLY else 0,  # -1 = CPU
            token=settings.HF_TOKEN,
        )
        _pipeline_cache[task] = pipe
        logger.info("[AI] Modelo cargado exitosamente.")
        return pipe
    except Exception as e:
        logger.error(f"[AI] Error cargando modelo: {e}")
        return None

# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat con modelo LLM",
)
async def chat(req: ChatRequest):
    model_name = req.model or settings.DEFAULT_MODEL
    pipe = await _get_hf_pipeline("text-generation")

    if pipe is None:
        # Modo sin modelo: respuesta informativa
        return ChatResponse(
            model=model_name,
            message=ChatMessage(
                role="assistant",
                content=(
                    "⚠️ Modelo no cargado. Configura HF_TOKEN en .env y "
                    "asegúrate de que el servidor tenga al menos 4GB RAM."
                ),
            ),
        )

    # Construir prompt
    prompt = "\n".join(f"{m.role}: {m.content}" for m in req.messages)
    try:
        result = pipe(prompt, max_new_tokens=req.max_tokens, temperature=req.temperature)
        reply_text = result[0]["generated_text"][len(prompt):].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de inferencia: {e}")

    return ChatResponse(
        model=model_name,
        message=ChatMessage(role="assistant", content=reply_text),
        usage={"prompt_tokens": len(prompt.split()), "completion_tokens": len(reply_text.split())},
    )


@router.get(
    "/models",
    summary="Listar modelos disponibles",
)
async def list_models():
    return {
        "default": settings.DEFAULT_MODEL,
        "recommended_free_tier": [
            {"id": "THUDM/glm-4-9b-chat",     "size": "9B",  "cpu_ok": True},
            {"id": "microsoft/phi-3-mini-4k",  "size": "3.8B","cpu_ok": True},
            {"id": "Qwen/Qwen2.5-1.5B-Instruct","size": "1.5B","cpu_ok": True},
            {"id": "google/gemma-2-2b-it",     "size": "2B",  "cpu_ok": True},
        ],
        "note": "En hosting gratuito usa modelos ≤3B para tiempos de respuesta razonables.",
    }


@router.get(
    "/status",
    summary="Estado del módulo IA",
)
async def ai_status():
    return {
        "model": settings.DEFAULT_MODEL,
        "loaded": settings.DEFAULT_MODEL in _pipeline_cache,
        "device": "CPU" if settings.USE_CPU_ONLY else "GPU",
        "hf_token_set": bool(settings.HF_TOKEN),
    }
