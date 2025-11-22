from typing import List, Dict, Any, Optional
from loguru import logger
from app.core.config import settings

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning(
        "LangChain não está disponível. Funcionalidades de chat desabilitadas.")


class ChatService:
    """Serviço para processamento de chat com IA"""

    def __init__(self):
        self.llm = None
        self._initialize_llm()

    def _initialize_llm(self):
        """Inicializar modelo de linguagem"""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain não disponível. Chat desabilitado.")
            return

        try:
            # Prioridade: OpenAI > Groq
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",  # Modelo mais barato e eficiente da OpenAI
                    temperature=0.7,
                    api_key=settings.OPENAI_API_KEY
                )
                logger.info("Modelo OpenAI GPT-4o-mini inicializado")
            elif settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip():
                # Groq usa API compatível com OpenAI
                # Modelos disponíveis: llama-3.1-8b-instant, mixtral-8x7b-32768, gemma-7b-it
                self.llm = ChatOpenAI(
                    # Modelo gratuito do Groq (atualizado)
                    model="llama-3.1-8b-instant",
                    temperature=0.7,
                    api_key=settings.GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )
                logger.info("Modelo Groq (Llama 3.1 8B Instant) inicializado")
            else:
                logger.warning(
                    "Nenhuma chave de API configurada. Chat desabilitado.")
        except Exception as e:
            logger.error(f"Erro ao inicializar modelo de linguagem: {str(e)}")
            self.llm = None

    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Processar mensagem do usuário e retornar resposta

        Args:
            message: Mensagem do usuário
            conversation_history: Histórico de conversa anterior

        Returns:
            Dict com 'message', 'sources' e 'suggestions'
        """
        if not self.llm:
            return {
                "message": "Desculpe, o serviço de chat não está disponível no momento. Por favor, configure uma chave de API (OPENAI_API_KEY ou GROQ_API_KEY) no arquivo .env do backend.",
                "sources": [],
                "suggestions": []
            }

        try:
            # Verificar se o LLM está disponível antes de processar
            if not self.llm:
                return {
                    "message": "O serviço de chat não está disponível. Por favor, configure uma chave de API (OPENAI_API_KEY ou GROQ_API_KEY) no arquivo .env do backend. Veja o arquivo CONFIGURAR_API.md para mais informações.",
                    "sources": [],
                    "suggestions": []
                }

            # Preparar mensagens para o modelo
            messages = []

            # Adicionar mensagem do sistema
            # Prompt otimizado para público-alvo: Classes C, D, E - linguagem simples e acessível
            system_prompt = """Você é um assistente especializado em legislação brasileira chamado Voz da Lei.
            
            SEU PÚBLICO: Cidadãos brasileiros de todas as classes sociais, especialmente pessoas que não têm 
            formação jurídica. Muitos têm acesso limitado à internet e baixa familiaridade com termos técnicos.
            
            SUAS REGRAS:
            1. USE LINGUAGEM SIMPLES: Evite jargões jurídicos. Se precisar usar um termo técnico, explique imediatamente.
            2. SEJA DIRETO: Respostas curtas e objetivas (máximo 3 parágrafos quando possível).
            3. USE EXEMPLOS PRÁTICOS: Sempre que possível, dê exemplos do dia a dia.
            4. SEJA EMPÁTICO: Entenda que o usuário pode estar confuso ou frustrado.
            5. SEJA HONESTO: Se não souber algo, diga claramente.
            6. FORMATO: Use parágrafos curtos, listas quando ajudar, e evite textos longos.
            
            EXEMPLO DE BOA RESPOSTA:
            "Um projeto de lei é como uma proposta que alguém faz para criar ou mudar uma lei. 
            É como quando você sugere uma regra na sua casa, mas aqui é para todo o Brasil.
            
            Exemplo: Se alguém quer que todos os ônibus tenham ar-condicionado, isso vira um projeto de lei.
            Depois, os deputados e senadores votam se concordam ou não."
            
            EXEMPLO DE MÁ RESPOSTA:
            "Um projeto de lei é uma proposição legislativa submetida ao Poder Legislativo para apreciação..."
            
            Lembre-se: Você está democratizando o acesso à informação. Seja claro, simples e útil."""

            messages.append(SystemMessage(content=system_prompt))

            # Adicionar histórico de conversa
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        messages.append(AIMessage(content=content))

            # Adicionar mensagem atual
            messages.append(HumanMessage(content=message))

            # Obter resposta do modelo
            response = await self.llm.ainvoke(messages)
            response_text = response.content if hasattr(
                response, 'content') else str(response)

            # Gerar sugestões baseadas na mensagem
            suggestions = self._generate_suggestions(message)

            return {
                "message": response_text,
                "sources": [],  # TODO: Implementar busca de legislação relacionada
                "suggestions": suggestions
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro ao processar chat: {error_msg}")

            # Tratar erros de autenticação especificamente
            if "401" in error_msg or "authentication_error" in error_msg or ("invalid" in error_msg.lower() and "api" in error_msg.lower()):
                return {
                    "message": "Erro de autenticação: As chaves de API não estão configuradas corretamente. Por favor, configure OPENAI_API_KEY ou GROQ_API_KEY no arquivo .env do backend.",
                    "sources": [],
                    "suggestions": []
                }

            # Tratar erro de modelo descontinuado
            if "model_decommissioned" in error_msg or "decommissioned" in error_msg.lower():
                return {
                    "message": "O modelo de IA foi atualizado. Por favor, reinicie o servidor backend para usar o novo modelo.",
                    "sources": [],
                    "suggestions": []
                }

            # Tratar outros erros de forma genérica, mas com mais detalhes em modo DEBUG
            if settings.DEBUG:
                return {
                    "message": f"Erro ao processar mensagem: {error_msg[:200]}",
                    "sources": [],
                    "suggestions": []
                }

            return {
                "message": "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde.",
                "sources": [],
                "suggestions": []
            }

    def _generate_suggestions(self, message: str) -> List[str]:
        """Gerar sugestões de perguntas relacionadas"""
        # Sugestões padrão
        default_suggestions = [
            "O que é um projeto de lei?",
            "Como funciona a tramitação de uma PEC?",
            "Quais são os projetos em votação hoje?",
            "Como posso acompanhar um projeto específico?"
        ]

        # TODO: Implementar geração inteligente de sugestões baseada na mensagem
        return default_suggestions

    async def simplify_text(
        self,
        text: str,
        target_level: str = "simple"
    ) -> str:
        """
        Simplificar texto legislativo

        Args:
            text: Texto a ser simplificado
            target_level: Nível de simplificação (simple, moderate, technical)

        Returns:
            Texto simplificado
        """
        if not self.llm:
            return "Serviço de simplificação não disponível."

        try:
            prompt = f"""Simplifique o seguinte texto legislativo para um nível {target_level}.
            Mantenha o significado original, mas use linguagem mais acessível.
            
            Texto original:
            {text}
            
            Texto simplificado:"""

            response = await self.llm.ainvoke([HumanMessage(content=prompt)])
            return response.content if hasattr(response, 'content') else str(response)

        except Exception as e:
            logger.error(f"Erro ao simplificar texto: {str(e)}")
            return f"Erro ao simplificar texto: {str(e)}"


class SimplificationService:
    """Serviço especializado para simplificação de textos legislativos"""

    def __init__(self):
        self.chat_service = ChatService()

    async def simplify_text(
        self,
        text: str,
        target_level: str = "simple"
    ) -> Dict[str, Any]:
        """
        Simplificar texto legislativo e retornar com metadados

        Args:
            text: Texto a ser simplificado
            target_level: Nível de simplificação (simple, moderate, technical)

        Returns:
            Dict com 'simplified_text' e 'reading_time_minutes'
        """
        simplified = await self.chat_service.simplify_text(text, target_level)

        # Calcular tempo de leitura (assumindo ~200 palavras por minuto)
        word_count = len(simplified.split())
        reading_time = max(1, round(word_count / 200))

        return {
            "simplified_text": simplified,
            "reading_time_minutes": reading_time
        }


# Instâncias globais dos serviços
chat_service = ChatService()
simplification_service = SimplificationService()
