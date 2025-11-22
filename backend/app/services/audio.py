import base64
import os
from typing import Optional, Dict, Any
from loguru import logger
import asyncio
from pathlib import Path

try:
    import whisper
    from gtts import gTTS
    from pydub import AudioSegment
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logger.warning("Bibliotecas de áudio não instaladas. Funcionalidades de áudio desabilitadas.")

from app.core.config import settings


class AudioService:
    """Serviço para processamento de áudio (transcrição e TTS)"""
    
    def __init__(self):
        self.whisper_model = None
        self.audio_dir = Path("temp/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        if AUDIO_AVAILABLE:
            self._initialize_whisper()
    
    def _initialize_whisper(self):
        """Inicializar modelo Whisper para transcrição"""
        try:
            # Usar modelo base para economia de recursos
            self.whisper_model = whisper.load_model("base")
            logger.info("Modelo Whisper carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo Whisper: {str(e)}")
    
    async def transcribe_audio(
        self,
        audio_data: str,
        language: str = "pt"
    ) -> Dict[str, Any]:
        """
        Transcrever áudio para texto usando Whisper
        
        Args:
            audio_data: Dados do áudio em base64
            language: Código do idioma (pt, en, etc)
        
        Returns:
            Dict com texto transcrito e metadados
        """
        if not AUDIO_AVAILABLE or not self.whisper_model:
            return {
                "text": "",
                "error": "Serviço de transcrição não disponível"
            }
        
        try:
            # Decodificar base64
            audio_bytes = base64.b64decode(audio_data)
            
            # Salvar temporariamente
            temp_path = self.audio_dir / "temp_input.wav"
            with open(temp_path, "wb") as f:
                f.write(audio_bytes)
            
            # Transcrever
            result = await asyncio.to_thread(
                self.whisper_model.transcribe,
                str(temp_path),
                language=language
            )
            
            # Limpar arquivo temporário
            temp_path.unlink(missing_ok=True)
            
            return {
                "text": result["text"],
                "language": result.get("language", language),
                "confidence": None  # Whisper não retorna confidence diretamente
            }
            
        except Exception as e:
            logger.error(f"Erro ao transcrever áudio: {str(e)}")
            return {
                "text": "",
                "error": str(e)
            }
    
    async def text_to_speech(
        self,
        text: str,
        language: str = "pt",
        slow: bool = False
    ) -> Optional[str]:
        """
        Converter texto em áudio usando gTTS
        
        Args:
            text: Texto para converter
            language: Código do idioma
            slow: Se True, fala mais devagar
        
        Returns:
            Caminho do arquivo de áudio ou None em caso de erro
        """
        if not AUDIO_AVAILABLE:
            logger.warning("Serviço TTS não disponível")
            return None
        
        try:
            # Gerar nome único para o arquivo
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
            output_path = self.audio_dir / f"tts_{text_hash}.mp3"
            
            # Se já existe, retornar caminho
            if output_path.exists():
                return str(output_path)
            
            # Gerar áudio
            tts = gTTS(text=text, lang=language, slow=slow)
            await asyncio.to_thread(tts.save, str(output_path))
            
            logger.info(f"Áudio gerado: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {str(e)}")
            return None
    
    async def convert_audio_format(
        self,
        input_path: str,
        output_format: str = "mp3"
    ) -> Optional[str]:
        """
        Converter formato de áudio
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_format: Formato de saída (mp3, wav, ogg)
        
        Returns:
            Caminho do arquivo convertido
        """
        if not AUDIO_AVAILABLE:
            return None
        
        try:
            audio = AudioSegment.from_file(input_path)
            output_path = Path(input_path).with_suffix(f".{output_format}")
            
            await asyncio.to_thread(
                audio.export,
                str(output_path),
                format=output_format
            )
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Erro ao converter formato de áudio: {str(e)}")
            return None
    
    def get_audio_url(self, audio_path: str) -> str:
        """
        Gerar URL pública para o áudio
        
        Args:
            audio_path: Caminho do arquivo de áudio
        
        Returns:
            URL pública
        """
        # Em produção, fazer upload para S3/CDN e retornar URL
        # Por enquanto, retornar caminho relativo
        filename = Path(audio_path).name
        return f"/api/v1/audio/{filename}"
    
    def cleanup_old_files(self, days: int = 7):
        """
        Limpar arquivos de áudio antigos
        
        Args:
            days: Número de dias para manter arquivos
        """
        try:
            import time
            current_time = time.time()
            
            for file_path in self.audio_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (days * 86400):  # dias em segundos
                        file_path.unlink()
                        logger.info(f"Arquivo antigo removido: {file_path}")
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos antigos: {str(e)}")


# Instância global
audio_service = AudioService()
