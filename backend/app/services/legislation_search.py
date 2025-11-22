"""
Serviço unificado de busca de legislação

Busca em múltiplas fontes (LexML, Senado, Câmara) e retorna resultados padronizados.
"""
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime

from app.integrations.legislative_apis import (
    lexml_client,
    senado_client,
    camara_client
)


class UnifiedLegislationSearch:
    """Serviço unificado para buscar legislação em múltiplas fontes"""

    async def search(
        self,
        query: str,
        limit: int = 5,
        sources: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Buscar legislação em múltiplas fontes
        
        Args:
            query: Texto da busca
            limit: Número máximo de resultados por fonte
            sources: Fontes a buscar (None = todas)
                    Opções: 'lexml', 'senado', 'camara'
        
        Returns:
            Lista de resultados padronizados
        """
        if sources is None:
            sources = ['lexml', 'senado', 'camara']
        
        all_results = []
        
        # Buscar no LexML
        if 'lexml' in sources:
            try:
                lexml_results = await lexml_client.search_by_keywords(
                    keywords=query,
                    limit=limit
                )
                for doc in lexml_results:
                    all_results.append(self._normalize_lexml_result(doc))
            except Exception as e:
                logger.debug(f"Erro ao buscar no LexML: {str(e)}")
        
        # Buscar no Senado
        if 'senado' in sources:
            try:
                senado_results = await senado_client.search_legislation(
                    keywords=query,
                    limit=limit
                )
                for doc in senado_results:
                    all_results.append(self._normalize_senado_result(doc))
            except Exception as e:
                logger.debug(f"Erro ao buscar no Senado: {str(e)}")
        
        # Buscar na Câmara
        if 'camara' in sources:
            try:
                camara_results = await camara_client.search_propositions(
                    keywords=query,
                    limit=limit
                )
                for doc in camara_results:
                    all_results.append(self._normalize_camara_result(doc))
            except Exception as e:
                logger.debug(f"Erro ao buscar na Câmara: {str(e)}")
        
        # Ordenar por relevância (simples: por título que contém a query)
        all_results.sort(
            key=lambda x: (
                query.lower() in x.get('title', '').lower(),
                x.get('date', '')
            ),
            reverse=True
        )
        
        return all_results[:limit * len(sources)]

    def _normalize_lexml_result(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizar resultado do LexML"""
        return {
            "id": doc.get("urn", ""),
            "title": doc.get("title", doc.get("dc:title", "")),
            "description": doc.get("description", doc.get("dc:description", ""))[:300],
            "type": doc.get("tipo_documento", ""),
            "date": doc.get("date", doc.get("dc:date", "")),
            "source": "LexML",
            "url": doc.get("url", ""),
            "urn": doc.get("urn", "")
        }

    def _normalize_senado_result(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizar resultado do Senado"""
        return {
            "id": str(doc.get("id", "")),
            "title": doc.get("ementa", ""),
            "description": doc.get("ementa", "")[:300],
            "type": doc.get("tipo", ""),
            "date": doc.get("data_apresentacao", ""),
            "source": "Senado Federal",
            "number": doc.get("numero", ""),
            "year": doc.get("ano", ""),
            "author": doc.get("autor", "")
        }

    def _normalize_camara_result(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizar resultado da Câmara"""
        return {
            "id": str(doc.get("id", "")),
            "title": doc.get("ementa", ""),
            "description": doc.get("ementa", "")[:300],
            "type": doc.get("siglaTipo", ""),
            "date": doc.get("dataApresentacao", ""),
            "source": "Câmara dos Deputados",
            "number": str(doc.get("numero", "")),
            "year": doc.get("ano", ""),
            "status": doc.get("statusProposicao", {}).get("descricaoSituacao", "")
        }

    async def get_relevant_context(
        self,
        query: str,
        max_results: int = 3
    ) -> str:
        """
        Obter contexto relevante de legislação para uma pergunta
        
        Args:
            query: Pergunta do usuário
            max_results: Número máximo de resultados
        
        Returns:
            Texto formatado com contexto relevante
        """
        results = await self.search(query, limit=max_results)
        
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Sem título')
            description = result.get('description', '')
            source = result.get('source', '')
            date = result.get('date', '')
            
            context = f"{i}. {title}"
            if description:
                context += f"\n   {description}"
            if source:
                context += f"\n   Fonte: {source}"
            if date:
                context += f" ({date})"
            
            context_parts.append(context)
        
        return "\n\n".join(context_parts)


# Instância global
unified_search = UnifiedLegislationSearch()

