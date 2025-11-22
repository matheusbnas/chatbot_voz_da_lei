import base64
import os
import time
import uuid
from typing import Optional, Dict, Any
from loguru import logger
import asyncio
from pathlib import Path
import warnings

try:
    import whisper
    from gtts import gTTS
    from pydub import AudioSegment
    AUDIO_AVAILABLE = True

    # Configurar caminho do ffmpeg se existir localmente (na raiz do projeto)
    # O arquivo está em backend/app/services/audio.py, então voltamos 3 níveis para a raiz
    project_root = Path(__file__).parent.parent.parent.parent
    ffmpeg_path = project_root / "ffmpeg.exe"
    if ffmpeg_path.exists():
        AudioSegment.converter = str(ffmpeg_path)
        AudioSegment.ffmpeg = str(ffmpeg_path)
        AudioSegment.ffprobe = str(ffmpeg_path)
        logger.info(f"FFmpeg configurado: {ffmpeg_path}")
    else:
        # Suprimir aviso se ffmpeg não estiver disponível (funcionalidades básicas ainda funcionam)
        warnings.filterwarnings(
            "ignore", category=RuntimeWarning, module="pydub")

except ImportError:
    AUDIO_AVAILABLE = False
    logger.warning(
        "Bibliotecas de áudio não instaladas. Funcionalidades de áudio desabilitadas.")

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
        if not AUDIO_AVAILABLE:
            logger.error("Bibliotecas de áudio não disponíveis")
            return {
                "text": "",
                "error": "Serviço de transcrição não disponível. Bibliotecas de áudio não instaladas."
            }

        if not self.whisper_model:
            logger.error("Modelo Whisper não inicializado")
            return {
                "text": "",
                "error": "Serviço de transcrição não disponível. Modelo Whisper não carregado."
            }

        try:
            # Validar entrada
            if not audio_data or not audio_data.strip():
                logger.error("Dados de áudio vazios")
                return {
                    "text": "",
                    "error": "Dados de áudio vazios"
                }
            # Gerar nome único para evitar conflitos em requisições simultâneas
            unique_id = str(uuid.uuid4())[:8]
            timestamp = int(time.time() * 1000)

            # Decodificar base64
            try:
                audio_bytes = base64.b64decode(audio_data)
                if len(audio_bytes) == 0:
                    logger.error("Áudio decodificado está vazio")
                    return {
                        "text": "",
                        "error": "Áudio inválido ou corrompido"
                    }
                logger.debug(f"Áudio decodificado: {len(audio_bytes)} bytes")
            except Exception as decode_error:
                logger.error(
                    f"Erro ao decodificar base64: {str(decode_error)}")
                return {
                    "text": "",
                    "error": f"Erro ao decodificar áudio: {str(decode_error)}"
                }

            # Salvar temporariamente com nome único
            temp_input_path = self.audio_dir / \
                f"temp_input_{timestamp}_{unique_id}"
            temp_wav_path = self.audio_dir / \
                f"temp_input_{timestamp}_{unique_id}.wav"

            # Escrever arquivo e garantir que está fechado
            with open(temp_input_path, "wb") as f:
                f.write(audio_bytes)
                f.flush()
                os.fsync(f.fileno())  # Garantir que está escrito no disco

            # Pequeno delay para garantir que o arquivo está liberado
            await asyncio.sleep(0.1)

            # Tentar detectar o formato e converter se necessário
            # Whisper pode processar vários formatos diretamente, mas WAV é ideal
            try:
                from pydub import AudioSegment

                # Tentar carregar o áudio (pydub detecta automaticamente o formato)
                audio = AudioSegment.from_file(str(temp_input_path))

                # Converter para WAV mono 16kHz (formato ideal para Whisper)
                audio = audio.set_channels(1)  # Mono
                audio = audio.set_frame_rate(16000)  # 16kHz

                # Exportar como WAV diretamente
                audio.export(str(temp_wav_path), format="wav")

                # Limpar arquivo original após conversão bem-sucedida
                try:
                    if temp_input_path.exists():
                        temp_input_path.unlink()
                except Exception as e:
                    logger.debug(
                        f"Erro ao remover arquivo temporário original: {str(e)}")

                logger.debug(
                    f"Áudio convertido com sucesso para WAV: {temp_wav_path}")

            except FileNotFoundError as ffmpeg_error:
                # ffmpeg não encontrado - tentar usar Whisper diretamente
                logger.warning(
                    f"FFmpeg não encontrado: {str(ffmpeg_error)}. Tentando usar Whisper diretamente.")

                # Whisper pode processar WebM e outros formatos diretamente
                # Renomear o arquivo para ter extensão .webm para o Whisper reconhecer
                if temp_input_path.exists():
                    # Verificar se o arquivo tem extensão
                    if not temp_input_path.suffix:
                        # Adicionar extensão .webm (formato mais comum do MediaRecorder)
                        temp_webm = temp_input_path.with_suffix('.webm')
                        try:
                            await asyncio.sleep(0.2)
                            temp_input_path.rename(temp_webm)
                            temp_wav_path = temp_webm
                            logger.info(
                                f"Usando arquivo WebM diretamente: {temp_wav_path}")
                        except Exception as rename_err:
                            logger.warning(
                                f"Erro ao renomear: {str(rename_err)}")
                            temp_wav_path = temp_input_path
                    else:
                        temp_wav_path = temp_input_path
                        logger.info(
                            f"Usando arquivo original: {temp_wav_path}")
                else:
                    return {
                        "text": "",
                        "error": "FFmpeg não encontrado e arquivo original não disponível. Instale o FFmpeg ou use um formato de áudio suportado."
                    }

            except Exception as conv_error:
                logger.warning(f"Erro ao converter áudio: {str(conv_error)}")
                # Se falhar a conversão, tentar usar o arquivo original
                # Whisper pode aceitar alguns formatos diretamente (WebM, MP3, etc)
                if temp_wav_path.exists() and temp_wav_path != temp_input_path:
                    try:
                        temp_wav_path.unlink()
                    except:
                        pass

                # Se o arquivo original existe, tentar usar diretamente
                if temp_input_path.exists():
                    # Whisper suporta vários formatos: wav, mp3, m4a, ogg, webm, flac
                    # Tentar usar o arquivo original
                    temp_wav_path = temp_input_path
                    logger.info(
                        f"Usando arquivo original sem conversão: {temp_wav_path}")
                else:
                    logger.error(
                        "Arquivo original não encontrado após erro de conversão")
                    return {
                        "text": "",
                        "error": f"Erro ao processar áudio. Verifique se o FFmpeg está instalado ou use um formato suportado. Erro: {str(conv_error)}"
                    }

            # Verificar se o arquivo WAV existe antes de transcrever
            if not temp_wav_path.exists():
                logger.error(f"Arquivo WAV não encontrado: {temp_wav_path}")
                return {
                    "text": "",
                    "error": "Erro ao processar arquivo de áudio"
                }

            logger.debug(f"Transcrevendo áudio: {temp_wav_path}")

            # Transcrever
            try:
                result = await asyncio.to_thread(
                    self.whisper_model.transcribe,
                    str(temp_wav_path),
                    language=language
                )

                if not result or "text" not in result:
                    logger.error("Whisper retornou resultado inválido")
                    return {
                        "text": "",
                        "error": "Erro ao transcrever áudio"
                    }

                logger.debug(
                    f"Transcrição concluída: {len(result.get('text', ''))} caracteres")

            except Exception as transcribe_error:
                logger.error(
                    f"Erro durante transcrição do Whisper: {str(transcribe_error)}")
                return {
                    "text": "",
                    "error": f"Erro ao transcrever: {str(transcribe_error)}"
                }

            # Limpar arquivos temporários
            try:
                if temp_wav_path.exists():
                    temp_wav_path.unlink()
            except Exception as e:
                logger.debug(
                    f"Erro ao remover arquivo WAV temporário: {str(e)}")

            try:
                if temp_input_path.exists():
                    temp_input_path.unlink()
            except Exception as e:
                logger.debug(
                    f"Erro ao remover arquivo temporário original: {str(e)}")

            return {
                "text": result.get("text", ""),
                "language": result.get("language", language),
                "confidence": None  # Whisper não retorna confidence diretamente
            }

        except Exception as e:
            logger.error(f"Erro ao transcrever áudio: {str(e)}", exc_info=True)
            return {
                "text": "",
                "error": f"Erro ao processar áudio: {str(e)}"
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
