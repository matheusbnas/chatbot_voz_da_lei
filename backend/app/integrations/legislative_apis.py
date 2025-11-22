import aiohttp
import xml.etree.ElementTree as ET
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
    """Cliente para API do Senado Federal"""

    BASE_URL = settings.SENADO_API_URL

    async def search_matters(
        self,
        keywords: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Buscar matérias no Senado

        Args:
            keywords: Palavras-chave
            year: Ano
            limit: Limite de resultados

        Returns:
            Lista de matérias
        """
        try:
            # A API do Senado usa XML, aqui simplificado
            # Na prática, você precisaria usar xml.etree ou similar
            params = {
                "ano": year or datetime.now().year
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/materia/pesquisa/lista",
                    params=params
                ) as response:
                    response.raise_for_status()
                    # Processar XML aqui
                    return []

        except Exception as e:
            logger.error(f"Erro ao buscar matérias do Senado: {str(e)}")
            return []


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
        Tentar obter o texto completo do documento através da URN

        Args:
            urn: URN do documento

        Returns:
            Texto completo ou None
        """
        if not urn:
            return None

        try:
            # O LexML pode fornecer o texto completo através de uma URL específica
            # Baseado na URN, podemos construir a URL do documento
            # Exemplo: https://www.lexml.gov.br/documento/urn:lex:br:senado.federal:projeto.lei;pls:2008;489

            # Por enquanto, retornamos None pois precisaríamos testar a API real
            # para ver como acessar o texto completo
            # TODO: Implementar busca do texto completo quando descobrirmos o endpoint correto
            return None

        except Exception as e:
            logger.debug(
                f"Não foi possível obter texto completo para URN {urn}: {str(e)}")
            return None


# Instâncias globais
camara_client = CamaraAPIClient()
senado_client = SenadoAPIClient()
querido_diario_client = QueridoDiarioClient()
lexml_client = LexMLClient()
