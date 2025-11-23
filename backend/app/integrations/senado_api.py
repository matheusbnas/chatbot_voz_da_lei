"""
Cliente completo para API de Dados Abertos do Senado Federal

FONTE OFICIAL E CONFIÁVEL:
- Documentação oficial: https://legis.senado.leg.br/dadosabertos/v3/api-docs
- API Base: https://legis.senado.leg.br/dadosabertos
- Versão da API: 4.0.3.52 (conforme documentação oficial)

Esta é a API oficial de Dados Abertos Legislativos do Senado Federal e do Congresso Nacional.
É uma API de acesso público, sem necessidade de autenticação, fornecida pelo próprio Senado.

LIMITAÇÕES DE REQUISIÇÕES (conforme documentação oficial):
- Mais de 10 requisições por segundo podem retornar HTTP 429 (Too Many Requests)
- Em momentos de alta demanda, pode retornar HTTP 503 (Service Unavailable)
- Evitar requisições em horários arredondados (00:00:00, 01:00:00, etc) para evitar picos

FORMATOS DISPONÍVEIS:
- application/json (padrão usado neste cliente)
- application/xml
- text/csv
"""
import aiohttp
import xml.etree.ElementTree as ET
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
from time import time


class SenadoAPIClient:
    """Cliente para API de Dados Abertos do Senado Federal"""

    BASE_URL = "https://legis.senado.leg.br/dadosabertos"

    def __init__(self):
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "VozDaLei/1.0"
        }
        # Rate limiting: máximo de 10 requisições por segundo
        self._last_request_time = 0.0
        self._min_request_interval = 0.1  # 100ms entre requisições (10 req/s)

    # ==================== LEGISLAÇÃO (ENDPOINTS OFICIAIS) ====================
    # Endpoints da API oficial: /dadosabertos/legislacao/*
    # Documentação: https://legis.senado.leg.br/dadosabertos/v3/api-docs

    async def legislacao_por_codigo(self, codigo: str) -> Dict[str, Any]:
        """
        Obter detalhes de uma Norma Jurídica pelo código

        Endpoint: GET /dadosabertos/legislacao/{codigo}

        Args:
            codigo: Código da norma jurídica

        Returns:
            Detalhes completos da norma jurídica
        """
        try:
            url = f"{self.BASE_URL}/legislacao/{codigo}"
            data = await self._make_request(url)
            return data if data else {}
        except Exception as e:
            logger.error(
                f"Erro ao obter legislação por código {codigo}: {str(e)}")
            return {}

    async def legislacao_por_identificacao(
        self,
        tipo: str,
        numdata: str,
        anoseq: str
    ) -> Dict[str, Any]:
        """
        Obter detalhes de uma Norma Jurídica pela identificação (sigla / número / ano)

        Endpoint: GET /dadosabertos/legislacao/{tipo}/{numdata}/{anoseq}

        Args:
            tipo: Tipo/sigla da norma (ex: LEI, DEC, MPV)
            numdata: Número/data da norma
            anoseq: Ano/sequência da norma

        Returns:
            Detalhes completos da norma jurídica
        """
        try:
            url = f"{self.BASE_URL}/legislacao/{tipo}/{numdata}/{anoseq}"
            data = await self._make_request(url)
            return data if data else {}
        except Exception as e:
            logger.error(
                f"Erro ao obter legislação por identificação {tipo}/{numdata}/{anoseq}: {str(e)}")
            return {}

    async def legislacao_classes(self) -> List[Dict[str, Any]]:
        """
        Listar Classificação de Normas Jurídicas, Projetos e Pronunciamentos

        Endpoint: GET /dadosabertos/legislacao/classes

        Returns:
            Lista de classificações de normas jurídicas
        """
        try:
            url = f"{self.BASE_URL}/legislacao/classes"
            data = await self._make_request(url)
            if data:
                # A estrutura pode variar, retornar o que vier
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("classes", data.get("dados", []))
            return []
        except Exception as e:
            logger.error(f"Erro ao obter classes de legislação: {str(e)}")
            return []

    async def legislacao_lista(
        self,
        ano: Optional[int] = None,
        tipo: Optional[str] = None,
        numero: Optional[str] = None,
        data_inicio: Optional[str] = None,  # YYYYMMDD
        data_fim: Optional[str] = None,  # YYYYMMDD
        pagina: Optional[int] = None,
        quantidade: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Pesquisar Normas Federais

        Endpoint: GET /dadosabertos/legislacao/lista

        Args:
            ano: Ano da norma
            tipo: Tipo da norma (LEI, DEC, MPV, etc)
            numero: Número da norma
            data_inicio: Data de início (formato YYYYMMDD)
            data_fim: Data de fim (formato YYYYMMDD)
            pagina: Número da página
            quantidade: Quantidade de resultados por página

        Returns:
            Resultado da pesquisa com lista de normas
        """
        try:
            params = {}

            if ano:
                params["ano"] = ano
            if tipo:
                params["tipo"] = tipo
            if numero:
                params["numero"] = numero
            if data_inicio:
                params["dataInicio"] = data_inicio
            if data_fim:
                params["dataFim"] = data_fim
            if pagina:
                params["pagina"] = pagina
            if quantidade:
                params["quantidade"] = quantidade

            url = f"{self.BASE_URL}/legislacao/lista"
            data = await self._make_request(url, params=params if params else None)
            return data if data else {}
        except Exception as e:
            logger.error(f"Erro ao pesquisar legislação: {str(e)}")
            return {}

    async def legislacao_termos(
        self,
        termo: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Pesquisar Termos do Catálogo

        Endpoint: GET /dadosabertos/legislacao/termos

        Args:
            termo: Termo a pesquisar
            tipo: Tipo de termo (opcional)

        Returns:
            Lista de termos encontrados
        """
        try:
            params = {}

            if termo:
                params["termo"] = termo
            if tipo:
                params["tipo"] = tipo

            url = f"{self.BASE_URL}/legislacao/termos"
            data = await self._make_request(url, params=params if params else None)
            if data:
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("termos", data.get("dados", []))
            return []
        except Exception as e:
            logger.error(f"Erro ao pesquisar termos: {str(e)}")
            return []

    async def legislacao_tipos_declaracao_detalhe(self) -> List[Dict[str, Any]]:
        """
        Listar Detalhes de Declaração

        Endpoint: GET /dadosabertos/legislacao/tiposdeclaracao/detalhe

        Returns:
            Lista de detalhes de declaração
        """
        try:
            url = f"{self.BASE_URL}/legislacao/tiposdeclaracao/detalhe"
            data = await self._make_request(url)
            if data:
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("tipos", data.get("dados", []))
            return []
        except Exception as e:
            logger.error(f"Erro ao obter tipos de declaração: {str(e)}")
            return []

    async def legislacao_tipos_norma(self) -> List[Dict[str, Any]]:
        """
        Listar Tipos de Norma

        Endpoint: GET /dadosabertos/legislacao/tiposNorma

        Returns:
            Lista de tipos de norma disponíveis
        """
        try:
            url = f"{self.BASE_URL}/legislacao/tiposNorma"
            data = await self._make_request(url)
            if data:
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("tipos", data.get("dados", []))
            return []
        except Exception as e:
            logger.error(f"Erro ao obter tipos de norma: {str(e)}")
            return []

    async def legislacao_tipos_publicacao(self) -> List[Dict[str, Any]]:
        """
        Listar Tipos de Publicação

        Endpoint: GET /dadosabertos/legislacao/tiposPublicacao

        Returns:
            Lista de tipos de publicação disponíveis
        """
        try:
            url = f"{self.BASE_URL}/legislacao/tiposPublicacao"
            data = await self._make_request(url)
            if data:
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("tipos", data.get("dados", []))
            return []
        except Exception as e:
            logger.error(f"Erro ao obter tipos de publicação: {str(e)}")
            return []

    async def legislacao_tipos_vide(self) -> List[Dict[str, Any]]:
        """
        Listar Tipos de Declaração

        Endpoint: GET /dadosabertos/legislacao/tiposVide

        Returns:
            Lista de tipos de declaração (vide)
        """
        try:
            url = f"{self.BASE_URL}/legislacao/tiposVide"
            data = await self._make_request(url)
            if data:
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("tipos", data.get("dados", []))
            return []
        except Exception as e:
            logger.error(f"Erro ao obter tipos vide: {str(e)}")
            return []

    async def legislacao_por_urn(self, urn: str) -> Dict[str, Any]:
        """
        Obter detalhes de uma Norma Jurídica pela URN

        Endpoint: GET /dadosabertos/legislacao/urn

        Args:
            urn: URN (Uniform Resource Name) da norma jurídica

        Returns:
            Detalhes completos da norma jurídica
        """
        try:
            params = {"urn": urn}
            url = f"{self.BASE_URL}/legislacao/urn"
            data = await self._make_request(url, params=params)
            return data if data else {}
        except Exception as e:
            logger.error(f"Erro ao obter legislação por URN {urn}: {str(e)}")
            return {}

    # ==================== NORMAS (LEIS E LEGISLAÇÃO) - MÉTODOS LEGADOS ====================
    # Nota: Estes métodos usam endpoints alternativos (/norma/*)
    # Para usar os endpoints oficiais de legislação, prefira os métodos acima

    async def listar_normas(
        self,
        ano: Optional[int] = None,
        numero: Optional[str] = None,
        tipo: Optional[str] = None,  # LEI, DEC, MPV, etc
        tramitando: bool = False,
        data_inicio: Optional[str] = None,  # YYYYMMDD
        data_fim: Optional[str] = None,  # YYYYMMDD
        pagina: int = 1,
        quantidade: int = 100
    ) -> Dict[str, Any]:
        """
        Listar normas (leis, decretos, medidas provisórias, etc)

        Endpoint: /norma/listar
        """
        try:
            params = {
                "pagina": pagina,
                "quantidade": quantidade
            }

            if ano:
                params["ano"] = ano
            if numero:
                params["numero"] = numero
            if tipo:
                params["tipo"] = tipo
            if tramitando:
                params["tramitando"] = "S"
            if data_inicio:
                params["dataInicio"] = data_inicio
            if data_fim:
                params["dataFim"] = data_fim

            url = f"{self.BASE_URL}/norma/listar"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    # Se retornar 404, tentar endpoint alternativo
                    if response.status == 404:
                        logger.warning(
                            f"Endpoint /norma/listar retornou 404. Tentando endpoint alternativo...")
                        # Tentar endpoint alternativo sem o /listar
                        alt_url = f"{self.BASE_URL}/norma"
                        async with session.get(alt_url, params=params, headers=self.headers) as alt_response:
                            if alt_response.status == 200:
                                data = await alt_response.json()
                                return data
                            else:
                                logger.warning(
                                    f"Endpoint alternativo também falhou: {alt_response.status}")
                                return {"normas": [], "total": 0}

                    response.raise_for_status()
                    data = await response.json()
                    return data

        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                logger.warning(
                    f"Endpoint do Senado retornou 404. Verifique a documentação oficial: https://legis.senado.leg.br/dadosabertos/v3/api-docs. URL: {e.request_info.url}")
            elif e.status == 429:
                logger.warning(
                    "Limite de requisições excedido (HTTP 429). Aguardando antes de tentar novamente...")
                await asyncio.sleep(1)  # Aguardar 1 segundo antes de retry
            elif e.status == 503:
                logger.warning(
                    "Serviço temporariamente indisponível (HTTP 503). Aguardando antes de tentar novamente...")
                await asyncio.sleep(2)  # Aguardar 2 segundos antes de retry
            else:
                logger.error(
                    f"Erro HTTP ao listar normas: {e.status} - {str(e)}")
            return {"normas": [], "total": 0}
        except Exception as e:
            logger.error(f"Erro ao listar normas: {str(e)}")
            return {"normas": [], "total": 0}

    async def detalhe_norma(self, codigo_norma: str) -> Dict[str, Any]:
        """
        Obter detalhes completos de uma norma

        Endpoint: /norma/{codigo}
        """
        try:
            url = f"{self.BASE_URL}/norma/{codigo_norma}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data

        except Exception as e:
            logger.error(
                f"Erro ao obter detalhes da norma {codigo_norma}: {str(e)}")
            return {}

    async def texto_norma(self, codigo_norma: str) -> Optional[str]:
        """
        Obter texto completo de uma norma

        Endpoint: /norma/{codigo}/texto
        """
        try:
            url = f"{self.BASE_URL}/norma/{codigo_norma}/texto"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Extrair texto do JSON
                    if "textoNorma" in data:
                        return data["textoNorma"].get("texto", "")

                    return None

        except Exception as e:
            logger.error(
                f"Erro ao obter texto da norma {codigo_norma}: {str(e)}")
            return None

    async def normas_relacionadas(self, codigo_norma: str) -> List[Dict[str, Any]]:
        """
        Obter normas relacionadas (alterações, revogações, etc)

        Endpoint: /norma/{codigo}/relacionadas
        """
        try:
            url = f"{self.BASE_URL}/norma/{codigo_norma}/relacionadas"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("normasRelacionadas", [])

        except Exception as e:
            logger.error(f"Erro ao obter normas relacionadas: {str(e)}")
            return []

    # ==================== MATÉRIAS (PROJETOS DE LEI) ====================

    async def listar_materias(
        self,
        ano: Optional[int] = None,
        numero: Optional[str] = None,
        sigla: Optional[str] = None,  # PLS, PLC, PEC, etc
        tramitando: bool = True,
        autor: Optional[str] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        pagina: int = 1,
        quantidade: int = 100
    ) -> Dict[str, Any]:
        """
        Listar matérias (projetos de lei, PECs, etc)

        Endpoint: /materia/pesquisa/lista
        """
        try:
            params = {
                "pagina": pagina,
                "quantidade": quantidade
            }

            if ano:
                params["ano"] = ano
            if numero:
                params["numero"] = numero
            if sigla:
                params["sigla"] = sigla
            if tramitando:
                params["tramitando"] = "S"
            else:
                params["tramitando"] = "N"
            if autor:
                params["autor"] = autor
            if data_inicio:
                params["dataInicio"] = data_inicio
            if data_fim:
                params["dataFim"] = data_fim

            url = f"{self.BASE_URL}/materia/pesquisa/lista"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data

        except Exception as e:
            logger.error(f"Erro ao listar matérias: {str(e)}")
            return {"materias": [], "total": 0}

    async def detalhe_materia(self, codigo_materia: str) -> Dict[str, Any]:
        """
        Obter detalhes completos de uma matéria

        Endpoint: /materia/{codigo}
        """
        try:
            url = f"{self.BASE_URL}/materia/{codigo_materia}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data

        except Exception as e:
            logger.error(
                f"Erro ao obter detalhes da matéria {codigo_materia}: {str(e)}")
            return {}

    async def texto_materia(self, codigo_materia: str) -> Optional[str]:
        """
        Obter texto/inteiro teor de uma matéria

        Endpoint: /materia/{codigo}/texto
        """
        try:
            url = f"{self.BASE_URL}/materia/{codigo_materia}/texto"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()

                    if "textoMateria" in data:
                        return data["textoMateria"].get("texto", "")

                    return None

        except Exception as e:
            logger.error(
                f"Erro ao obter texto da matéria {codigo_materia}: {str(e)}")
            return None

    async def autores_materia(self, codigo_materia: str) -> List[Dict[str, Any]]:
        """
        Obter autores de uma matéria

        Endpoint: /materia/{codigo}/autores
        """
        try:
            url = f"{self.BASE_URL}/materia/{codigo_materia}/autores"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("autores", [])

        except Exception as e:
            logger.error(f"Erro ao obter autores: {str(e)}")
            return []

    async def tramitacao_materia(self, codigo_materia: str) -> List[Dict[str, Any]]:
        """
        Obter tramitação de uma matéria

        Endpoint: /materia/{codigo}/movimentacoes
        """
        try:
            url = f"{self.BASE_URL}/materia/{codigo_materia}/movimentacoes"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("movimentacoes", [])

        except Exception as e:
            logger.error(f"Erro ao obter tramitação: {str(e)}")
            return []

    async def votacoes_materia(self, codigo_materia: str) -> List[Dict[str, Any]]:
        """
        Obter votações de uma matéria

        Endpoint: /materia/{codigo}/votacoes
        """
        try:
            url = f"{self.BASE_URL}/materia/{codigo_materia}/votacoes"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("votacoes", [])

        except Exception as e:
            logger.error(f"Erro ao obter votações: {str(e)}")
            return []

    # ==================== SENADORES ====================

    async def listar_senadores(
        self,
        legislatura: Optional[int] = None,
        uf: Optional[str] = None,
        partido: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Listar senadores

        Endpoint: /senador/lista
        """
        try:
            params = {}

            if legislatura:
                params["legislatura"] = legislatura
            if uf:
                params["uf"] = uf
            if partido:
                params["partido"] = partido

            url = f"{self.BASE_URL}/senador/lista/atual"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("senadores", [])

        except Exception as e:
            logger.error(f"Erro ao listar senadores: {str(e)}")
            return []

    async def detalhe_senador(self, codigo_senador: str) -> Dict[str, Any]:
        """
        Obter detalhes de um senador

        Endpoint: /senador/{codigo}
        """
        try:
            url = f"{self.BASE_URL}/senador/{codigo_senador}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data

        except Exception as e:
            logger.error(f"Erro ao obter detalhes do senador: {str(e)}")
            return {}

    # ==================== SESSÕES E PLENÁRIO ====================

    async def listar_sessoes(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        tipo: Optional[str] = None  # Ordinária, Extraordinária, etc
    ) -> List[Dict[str, Any]]:
        """
        Listar sessões plenárias

        Endpoint: /sessao/lista
        """
        try:
            params = {}

            if data_inicio:
                params["dataInicio"] = data_inicio
            if data_fim:
                params["dataFim"] = data_fim
            if tipo:
                params["tipo"] = tipo

            url = f"{self.BASE_URL}/sessao/lista"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("sessoes", [])

        except Exception as e:
            logger.error(f"Erro ao listar sessões: {str(e)}")
            return []

    async def ordem_do_dia(self, data: str) -> List[Dict[str, Any]]:
        """
        Obter ordem do dia de uma sessão

        Endpoint: /sessao/{data}/pauta
        """
        try:
            url = f"{self.BASE_URL}/sessao/{data}/pauta"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("pauta", [])

        except Exception as e:
            logger.error(f"Erro ao obter ordem do dia: {str(e)}")
            return []

    # ==================== COMISSÕES ====================

    async def listar_comissoes(self) -> List[Dict[str, Any]]:
        """
        Listar comissões permanentes e temporárias

        Endpoint: /comissao/lista
        """
        try:
            url = f"{self.BASE_URL}/comissao/lista"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("comissoes", [])

        except Exception as e:
            logger.error(f"Erro ao listar comissões: {str(e)}")
            return []

    async def detalhe_comissao(self, codigo_comissao: str) -> Dict[str, Any]:
        """
        Obter detalhes de uma comissão

        Endpoint: /comissao/{codigo}
        """
        try:
            url = f"{self.BASE_URL}/comissao/{codigo_comissao}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data

        except Exception as e:
            logger.error(f"Erro ao obter detalhes da comissão: {str(e)}")
            return {}

    async def membros_comissao(self, codigo_comissao: str) -> List[Dict[str, Any]]:
        """
        Obter membros de uma comissão

        Endpoint: /comissao/{codigo}/membros
        """
        try:
            url = f"{self.BASE_URL}/comissao/{codigo_comissao}/membros"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("membros", [])

        except Exception as e:
            logger.error(f"Erro ao obter membros da comissão: {str(e)}")
            return []

    # ==================== MÉTODOS AUXILIARES ====================

    async def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Método auxiliar para fazer requisições com rate limiting e tratamento de erros

        Implementa:
        - Rate limiting (máximo 10 req/s conforme documentação oficial)
        - Retry automático para erros 429 e 503
        - Tratamento adequado de erros HTTP
        """
        # Rate limiting: garantir intervalo mínimo entre requisições
        current_time = time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)
        self._last_request_time = time()

        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, headers=self.headers) as response:
                        # Tratar erros específicos da API
                        if response.status == 429:
                            wait_time = 2 ** attempt  # Backoff exponencial
                            logger.warning(
                                f"Rate limit excedido (HTTP 429). Aguardando {wait_time}s antes de tentar novamente...")
                            await asyncio.sleep(wait_time)
                            continue

                        if response.status == 503:
                            wait_time = 2 ** attempt
                            logger.warning(
                                f"Serviço indisponível (HTTP 503). Aguardando {wait_time}s antes de tentar novamente...")
                            await asyncio.sleep(wait_time)
                            continue

                        response.raise_for_status()
                        data = await response.json()
                        return data

            except aiohttp.ClientResponseError as e:
                if e.status in [429, 503] and attempt < max_retries - 1:
                    continue  # Tentar novamente
                else:
                    logger.error(f"Erro HTTP {e.status} na requisição: {url}")
                    raise
            except Exception as e:
                logger.error(f"Erro na requisição para {url}: {str(e)}")
                raise

        return None

    async def buscar_por_palavra_chave(
        self,
        palavra_chave: str,
        tipo: str = "materia",  # materia ou norma
        ano: Optional[int] = None,
        quantidade: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Buscar matérias ou normas por palavra-chave
        """
        try:
            if tipo == "materia":
                # Buscar em matérias (projetos)
                params = {
                    "palavraChave": palavra_chave,
                    "quantidade": quantidade
                }
                if ano:
                    params["ano"] = ano

                url = f"{self.BASE_URL}/materia/pesquisa/lista"

            else:
                # Buscar em normas (leis)
                params = {
                    "palavraChave": palavra_chave,
                    "quantidade": quantidade
                }
                if ano:
                    params["ano"] = ano

                url = f"{self.BASE_URL}/norma/pesquisa/lista"

            data = await self._make_request(url, params=params)

            if not data:
                return []

            if tipo == "materia":
                return data.get("materias", [])
            else:
                return data.get("normas", [])

        except Exception as e:
            logger.error(f"Erro na busca por palavra-chave: {str(e)}")
            return []

    async def coletar_tudo_periodo(
        self,
        ano_inicio: int,
        ano_fim: int,
        tipo: str = "norma"  # norma ou materia
    ) -> List[Dict[str, Any]]:
        """
        Coletar todas as normas/matérias de um período
        """
        todos_documentos = []

        for ano in range(ano_inicio, ano_fim + 1):
            logger.info(f"Coletando {tipo}s de {ano}...")

            pagina = 1
            while True:
                if tipo == "norma":
                    resultado = await self.listar_normas(
                        ano=ano,
                        pagina=pagina,
                        quantidade=100
                    )
                    documentos = resultado.get("normas", [])
                else:
                    resultado = await self.listar_materias(
                        ano=ano,
                        pagina=pagina,
                        quantidade=100
                    )
                    documentos = resultado.get("materias", [])

                if not documentos:
                    break

                todos_documentos.extend(documentos)
                logger.info(f"  Página {pagina}: {len(documentos)} {tipo}s")

                pagina += 1

                # Limite de segurança
                if pagina > 100:
                    logger.warning(
                        f"Limite de páginas atingido para ano {ano}")
                    break

        return todos_documentos

    # ==================== MÉTODOS DE COMPATIBILIDADE ====================
    # Estes métodos mantêm compatibilidade com código que usa a interface
    # do SenadoAPIClient em legislative_apis.py

    async def search_legislation(
        self,
        keywords: Optional[str] = None,
        year: Optional[int] = None,
        tipo: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Buscar legislação no Senado usando endpoints oficiais

        Args:
            keywords: Palavras-chave para busca
            year: Ano da legislação
            tipo: Tipo de legislação (LEI, DEC, MPV, etc)
            limit: Limite de resultados

        Returns:
            Lista de legislações encontradas
        """
        try:
            # Se tem keywords, usar endpoint oficial de legislação
            if keywords:
                try:
                    # Expandir termos comuns (ex: AI -> inteligência artificial)
                    expanded_keywords = keywords
                    keywords_lower = keywords.lower()
                    if 'ai' in keywords_lower or 'inteligência artificial' in keywords_lower or 'inteligencia artificial' in keywords_lower:
                        expanded_keywords = f"{keywords} inteligência artificial IA"

                    # Buscar legislações recentes (últimos 5 anos se não especificado ano)
                    search_years = [year] if year else [
                        2025, 2024, 2023, 2022, 2021]
                    all_normas = []

                    # Limitar a 3 anos para não sobrecarregar
                    for search_year in search_years[:3]:
                        try:
                            legislacao_result = await self.legislacao_lista(
                                ano=search_year,
                                tipo=tipo if tipo else None,
                                quantidade=limit * 2
                            )

                            # Extrair normas
                            normas = []
                            if isinstance(legislacao_result, dict):
                                normas = legislacao_result.get(
                                    "normas", legislacao_result.get("dados", []))
                            elif isinstance(legislacao_result, list):
                                normas = legislacao_result

                            all_normas.extend(normas)

                            # Se já encontrou resultados suficientes, parar
                            if len(all_normas) >= limit * 3:
                                break
                        except Exception as e:
                            logger.debug(
                                f"Erro ao buscar legislação do ano {search_year}: {str(e)}")
                            continue

                    # Filtrar por palavras-chave (tentar todas as variações)
                    keywords_variations = [
                        keywords.lower(),
                        expanded_keywords.lower(),
                        'inteligência artificial',
                        'inteligencia artificial',
                        'ia',
                        'ai'
                    ]

                    filtered_normas = []
                    for n in all_normas:
                        descricao = str(n.get("descricao", "")).lower()
                        titulo = str(n.get("titulo", "")).lower()
                        nome = str(n.get("nome", "")).lower()
                        texto_completo = f"{descricao} {titulo} {nome}"

                        # Verificar se alguma variação da keyword está presente
                        for kw in keywords_variations:
                            if kw in texto_completo:
                                filtered_normas.append(n)
                                break

                    # Se não encontrou com filtro, retornar algumas normas recentes
                    if not filtered_normas and all_normas:
                        return all_normas[:limit]

                    return filtered_normas[:limit]

                except Exception as e:
                    logger.debug(
                        f"Erro ao buscar legislação por keywords: {str(e)}")
                    # Fallback: buscar diretamente por ano/tipo
                    pass

            # Se não tem keywords ou erro, listar por ano/tipo usando endpoint oficial
            try:
                legislacao_result = await self.legislacao_lista(
                    ano=year,
                    tipo=tipo if tipo else None,
                    quantidade=limit
                )

                normas = []
                if isinstance(legislacao_result, dict):
                    normas = legislacao_result.get(
                        "normas", legislacao_result.get("dados", []))
                elif isinstance(legislacao_result, list):
                    normas = legislacao_result

                return normas[:limit]
            except Exception as e:
                logger.debug(f"Erro ao buscar legislação: {str(e)}")
                # Fallback para métodos legados apenas se endpoint oficial falhar
                if tipo and tipo in ["PLS", "PEC", "PLC"]:
                    resultado = await self.listar_materias(
                        ano=year,
                        sigla=tipo,
                        quantidade=limit
                    )
                    return resultado.get("materias", [])[:limit]
                else:
                    resultado = await self.listar_normas(
                        ano=year,
                        tipo=tipo,
                        quantidade=limit
                    )
                    return resultado.get("normas", [])[:limit]

        except Exception as e:
            logger.error(f"Erro ao buscar legislação: {str(e)}")
            return []

    async def get_legislation_by_id(
        self,
        legislation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obter detalhes de uma legislação específica (método de compatibilidade)

        Args:
            legislation_id: ID ou código da legislação

        Returns:
            Detalhes da legislação
        """
        try:
            # Tentar como norma primeiro
            detalhes = await self.detalhe_norma(legislation_id)
            if detalhes and detalhes.get("norma"):
                return detalhes.get("norma", detalhes)

            # Se não encontrou, tentar como matéria
            detalhes = await self.detalhe_materia(legislation_id)
            if detalhes and detalhes.get("materia"):
                return detalhes.get("materia", detalhes)

            return detalhes if detalhes else None

        except Exception as e:
            logger.error(
                f"Erro ao obter legislação {legislation_id}: {str(e)}")
            return None

    async def get_legislation_full_text(
        self,
        legislation_id: str
    ) -> Optional[str]:
        """
        Obter texto completo de uma legislação (método de compatibilidade)

        Args:
            legislation_id: ID ou código da legislação

        Returns:
            Texto completo da legislação
        """
        try:
            # Tentar como norma primeiro
            texto = await self.texto_norma(legislation_id)
            if texto:
                return texto

            # Se não encontrou, tentar como matéria
            texto = await self.texto_materia(legislation_id)
            return texto

        except Exception as e:
            logger.error(f"Erro ao obter texto completo: {str(e)}")
            return None

    async def search_projects_of_law(
        self,
        year: Optional[int] = None,
        keywords: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Buscar projetos de lei (PLS) no Senado (método de compatibilidade)

        Args:
            year: Ano do projeto
            keywords: Palavras-chave
            limit: Limite de resultados

        Returns:
            Lista de projetos de lei
        """
        try:
            if keywords:
                resultados = await self.buscar_por_palavra_chave(
                    palavra_chave=keywords,
                    tipo="materia",
                    ano=year,
                    quantidade=limit
                )
                # Filtrar apenas PLS
                pls_results = [
                    r for r in resultados
                    if r.get("siglaTipo", "").upper() in ["PLS", "PLC", "PEC"]
                ]
                return pls_results[:limit]
            else:
                resultado = await self.listar_materias(
                    ano=year,
                    sigla="PLS",
                    quantidade=limit
                )
                return resultado.get("materias", [])[:limit]

        except Exception as e:
            logger.error(f"Erro ao buscar projetos de lei: {str(e)}")
            return []


# Instância global
senado_client = SenadoAPIClient()
