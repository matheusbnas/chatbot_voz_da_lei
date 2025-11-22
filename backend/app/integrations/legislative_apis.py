import aiohttp
import xml.etree.ElementTree as ET
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
from urllib.parse import quote

from app.core.config import settings


class CamaraAPIClient:
    """Cliente para API da Câmara dos Deputados"""

    BASE_URL = settings.CAMARA_API_URL

    async def search_propositions(
        self,
        keywords: Optional[str] = None,
        year: Optional[int] = None,
        author: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Buscar proposições (PLs, PECs, etc)

        Args:
            keywords: Palavras-chave para busca
            year: Ano da proposição
            author: Nome do autor
            limit: Número máximo de resultados

        Returns:
            Lista de proposições
        """
        try:
            params = {
                "itens": limit,
                "ordem": "DESC",
                "ordenarPor": "id"
            }

            if keywords:
                params["keywords"] = keywords
            if year:
                params["ano"] = year
            if author:
                params["autor"] = author

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/proposicoes",
                    params=params
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("dados", [])

        except Exception as e:
            logger.error(f"Erro ao buscar proposições: {str(e)}")
            return []

    async def get_proposition_details(self, proposition_id: int) -> Optional[Dict[str, Any]]:
        """
        Obter detalhes de uma proposição específica

        Args:
            proposition_id: ID da proposição

        Returns:
            Detalhes da proposição
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/proposicoes/{proposition_id}"
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("dados", {})

        except Exception as e:
            logger.error(
                f"Erro ao obter detalhes da proposição {proposition_id}: {str(e)}")
            return None

    async def get_proposition_full_text(self, proposition_id: int) -> Optional[str]:
        """
        Obter texto completo de uma proposição

        Args:
            proposition_id: ID da proposição

        Returns:
            Texto completo da proposição
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Buscar arquivos da proposição
                async with session.get(
                    f"{self.BASE_URL}/proposicoes/{proposition_id}/arquivos"
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    arquivos = data.get("dados", [])

                    # Encontrar o arquivo de texto integral
                    for arquivo in arquivos:
                        if "Texto integral" in arquivo.get("descricao", ""):
                            # Baixar o arquivo
                            url = arquivo.get("url")
                            if url:
                                async with session.get(url) as text_response:
                                    if text_response.status == 200:
                                        # Aqui você precisaria processar o PDF/DOC
                                        # Por simplicidade, retornamos a URL
                                        return url

                    return None

        except Exception as e:
            logger.error(
                f"Erro ao obter texto da proposição {proposition_id}: {str(e)}")
            return None

    async def get_proposition_authors(self, proposition_id: int) -> List[Dict[str, Any]]:
        """
        Obter autores de uma proposição

        Args:
            proposition_id: ID da proposição

        Returns:
            Lista de autores
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/proposicoes/{proposition_id}/autores"
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("dados", [])

        except Exception as e:
            logger.error(
                f"Erro ao obter autores da proposição {proposition_id}: {str(e)}")
            return []

    async def get_proposition_votes(self, proposition_id: int) -> List[Dict[str, Any]]:
        """
        Obter votações de uma proposição

        Args:
            proposition_id: ID da proposição

        Returns:
            Lista de votações
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/proposicoes/{proposition_id}/votacoes"
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("dados", [])

        except Exception as e:
            logger.error(
                f"Erro ao obter votações da proposição {proposition_id}: {str(e)}")
            return []

    async def get_trending_topics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obter tópicos em destaque (proposições mais recentes)

        Args:
            limit: Número de tópicos

        Returns:
            Lista de proposições em destaque
        """
        try:
            # Buscar proposições mais recentes
            params = {
                "itens": limit,
                "ordem": "DESC",
                "ordenarPor": "id",
                "ano": datetime.now().year
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/proposicoes",
                    params=params
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("dados", [])

        except Exception as e:
            logger.error(f"Erro ao obter tópicos em destaque: {str(e)}")
            return []


class SenadoAPIClient:
    """
    Cliente para API de Dados Abertos do Senado Federal

    Documentação: https://legis.senado.leg.br/dadosabertos/api-docs/swagger-ui/index.html
    A API foi modernizada e agora usa FastAPI com endpoints REST/JSON.
    """

    BASE_URL = settings.SENADO_API_URL

    async def search_legislation(
        self,
        keywords: Optional[str] = None,
        year: Optional[int] = None,
        tipo: Optional[str] = None,  # PLS, PEC, etc
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Buscar legislação no Senado

        Args:
            keywords: Palavras-chave para busca
            year: Ano da legislação
            tipo: Tipo de legislação (PLS, PEC, etc)
            limit: Limite de resultados

        Returns:
            Lista de legislações encontradas
        """
        try:
            params = {}

            if keywords:
                params["busca"] = keywords
            if year:
                params["ano"] = year
            if tipo:
                params["tipo"] = tipo

            # A API do Senado modernizada usa endpoints REST
            # Endpoint: /legislacao ou /materia (dependendo da versão)
            async with aiohttp.ClientSession() as session:
                # Tentar endpoint de legislação
                async with session.get(
                    f"{self.BASE_URL}/legislacao",
                    params=params,
                    headers={"Accept": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # A estrutura pode variar, adaptar conforme necessário
                        if isinstance(data, list):
                            return data[:limit]
                        elif isinstance(data, dict):
                            return data.get("dados", data.get("items", []))[:limit]
                        return []
                    elif response.status == 404:
                        # Tentar endpoint alternativo de matérias
                        return await self._search_matters_legacy(keywords, year, limit)
                    else:
                        response.raise_for_status()
                        return []

        except aiohttp.ClientError as e:
            logger.error(
                f"Erro de conexão ao buscar legislação do Senado: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Erro ao buscar legislação do Senado: {str(e)}")
            return []

    async def _search_matters_legacy(
        self,
        keywords: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Buscar matérias usando endpoint legado (XML)

        Args:
            keywords: Palavras-chave
            year: Ano
            limit: Limite de resultados

        Returns:
            Lista de matérias
        """
        try:
            params = {}
            if year:
                params["ano"] = year

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/materia/pesquisa/lista",
                    params=params,
                    headers={"Accept": "application/xml, application/json"}
                ) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")

                        # Se for JSON
                        if "json" in content_type.lower():
                            data = await response.json()
                            return data.get("dados", [])[:limit]

                        # Se for XML, processar
                        elif "xml" in content_type.lower():
                            xml_content = await response.text()
                            return self._parse_senado_xml(xml_content, limit)

                    return []

        except Exception as e:
            logger.debug(f"Erro ao buscar matérias (legado): {str(e)}")
            return []

    def _parse_senado_xml(self, xml_content: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Parsear XML do Senado (formato legado)

        Args:
            xml_content: Conteúdo XML
            limit: Limite de resultados

        Returns:
            Lista de matérias parseadas
        """
        try:
            root = ET.fromstring(xml_content)
            matters = []

            # Estrutura XML do Senado pode variar
            # Adaptar conforme a estrutura real
            for materia in root.findall('.//Materia')[:limit]:
                matter_data = {
                    "id": materia.findtext("Codigo", ""),
                    "numero": materia.findtext("Numero", ""),
                    "ano": materia.findtext("Ano", ""),
                    "tipo": materia.findtext("SiglaSubtipoMateria", ""),
                    "ementa": materia.findtext("Ementa", ""),
                    "data_apresentacao": materia.findtext("DataApresentacao", ""),
                    "autor": materia.findtext("Autor", ""),
                }
                matters.append(matter_data)

            return matters

        except ET.ParseError as e:
            logger.debug(f"Erro ao parsear XML do Senado: {str(e)}")
            return []
        except Exception as e:
            logger.debug(f"Erro ao processar XML: {str(e)}")
            return []

    async def get_legislation_by_id(
        self,
        legislation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obter detalhes de uma legislação específica

        Args:
            legislation_id: ID ou código da legislação

        Returns:
            Detalhes da legislação
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Tentar endpoint moderno
                async with session.get(
                    f"{self.BASE_URL}/legislacao/{legislation_id}",
                    headers={"Accept": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("dados", data) if isinstance(data, dict) else data
                    elif response.status == 404:
                        # Tentar endpoint de matéria
                        return await self._get_matter_by_id(legislation_id)
                    else:
                        response.raise_for_status()
                        return None

        except Exception as e:
            logger.error(
                f"Erro ao obter legislação {legislation_id}: {str(e)}")
            return None

    async def _get_matter_by_id(self, matter_id: str) -> Optional[Dict[str, Any]]:
        """Obter matéria por ID (endpoint legado)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/materia/{matter_id}",
                    headers={"Accept": "application/json, application/xml"}
                ) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        if "json" in content_type.lower():
                            data = await response.json()
                            return data.get("dados", data)
                        else:
                            xml_content = await response.text()
                            # Processar XML se necessário
                            return {"id": matter_id, "raw_xml": xml_content}
                    return None
        except Exception as e:
            logger.debug(f"Erro ao obter matéria {matter_id}: {str(e)}")
            return None

    async def get_legislation_full_text(
        self,
        legislation_id: str
    ) -> Optional[str]:
        """
        Obter texto completo de uma legislação

        Args:
            legislation_id: ID ou código da legislação

        Returns:
            Texto completo da legislação
        """
        try:
            # Tentar obter texto completo via endpoint específico
            async with aiohttp.ClientSession() as session:
                # Endpoint para texto integral
                async with session.get(
                    f"{self.BASE_URL}/legislacao/{legislation_id}/texto-integral",
                    headers={
                        "Accept": "application/json, text/plain, application/xml"}
                ) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")

                        if "json" in content_type.lower():
                            data = await response.json()
                            # O texto pode estar em diferentes campos
                            return data.get("texto", data.get("conteudo", data.get("textoIntegral", "")))
                        elif "xml" in content_type.lower():
                            xml_content = await response.text()
                            # Extrair texto do XML
                            return self._extract_text_from_senado_xml(xml_content)
                        else:
                            # Texto plano
                            return await response.text()

                # Se não encontrou, tentar obter via detalhes da legislação
                details = await self.get_legislation_by_id(legislation_id)
                if details:
                    # O texto pode estar nos detalhes
                    return details.get("textoIntegral", details.get("texto", details.get("conteudo", "")))

            return None

        except Exception as e:
            logger.error(
                f"Erro ao obter texto completo da legislação {legislation_id}: {str(e)}")
            return None

    def _extract_text_from_senado_xml(self, xml_content: str) -> Optional[str]:
        """
        Extrair texto do XML do Senado

        Args:
            xml_content: Conteúdo XML

        Returns:
            Texto extraído
        """
        try:
            root = ET.fromstring(xml_content)
            text_parts = []

            # Buscar elementos de texto (estrutura pode variar)
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    tag = elem.tag.lower()
                    # Filtrar tags de metadados
                    if tag not in ['codigo', 'numero', 'ano', 'data', 'autor']:
                        text_parts.append(elem.text.strip())

            return "\n".join(text_parts) if text_parts else None

        except ET.ParseError as e:
            logger.debug(f"Erro ao parsear XML do Senado: {str(e)}")
            return None
        except Exception as e:
            logger.debug(f"Erro ao extrair texto: {str(e)}")
            return None

    async def search_projects_of_law(
        self,
        year: Optional[int] = None,
        keywords: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Buscar projetos de lei (PLS) no Senado

        Args:
            year: Ano do projeto
            keywords: Palavras-chave
            limit: Limite de resultados

        Returns:
            Lista de projetos de lei
        """
        return await self.search_legislation(
            keywords=keywords,
            year=year,
            tipo="PLS",
            limit=limit
        )


class QueridoDiarioClient:
    """Cliente para API do Querido Diário"""

    BASE_URL = settings.QUERIDO_DIARIO_API_URL

    async def search_gazettes(
        self,
        city: str,
        state: str,
        keywords: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Buscar diários oficiais municipais

        Args:
            city: Nome da cidade
            state: Sigla do estado
            keywords: Palavras-chave para buscar no conteúdo
            start_date: Data início (YYYY-MM-DD)
            end_date: Data fim (YYYY-MM-DD)

        Returns:
            Lista de publicações
        """
        try:
            params = {
                "territory_name": city,
                "state_code": state.upper()
            }

            if keywords:
                params["querystring"] = keywords
            if start_date:
                params["published_since"] = start_date
            if end_date:
                params["published_until"] = end_date

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/gazettes",
                    params=params
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data.get("gazettes", [])

        except Exception as e:
            logger.error(f"Erro ao buscar diários oficiais: {str(e)}")
            return []


class LexMLClient:
    """Cliente para API do LexML - Rede de Informação Legislativa e Jurídica"""

    BASE_URL = settings.LEXML_API_URL

    def _parse_lexml_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """
        Parsear resposta XML do LexML baseado na estrutura SRU real

        Args:
            xml_content: Conteúdo XML da resposta

        Returns:
            Lista de documentos parseados
        """
        try:
            root = ET.fromstring(xml_content)

            # Namespaces do SRU
            namespaces = {
                'srw': 'http://www.loc.gov/zing/srw/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'srw_dc': 'info:srw/schema/1/dc-schema'
            }

            records = []
            for record in root.findall('.//srw:record', namespaces):
                record_data = record.find('.//srw_dc:dc', namespaces)
                if record_data is None:
                    continue

                doc = {}

                # Extrair campos principais (sem namespace para campos customizados)
                tipo_doc = record_data.find('tipoDocumento')
                if tipo_doc is not None:
                    doc['tipo_documento'] = tipo_doc.text

                # Facet tipo documento
                facet_tipo = record_data.find('facet-tipoDocumento')
                if facet_tipo is not None:
                    doc['facet_tipo_documento'] = facet_tipo.text

                urn = record_data.find('urn')
                if urn is not None:
                    doc['urn'] = urn.text
                    doc['identifier'] = urn.text

                # Campos Dublin Core (com namespace)
                title = record_data.find('.//dc:title', namespaces)
                if title is not None:
                    doc['title'] = title.text

                description = record_data.find('.//dc:description', namespaces)
                if description is not None:
                    doc['description'] = description.text

                date = record_data.find('.//dc:date', namespaces)
                if date is not None:
                    doc['date'] = date.text

                dc_type = record_data.find('.//dc:type', namespaces)
                if dc_type is not None:
                    doc['dc_type'] = dc_type.text

                # Campos customizados do LexML (sem namespace)
                localidade = record_data.find('localidade')
                if localidade is not None:
                    doc['localidade'] = localidade.text

                facet_localidade = record_data.find('facet-localidade')
                if facet_localidade is not None:
                    doc['facet_localidade'] = facet_localidade.text

                autoridade = record_data.find('autoridade')
                if autoridade is not None:
                    doc['autoridade'] = autoridade.text

                facet_autoridade = record_data.find('facet-autoridade')
                if facet_autoridade is not None:
                    doc['facet_autoridade'] = facet_autoridade.text

                # Identifier Dublin Core
                identifier = record_data.find('.//dc:identifier', namespaces)
                if identifier is not None:
                    doc['lexml_id'] = identifier.text

                records.append(doc)

            return records

        except ET.ParseError as e:
            logger.error(f"Erro ao parsear XML do LexML: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Erro ao processar resposta do LexML: {str(e)}")
            return []

    async def search(
        self,
        query: str,
        start_record: int = 1,
        maximum_records: int = 20,
        record_schema: str = "dc"
    ) -> Dict[str, Any]:
        """
        Buscar documentos no LexML usando SRU

        Args:
            query: Query SRU (ex: 'urn="senado.federal pls 2008"')
            start_record: Registro inicial (para paginação)
            maximum_records: Número máximo de registros
            record_schema: Schema dos registros (dc, mods, etc)

        Returns:
            Dict com 'total', 'records' e 'next_start'
        """
        try:
            params = {
                "operation": "searchRetrieve",
                "query": query,
                "startRecord": str(start_record),
                "maximumRecords": str(maximum_records),
                "recordPacking": "xml",
                "recordSchema": record_schema
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.BASE_URL,
                    params=params,
                    headers={"Accept": "application/xml"}
                ) as response:
                    response.raise_for_status()
                    xml_content = await response.text()

                    # Parsear XML
                    root = ET.fromstring(xml_content)
                    namespaces = {'srw': 'http://www.loc.gov/zing/srw/'}

                    # Obter número total de registros
                    number_of_records = root.find(
                        './/srw:numberOfRecords', namespaces)
                    total = int(
                        number_of_records.text) if number_of_records is not None else 0

                    # Parsear registros
                    records = self._parse_lexml_xml(xml_content)

                    # Calcular próximo registro
                    next_start = start_record + maximum_records if start_record + \
                        maximum_records <= total else None

                    return {
                        "total": total,
                        "records": records,
                        "start_record": start_record,
                        "maximum_records": maximum_records,
                        "next_start": next_start
                    }

        except Exception as e:
            logger.error(f"Erro ao buscar no LexML: {str(e)}")
            return {
                "total": 0,
                "records": [],
                "start_record": start_record,
                "maximum_records": maximum_records,
                "next_start": None
            }

    async def search_by_urn(
        self,
        urn: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Buscar por URN específica

        Args:
            urn: URN do documento (ex: 'senado.federal pls 2008')
            limit: Limite de resultados

        Returns:
            Lista de documentos
        """
        query = f'urn="{urn}"'
        result = await self.search(query, maximum_records=limit)
        return result.get("records", [])

    async def search_by_keywords(
        self,
        keywords: str,
        year: Optional[int] = None,
        tipo_documento: Optional[str] = None,
        autoridade: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Buscar por palavras-chave

        Args:
            keywords: Palavras-chave para busca
            year: Ano do documento
            tipo_documento: Tipo de documento (Lei, Projeto de Lei, etc)
            autoridade: Autoridade (Senado Federal, Câmara dos Deputados, etc)
            limit: Limite de resultados

        Returns:
            Lista de documentos
        """
        # Construir query SRU
        query_parts = []

        if keywords:
            # Buscar em título e descrição
            query_parts.append(
                f'dc.title all "{keywords}" or dc.description all "{keywords}"')

        if year:
            query_parts.append(f'dc.date="{year}"')

        if tipo_documento:
            query_parts.append(f'tipoDocumento="{tipo_documento}"')

        if autoridade:
            query_parts.append(f'autoridade="{autoridade}"')

        query = " and ".join(
            query_parts) if query_parts else f'dc.title all "{keywords}"'

        result = await self.search(query, maximum_records=limit)
        return result.get("records", [])

    async def search_projects_of_law(
        self,
        year: Optional[int] = None,
        house: Optional[str] = None,  # 'senado' ou 'camara'
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Buscar projetos de lei

        Args:
            year: Ano do projeto
            house: Casa legislativa ('senado' ou 'camara')
            limit: Limite de resultados

        Returns:
            Lista de projetos de lei
        """
        query_parts = ['tipoDocumento="Projeto de Lei"']

        if year:
            query_parts.append(f'dc.date="{year}"')

        if house == 'senado':
            query_parts.append('autoridade="Senado Federal"')
        elif house == 'camara':
            query_parts.append('autoridade="Câmara dos Deputados"')

        query = " and ".join(query_parts)
        result = await self.search(query, maximum_records=limit)
        return result.get("records", [])

    async def search_laws(
        self,
        year: Optional[int] = None,
        keywords: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Buscar leis

        Args:
            year: Ano da lei
            keywords: Palavras-chave
            limit: Limite de resultados

        Returns:
            Lista de leis
        """
        query_parts = ['tipoDocumento="Lei"']

        if year:
            query_parts.append(f'dc.date="{year}"')

        if keywords:
            query_parts.append(
                f'dc.title all "{keywords}" or dc.description all "{keywords}"')

        query = " and ".join(query_parts)
        result = await self.search(query, maximum_records=limit)
        return result.get("records", [])

    async def get_document_by_urn(self, urn: str) -> Optional[Dict[str, Any]]:
        """
        Obter documento específico por URN

        Args:
            urn: URN completa do documento (ex: 'urn:lex:br:senado.federal:projeto.lei;pls:2008;489')

        Returns:
            Documento ou None
        """
        # Normalizar URN para busca
        if "urn:lex:" in urn:
            # Extrair parte relevante da URN para busca
            # Ex: "urn:lex:br:senado.federal:projeto.lei;pls:2008;489" -> "senado.federal pls 2008"
            urn_clean = urn.replace("urn:lex:br:", "").replace("urn:lex:", "")
            # Extrair componentes da URN
            parts = urn_clean.split(":")
            if len(parts) >= 2:
                # Formato: senado.federal:projeto.lei;pls:2008;489
                authority = parts[0]  # senado.federal
                doc_type = parts[1].split(";")[0]  # projeto.lei
                if "pls" in doc_type or "pl" in doc_type.lower():
                    # Tentar extrair número e ano
                    if len(parts) > 2:
                        year = parts[2] if parts[2].isdigit() else None
                        number = parts[3] if len(parts) > 3 else None
                        if year:
                            query = f'urn="{authority} pls {year}"'
                        else:
                            query = f'urn="{urn_clean}"'
                    else:
                        query = f'urn="{urn_clean}"'
                else:
                    query = f'urn="{urn_clean}"'
            else:
                query = f'urn="{urn_clean}"'
        else:
            query = f'urn="{urn}"'

        result = await self.search(query, maximum_records=1)
        records = result.get("records", [])
        if records:
            doc = records[0]
            # Tentar buscar texto completo se disponível
            full_text = await self._get_document_full_text(doc.get("urn"))
            if full_text:
                doc['full_text'] = full_text
            return doc
        return None

    async def _get_document_full_text(self, urn: Optional[str]) -> Optional[str]:
        """
        Obter o texto completo do documento através da URN

        O LexML fornece documentos em XML. Este método busca o XML completo
        e extrai o texto estruturado (artigos, parágrafos, incisos, etc).

        Args:
            urn: URN do documento (ex: 'urn:lex:br:senado.federal:projeto.lei;pls:2008;489')

        Returns:
            Texto completo formatado ou None
        """
        if not urn:
            return None

        try:
            # Normalizar URN
            if not urn.startswith("urn:lex:"):
                urn = f"urn:lex:br:{urn}" if not urn.startswith(
                    "urn:lex:br:") else urn

            # Tentar diferentes endpoints do LexML para obter o XML completo
            # O LexML pode fornecer o documento em diferentes formatos
            urls_to_try = [
                # Tentar endpoint direto do documento (mais provável de ter o XML completo)
                f"https://www.lexml.gov.br/documento/{quote(urn, safe='')}",
                f"https://www.lexml.gov.br/documento/{urn}",
                # Tentar com formato XML explícito
                f"https://www.lexml.gov.br/documento/{quote(urn, safe='')}?formato=xml",
                # Tentar endpoint de download/export
                f"https://www.lexml.gov.br/documento/{quote(urn, safe='')}/xml",
                # Última opção: buscar via SRU com schema lexml (pode retornar XML completo)
                f"https://www.lexml.gov.br/busca/SRU?operation=searchRetrieve&query=urn%3D%22{quote(urn, safe='')}%22&recordSchema=lexml&maximumRecords=1",
            ]

            async with aiohttp.ClientSession() as session:
                for url in urls_to_try:
                    try:
                        async with session.get(
                            url,
                            headers={
                                "Accept": "application/xml, text/xml, */*"},
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                content_type = response.headers.get(
                                    "Content-Type", "")

                                # Se for XML, processar
                                if "xml" in content_type.lower():
                                    xml_content = await response.text()

                                    # Verificar se é XML SRU (metadados) ou XML LexML (documento completo)
                                    if "searchRetrieveResponse" in xml_content or "srw:" in xml_content:
                                        # É XML SRU (metadados), não o documento completo
                                        # Tentar extrair referência ao documento completo
                                        logger.debug(
                                            f"Recebido XML SRU (metadados) para {urn}, tentando obter documento completo")
                                        # Continuar para próxima URL
                                        continue

                                    # Extrair texto do XML LexML
                                    text = self._extract_text_from_lexml_xml(
                                        xml_content)
                                    if text and len(text) > 200:  # Texto significativo
                                        return text

                                # Se for HTML, tentar extrair texto
                                elif "html" in content_type.lower():
                                    html_content = await response.text()
                                    # Extrair texto do HTML (simplificado)
                                    text = self._extract_text_from_html(
                                        html_content)
                                    if text:
                                        return text

                                # Se for texto plano
                                else:
                                    text = await response.text()
                                    if text and len(text) > 100:  # Texto significativo
                                        return text
                    except Exception as e:
                        logger.debug(f"Erro ao tentar URL {url}: {str(e)}")
                        continue

            logger.warning(
                f"Não foi possível obter texto completo para URN {urn}")
            return None

        except Exception as e:
            logger.debug(
                f"Não foi possível obter texto completo para URN {urn}: {str(e)}")
            return None

    def _extract_text_from_lexml_xml(self, xml_content: str) -> Optional[str]:
        """
        Extrair texto estruturado do XML LexML

        O LexML usa uma estrutura XML específica com elementos como:
        - Artigo, Paragrafo, Inciso, Alinea
        - Texto, Rotulo, etc.

        Args:
            xml_content: Conteúdo XML do LexML

        Returns:
            Texto formatado ou None
        """
        try:
            root = ET.fromstring(xml_content)

            # Verificar se é XML SRU (metadados) - não processar
            if root.tag.endswith('searchRetrieveResponse') or 'srw:' in root.tag:
                return None

            # Namespaces comuns do LexML (tentar diferentes variações)
            namespaces_list = [
                {'lexml': 'http://www.lexml.gov.br/1.0'},
                {'': 'http://www.lexml.gov.br/1.0'},
                {},  # Sem namespace
            ]

            text_parts = []

            # Tentar com diferentes namespaces
            for namespaces in namespaces_list:
                # Buscar artigos (com diferentes variações de case)
                for tag_variation in ['Artigo', 'artigo', 'ARTIGO']:
                    artigos = root.findall(
                        f'.//{tag_variation}', namespaces) if namespaces else root.findall(f'.//{tag_variation}')
                    for artigo in artigos:
                        # Buscar rótulo
                        for rotulo_tag in ['Rotulo', 'rotulo', 'ROTULO', 'Label', 'label']:
                            rotulo = artigo.find(
                                f'.//{rotulo_tag}', namespaces) if namespaces else artigo.find(f'.//{rotulo_tag}')
                            if rotulo is not None and rotulo.text:
                                text_parts.append(f"\n{rotulo.text.strip()}")
                                break

                        # Buscar parágrafos
                        for par_tag in ['Paragrafo', 'paragrafo', 'PARAGRAFO', 'Paragraphe']:
                            paragrafos = artigo.findall(
                                f'.//{par_tag}', namespaces) if namespaces else artigo.findall(f'.//{par_tag}')
                            for paragrafo in paragrafos:
                                # Rótulo do parágrafo
                                for rotulo_tag in ['Rotulo', 'rotulo', 'ROTULO']:
                                    par_rotulo = paragrafo.find(
                                        f'.//{rotulo_tag}', namespaces) if namespaces else paragrafo.find(f'.//{rotulo_tag}')
                                    if par_rotulo is not None and par_rotulo.text:
                                        text_parts.append(
                                            f"\n{par_rotulo.text.strip()}")
                                        break

                                # Texto do parágrafo
                                for texto_tag in ['Texto', 'texto', 'TEXTO', 'Text', 'text', 'Conteudo', 'conteudo']:
                                    texto = paragrafo.find(
                                        f'.//{texto_tag}', namespaces) if namespaces else paragrafo.find(f'.//{texto_tag}')
                                    if texto is not None and texto.text and texto.text.strip():
                                        text_parts.append(texto.text.strip())
                                        break

                        # Buscar incisos
                        for inc_tag in ['Inciso', 'inciso', 'INCISO']:
                            incisos = artigo.findall(
                                f'.//{inc_tag}', namespaces) if namespaces else artigo.findall(f'.//{inc_tag}')
                            for inciso in incisos:
                                # Rótulo do inciso
                                for rotulo_tag in ['Rotulo', 'rotulo', 'ROTULO']:
                                    inc_rotulo = inciso.find(
                                        f'.//{rotulo_tag}', namespaces) if namespaces else inciso.find(f'.//{rotulo_tag}')
                                    if inc_rotulo is not None and inc_rotulo.text:
                                        text_parts.append(
                                            f"\n{inc_rotulo.text.strip()}")
                                        break

                                # Texto do inciso
                                for texto_tag in ['Texto', 'texto', 'TEXTO']:
                                    texto = inciso.find(
                                        f'.//{texto_tag}', namespaces) if namespaces else inciso.find(f'.//{texto_tag}')
                                    if texto is not None and texto.text and texto.text.strip():
                                        text_parts.append(texto.text.strip())
                                        break

                # Se encontrou texto, parar de tentar outros namespaces
                if text_parts:
                    break

            # Se não encontrou estrutura específica, extrair todo o texto de forma genérica
            if not text_parts or len(''.join(text_parts)) < 100:
                # Função recursiva para extrair todo o texto
                def extract_all_text(elem, depth=0):
                    """Extrair todo o texto de um elemento recursivamente"""
                    texts = []
                    # Texto direto do elemento
                    if elem.text and elem.text.strip():
                        texts.append(elem.text.strip())
                    # Texto dos filhos
                    for child in elem:
                        child_texts = extract_all_text(child, depth + 1)
                        if child_texts:
                            texts.extend(child_texts)
                    # Texto após os filhos (tail)
                    if elem.tail and elem.tail.strip():
                        texts.append(elem.tail.strip())
                    return texts

                all_texts = extract_all_text(root)
                if all_texts:
                    # Filtrar textos muito curtos ou que parecem ser metadados
                    filtered_texts = [t for t in all_texts if len(
                        t) > 10 and not t.isdigit()]
                    if filtered_texts:
                        text_parts.extend(filtered_texts)

            # Juntar e limpar
            result = "\n".join(text_parts).strip() if text_parts else None

            # Verificar se o resultado é significativo (não apenas metadados)
            if result and len(result) > 200:
                return result

            return None

        except ET.ParseError as e:
            logger.debug(f"Erro ao parsear XML LexML: {str(e)}")
            return None
        except Exception as e:
            logger.debug(f"Erro ao extrair texto do XML: {str(e)}")
            return None

    def _extract_text_from_html(self, html_content: str) -> Optional[str]:
        """
        Extrair texto de HTML (simplificado)

        Args:
            html_content: Conteúdo HTML

        Returns:
            Texto extraído ou None
        """
        try:
            # Remover tags HTML básicas e extrair texto
            # Remover scripts e styles
            html_content = re.sub(
                r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            html_content = re.sub(
                r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            # Remover tags HTML
            text = re.sub(r'<[^>]+>', '\n', html_content)
            # Limpar espaços em branco
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = text.strip()

            return text if len(text) > 100 else None

        except Exception as e:
            logger.debug(f"Erro ao extrair texto do HTML: {str(e)}")
            return None


# Instâncias globais
camara_client = CamaraAPIClient()
senado_client = SenadoAPIClient()
querido_diario_client = QueridoDiarioClient()
lexml_client = LexMLClient()
