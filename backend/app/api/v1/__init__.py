from fastapi import APIRouter

from app.api.v1 import chat, legislation, simplification, search, audio, data_pipeline

router = APIRouter()

# Incluir rotas de cada módulo
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
router.include_router(legislation.router, prefix="/legislation", tags=["Legislação"])
router.include_router(simplification.router, prefix="/simplification", tags=["Simplificação"])
router.include_router(search.router, prefix="/search", tags=["Busca"])
router.include_router(audio.router, prefix="/audio", tags=["Áudio"])
router.include_router(data_pipeline.router, prefix="/data", tags=["Pipeline de Dados"])
