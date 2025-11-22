from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from loguru import logger
from pathlib import Path

from app.schemas.schemas import AudioTranscriptionRequest, AudioTranscriptionResponse
from app.services.audio import audio_service

router = APIRouter()


@router.post("/transcribe", response_model=AudioTranscriptionResponse)
async def transcribe_audio(request: AudioTranscriptionRequest):
    """
    Transcrever áudio para texto
    
    Converte áudio em texto usando Whisper AI.
    """
    try:
        # Validar entrada
        if not request.audio_base64 or not request.audio_base64.strip():
            raise HTTPException(
                status_code=400,
                detail="Dados de áudio não fornecidos"
            )
        
        logger.debug(f"Recebendo requisição de transcrição (tamanho: {len(request.audio_base64)} caracteres)")
        
        result = await audio_service.transcribe_audio(
            audio_data=request.audio_base64,
            language=request.language
        )
        
        if "error" in result:
            error_msg = result["error"]
            logger.error(f"Erro na transcrição: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
        if not result.get("text"):
            logger.warning("Transcrição retornou texto vazio")
            return AudioTranscriptionResponse(
                text="",
                confidence=None,
                language=result.get("language", request.language)
            )
        
        return AudioTranscriptionResponse(
            text=result["text"],
            confidence=result.get("confidence"),
            language=result.get("language", request.language)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao transcrever áudio: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao transcrever áudio: {str(e)}"
        )


@router.post("/tts")
async def text_to_speech(text: str, language: str = "pt", slow: bool = False):
    """
    Converter texto em áudio
    
    Gera arquivo de áudio a partir de texto.
    """
    try:
        audio_path = await audio_service.text_to_speech(
            text=text,
            language=language,
            slow=slow
        )
        
        if not audio_path:
            raise HTTPException(
                status_code=500,
                detail="Erro ao gerar áudio"
            )
        
        audio_url = audio_service.get_audio_url(audio_path)
        
        return {
            "audio_url": audio_url,
            "text": text,
            "language": language
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar áudio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{filename}")
async def get_audio_file(filename: str):
    """
    Servir arquivo de áudio
    
    Args:
        filename: Nome do arquivo de áudio
    """
    try:
        audio_path = Path("temp/audio") / filename
        
        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="Áudio não encontrado")
        
        return FileResponse(
            path=str(audio_path),
            media_type="audio/mpeg",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao servir áudio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload de arquivo de áudio para transcrição
    
    Args:
        file: Arquivo de áudio
    """
    try:
        # Validar tamanho
        contents = await file.read()
        size_mb = len(contents) / (1024 * 1024)
        
        if size_mb > 25:  # Limite de 25MB
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande ({size_mb:.1f}MB). Máximo: 25MB"
            )
        
        # Validar formato
        if file.content_type not in ["audio/mpeg", "audio/wav", "audio/ogg"]:
            raise HTTPException(
                status_code=400,
                detail="Formato não suportado. Use MP3, WAV ou OGG"
            )
        
        # Salvar temporariamente
        temp_path = Path("temp/audio") / f"upload_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Transcrever
        import base64
        audio_base64 = base64.b64encode(contents).decode()
        
        result = await audio_service.transcribe_audio(
            audio_data=audio_base64,
            language="pt"
        )
        
        # Limpar arquivo temporário
        temp_path.unlink(missing_ok=True)
        
        return {
            "filename": file.filename,
            "text": result.get("text", ""),
            "language": result.get("language", "pt")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload de áudio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
