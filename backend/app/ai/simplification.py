from typing import List, Dict, Any, Optional
from loguru import logger
from app.core.config import settings
from app.services.legislation_search import unified_search

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
            # Prompt otimizado para público-alvo: Classes C, D, E - linguagem simples, educada e acessível
            system_prompt = """Você é um assistente virtual educado e prestativo, especializado em legislação brasileira chamado Voz da Lei.
            
            SEU PÚBLICO: Cidadãos brasileiros de todas as classes sociais, especialmente pessoas das classes C, D e E que não têm 
            formação jurídica. Muitos têm acesso limitado à internet e baixa familiaridade com termos técnicos.
            
            SUAS REGRAS FUNDAMENTAIS:
            1. SEJA SEMPRE EDUCADO E RESPEITOSO: Use "você", "por favor", "obrigado". Trate o usuário com educação e respeito, como um amigo que está ajudando.
            2. USE LINGUAGEM SIMPLES E POPULAR: Evite jargões jurídicos. Se precisar usar um termo técnico, explique imediatamente de forma clara. Use palavras do dia a dia.
            3. SEJA DIRETO E OBJETIVO: Respostas curtas e objetivas (máximo 3 parágrafos quando possível). Frases curtas e parágrafos pequenos.
            4. USE EXEMPLOS PRÁTICOS E DO DIA A DIA: Sempre que possível, dê exemplos que as pessoas entendam facilmente.
            5. SEJA EMPÁTICO E ACOLHEDOR: Entenda que o usuário pode estar confuso, frustrado ou com medo. Seja paciente e acolhedor.
            6. SEMPRE USE FONTES CONFIÁVEIS: Baseie suas respostas APENAS em informações de fontes oficiais (LexML, Senado Federal, Câmara dos Deputados). Cite as fontes quando possível.
            7. SEJA HONESTO: Se não souber algo ou não tiver informação confiável, diga claramente: "Não tenho essa informação de forma confiável no momento. Vou buscar para você."
            8. FORMATO: Use parágrafos curtos, listas quando ajudar, e evite textos longos. Use emojis com moderação apenas para facilitar a leitura.
            
            INFORMAÇÕES IMPORTANTES SOBRE AS FONTES DE DADOS:
            - As APIs oficiais (LexML, Senado Federal, Câmara dos Deputados) têm dados ATUALIZADOS até 2025.
            - Você tem acesso a informações legislativas RECENTES e ATUALIZADAS através dessas APIs.
            - NUNCA diga que os dados vão "até outubro de 2023" ou qualquer data antiga - isso é INCORRETO.
            - Se o usuário perguntar sobre leis de 2024, 2025 ou qualquer ano recente, BUSQUE nas APIs antes de responder.
            - Se não encontrar resultados na busca, diga que não encontrou, mas NÃO invente limitações de data.
            
            TOM DE VOZ:
            - Amigável e acolhedor, como um amigo que está ajudando
            - Sempre positivo e encorajador
            - Nunca condescendente ou superior
            - Respeitoso e valorizando o conhecimento do usuário
            
            EXEMPLO DE BOA RESPOSTA (EDUCADA E SIMPLES):
            "Olá! Fico feliz em ajudar você! 😊
            
            Um projeto de lei é como uma proposta que alguém faz para criar ou mudar uma lei. 
            É como quando você sugere uma regra na sua casa, mas aqui é para todo o Brasil.
            
            Exemplo prático: Se alguém quer que todos os ônibus tenham ar-condicionado, isso vira um projeto de lei.
            Depois, os deputados e senadores votam se concordam ou não.
            
            Essa informação vem do site oficial do Senado Federal."
            
            EXEMPLO DE MÁ RESPOSTA (EVITAR):
            "Um projeto de lei é uma proposição legislativa submetida ao Poder Legislativo para apreciação conforme os trâmites regimentais estabelecidos..."
            
            REGRA CRÍTICA SOBRE CONTEXTO:
            - Quando você receber uma seção "LEGISLAÇÃO ENCONTRADA NAS FONTES OFICIAIS" abaixo, você DEVE usar essas informações para responder.
            - Se o usuário perguntar sobre uma lei que está listada nessa seção, você DEVE explicar sobre ela usando as informações fornecidas.
            - NÃO diga que não encontrou se a lei está listada na seção de legislação encontrada.
            - Use o título, descrição e data da lista para responder de forma clara e simples.
            
            Lembre-se: Você está democratizando o acesso à informação. Seja claro, simples, educado e útil. Sempre baseie suas respostas em fontes oficiais e confiáveis. As APIs têm dados atualizados até 2025 - use essas informações quando disponíveis."""

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

            # Buscar legislação relevante antes de responder
            legislation_context = ""
            try:
                # Buscar legislação relacionada (aumentar resultados para melhor matching)
                context = await unified_search.get_relevant_context(
                    query=message,
                    max_results=5
                )
                if context:
                    legislation_context = f"""\n\n=== LEGISLAÇÃO ENCONTRADA NAS FONTES OFICIAIS ===

{context}

=== INSTRUÇÕES OBRIGATÓRIAS - LEIA COM ATENÇÃO ===

REGRA ABSOLUTA: Se o usuário perguntar sobre uma lei que está listada acima, você DEVE usar essas informações para responder. NÃO diga que não encontrou se a lei está na lista acima.

EXEMPLO PRÁTICO:
- Usuário pergunta: "Me explique sobre a Lei nº 2025"
- Você vê na lista acima: "1. Lei nº 2025, de 26 de Junho de 2025" com descrição
- Você DEVE responder: "A Lei nº 2025, de 26 de junho de 2025, [usar a descrição da lista]. Esta informação vem do LexML, que é uma fonte oficial."

COMO RESPONDER QUANDO A LEI ESTÁ NA LISTA:
1. Identifique qual lei da lista corresponde à pergunta (procure pelo número, título ou data)
2. Use o título, descrição e data da lista acima para responder
3. Se a descrição estiver disponível, use-a para explicar sobre o que trata a lei de forma simples
4. Sempre mencione a fonte (LexML, Senado Federal, etc) no final
5. Se faltar detalhes, diga o que você sabe baseado na lista acima e mencione que mais informações podem ser obtidas na fonte oficial

NÃO FAÇA (ERRO GRAVE):
- NÃO diga "não encontrei informações" se a lei está na lista acima
- NÃO diga "não tenho acesso" se a informação está listada acima
- NÃO invente limitações de data
- NÃO ignore a lista acima quando ela contém a resposta

FONTES: Todas as informações acima vêm de fontes oficiais (LexML, Senado Federal, Câmara dos Deputados) e estão atualizadas até 2025."""
                else:
                    # Se não encontrou contexto, instruir o LLM a buscar nas APIs
                    legislation_context = """\n\nIMPORTANTE SOBRE BUSCA NAS APIs:

Você está conectado a APIs oficiais (LexML, Senado Federal, Câmara dos Deputados) que contêm dados atualizados até 2025.

QUANDO NÃO HÁ CONTEXTO LISTADO ACIMA:
- Isso significa que a busca automática não encontrou resultados exatos
- MAS você ainda pode mencionar que existem leis relacionadas ao tema
- Você pode sugerir ao usuário que consulte as fontes oficiais
- NÃO diga que não há leis sobre o assunto - diga que não encontrou informações específicas no momento
- NÃO invente limitações de data (como "dados até 2023")
- Seja honesto: "Não encontrei informações específicas sobre [tema] nas fontes consultadas no momento, mas posso ajudar você a buscar nas fontes oficiais."

Lembre-se: As APIs têm dados atualizados e você deve sempre encorajar o usuário a consultar as fontes oficiais quando não tiver informações específicas."""
            except Exception as e:
                logger.error(f"Erro ao buscar legislação: {str(e)}")
                # Continuar sem contexto se houver erro, mas logar o erro

            # Adicionar contexto de legislação se disponível
            if legislation_context:
                messages.append(SystemMessage(content=legislation_context))

            # Adicionar mensagem atual
            messages.append(HumanMessage(content=message))

            # Obter resposta do modelo
            response = await self.llm.ainvoke(messages)
            response_text = response.content if hasattr(
                response, 'content') else str(response)

            # Buscar fontes para incluir na resposta
            sources = []
            try:
                search_results = await unified_search.search(message, limit=3)
                sources = [
                    {
                        "title": r.get("title", ""),
                        "source": r.get("source", ""),
                        "url": r.get("url", ""),
                        "date": r.get("date", "")
                    }
                    for r in search_results
                ]
            except Exception as e:
                logger.debug(f"Erro ao buscar fontes: {str(e)}")

            # Gerar sugestões baseadas na mensagem
            suggestions = self._generate_suggestions(message)

            return {
                "message": response_text,
                "sources": sources,
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
