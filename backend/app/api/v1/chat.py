from fastapi import APIRouter, HTTPException, Depends
from typing import List
from loguru import logger

from app.schemas.schemas import ChatRequest, ChatResponse, ChatMessage
from app.ai.simplification import chat_service
from app.services.audio import audio_service

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Enviar mensagem para o chatbot
    
    Processa mensagem do usuário e retorna resposta contextualizada
    sobre legislação brasileira.
    """
    try:
        # Processar mensagem com histórico de conversa
        history = request.conversation_history or []
        history_dict = [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]
        
        response = await chat_service.chat(
            message=request.message,
            conversation_history=history_dict
        )
        
        # Gerar áudio se solicitado
        audio_url = None
        if request.use_audio:
            audio_path = await audio_service.text_to_speech(
                text=response["message"],
                language="pt"
            )
            if audio_path:
                audio_url = audio_service.get_audio_url(audio_path)
        
        return ChatResponse(
            message=response["message"],
            audio_url=audio_url,
            sources=response.get("sources", []),
            suggestions=response.get("suggestions", [])
        )
        
    except Exception as e:
        logger.error(f"Erro no chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_suggestions():
    """
    Obter sugestões de perguntas populares
    
    Retorna lista de perguntas frequentes para ajudar usuários a começar.
    """
    suggestions = [
        "O que é um projeto de lei?",
        "Como funciona a tramitação de uma PEC?",
        "Quais são os projetos em votação hoje?",
        "Como posso acompanhar um projeto específico?",
        "O que significa emenda constitucional?",
        "Como entrar em contato com meu deputado?",
        "Quais são as leis mais importantes aprovadas este ano?",
        "Como funciona a votação no Congresso?"
    ]
    
    return {"suggestions": suggestions}


@router.get("/history/{user_id}")
async def get_chat_history(user_id: int, limit: int = 20):
    """
    Obter histórico de conversas do usuário
    
    Args:
        user_id: ID do usuário
        limit: Número máximo de mensagens
    """
    # TODO: Implementar busca no banco de dados
    return {
        "user_id": user_id,
        "messages": [],
        "total": 0
    }
