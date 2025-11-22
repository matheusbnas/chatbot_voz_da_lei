from fastapi import APIRouter, HTTPException
from loguru import logger

from app.schemas.schemas import SimplificationRequest, SimplificationResponse
from app.ai.simplification import simplification_service
from app.services.audio import audio_service

router = APIRouter()


@router.post("/", response_model=SimplificationResponse)
async def simplify_text(request: SimplificationRequest):
    """
    Simplificar texto jurídico
    
    Converte linguagem jurídica complexa em linguagem cidadã acessível.
    """
    try:
        # Simplificar texto
        result = await simplification_service.simplify_text(
            text=request.text,
            target_level=request.target_level
        )
        
        # Gerar áudio se solicitado
        audio_url = None
        if request.include_audio:
            audio_path = await audio_service.text_to_speech(
                text=result["simplified_text"],
                language="pt"
            )
            if audio_path:
                audio_url = audio_service.get_audio_url(audio_path)
        
        return SimplificationResponse(
            original_text=request.text,
            simplified_text=result["simplified_text"],
            audio_url=audio_url,
            reading_time_minutes=result["reading_time_minutes"]
        )
        
    except Exception as e:
        logger.error(f"Erro ao simplificar texto: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def simplify_batch(texts: list[str], target_level: str = "simple"):
    """
    Simplificar múltiplos textos em lote
    
    Args:
        texts: Lista de textos para simplificar
        target_level: Nível de simplificação
    """
    try:
        results = []
        
        for text in texts[:10]:  # Limitar a 10 por requisição
            result = await simplification_service.simplify_text(
                text=text,
                target_level=target_level
            )
            results.append({
                "original": text,
                "simplified": result["simplified_text"],
                "reading_time": result["reading_time_minutes"]
            })
        
        return {
            "total": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Erro ao simplificar lote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
