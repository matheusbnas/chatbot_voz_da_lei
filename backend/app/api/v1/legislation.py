from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from loguru import logger
from datetime import datetime

from app.schemas.schemas import LegislationSimplified, LegislationDetail
from app.integrations.legislative_apis import lexml_client

router = APIRouter()


@router.get("/trending", response_model=List[LegislationSimplified])
async def get_trending_legislation(limit: int = Query(10, ge=1, le=50)):
    """
    Obter legislações em destaque

    Retorna as proposições mais recentes e relevantes do LexML.
    """
    try:
        result = []

        # Buscar no LexML - projetos de lei recentes
        current_year = datetime.now().year

        # Buscar projetos de lei do ano atual
        lexml_projects = await lexml_client.search_projects_of_law(
            year=current_year,
            limit=limit
        )

        # Se não houver projetos suficientes, buscar também leis
        if len(lexml_projects) < limit:
            lexml_laws = await lexml_client.search_laws(
                year=current_year,
                limit=limit - len(lexml_projects)
            )
            lexml_projects.extend(lexml_laws)

        for doc in lexml_projects[:limit]:
            # Extrair número e ano do título ou URN
            title = doc.get("title", "")
            urn = doc.get("urn", "")

            # Tentar extrair número do título (ex: "PLS nº 489/2008")
            number = ""
            year = doc.get("date", current_year)

            if "nº" in title or "Nº" in title:
                parts = title.split(
                    "nº") if "nº" in title else title.split("Nº")
                if len(parts) > 1:
                    number_part = parts[1].split("/")[0].strip()
                    number = number_part

            # Usar hash da URN como ID se não houver lexml_id
            doc_id = doc.get("lexml_id")
            if not doc_id:
                # ID numérico baseado no hash
                doc_id = abs(hash(urn)) % (10 ** 10)

            result.append(LegislationSimplified(
                id=int(doc_id) if doc_id else abs(hash(urn)) % (10 ** 10),
                type=doc.get("tipo_documento", "Documento"),
                number=number or "N/A",
                year=int(year) if year else current_year,
                title=title,
                summary=doc.get("description", "")[
                    :200] + "..." if doc.get("description") else "",
                status=None,
                author=doc.get("autoridade"),
                presentation_date=None,
                tags=None
            ))

        return result[:limit]

    except Exception as e:
        logger.error(f"Erro ao buscar legislações em destaque: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{legislation_id}", response_model=LegislationDetail)
async def get_legislation_detail(legislation_id: int):
    """
    Obter detalhes de uma legislação específica do LexML

    Args:
        legislation_id: ID da legislação (lexml_id ou hash da URN)
    """
    try:
        # Buscar por ID no LexML usando busca genérica
        # Como o LexML não tem endpoint direto por ID, vamos buscar por palavras-chave
        # ou usar a busca por URN se o ID for uma URN

        # Por enquanto, vamos buscar legislações recentes e filtrar por ID
        # Em produção, seria melhor ter um cache ou banco de dados local
        current_year = datetime.now().year

        # Buscar em projetos de lei
        projects = await lexml_client.search_projects_of_law(
            year=current_year,
            limit=100
        )

        # Buscar em leis
        laws = await lexml_client.search_laws(
            year=current_year,
            limit=100
        )

        all_docs = projects + laws

        # Encontrar documento pelo ID
        doc = None
        for d in all_docs:
            doc_id = d.get("lexml_id")
            if doc_id and str(doc_id) == str(legislation_id):
                doc = d
                break
            # Também verificar por hash da URN
            if not doc_id:
                urn = d.get("urn", "")
                if urn and abs(hash(urn)) % (10 ** 10) == legislation_id:
                    doc = d
                    break

        if not doc:
            raise HTTPException(
                status_code=404, detail="Legislação não encontrada no LexML")

        # Buscar texto completo se disponível
        full_text = doc.get("full_text")
        if not full_text and doc.get("urn"):
            full_text = await lexml_client._get_document_full_text(doc.get("urn"))

        # Extrair número do título
        title = doc.get("title", "")
        number = ""
        if "nº" in title or "Nº" in title:
            parts = title.split("nº") if "nº" in title else title.split("Nº")
            if len(parts) > 1:
                number_part = parts[1].split("/")[0].strip()
                number = number_part

        year = doc.get("date", current_year)

        return LegislationDetail(
            id=int(doc.get("lexml_id")) if doc.get("lexml_id") else abs(
                hash(doc.get("urn", ""))) % (10 ** 10),
            type=doc.get("tipo_documento", "Documento"),
            number=number or "N/A",
            year=int(year) if year else current_year,
            title=title,
            summary=doc.get("description", ""),
            full_text=full_text,
            simplified_text=None,
            status=None,
            author=doc.get("autoridade"),
            presentation_date=None,
            last_update=None,
            tags=None,
            raw_data=doc
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes da legislação: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/municipal/{state}/{city}")
async def get_municipal_legislation(
    state: str,
    city: str,
    keywords: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """
    Buscar legislação municipal no LexML

    Args:
        state: Sigla do estado (ex: SP, RJ)
        city: Nome da cidade
        keywords: Palavras-chave para buscar
        limit: Número de resultados
    """
    try:
        # Buscar no LexML usando palavras-chave e filtro de localidade
        query_parts = []

        if keywords:
            query_parts.append(
                f'dc.title all "{keywords}" or dc.description all "{keywords}"')

        # Filtrar por localidade (municipal)
        query_parts.append(f'localidade="{city}"')

        query = " and ".join(
            query_parts) if query_parts else f'localidade="{city}"'

        result = await lexml_client.search(
            query=query,
            maximum_records=limit
        )

        return {
            "state": state,
            "city": city,
            "total": result.get("total", 0),
            "results": result.get("records", [])[:limit]
        }

    except Exception as e:
        logger.error(f"Erro ao buscar legislação municipal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lexml/search")
async def search_lexml(
    query: str = Query(...,
                       description="Query de busca no LexML (ex: 'urn=\"senado.federal pls 2008\"')"),
    start_record: int = Query(1, ge=1),
    maximum_records: int = Query(20, ge=1, le=100)
):
    """
    Buscar documentos no LexML

    Permite busca avançada usando a sintaxe SRU do LexML.
    Exemplos de queries:
    - urn="senado.federal pls 2008"
    - dc.title all "meio ambiente"
    - tipoDocumento="Lei" and dc.date="2023"
    """
    try:
        result = await lexml_client.search(
            query=query,
            start_record=start_record,
            maximum_records=maximum_records
        )

        return result

    except Exception as e:
        logger.error(f"Erro ao buscar no LexML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lexml/by-keywords")
async def search_lexml_by_keywords(
    keywords: str = Query(..., description="Palavras-chave para busca"),
    year: Optional[int] = Query(None, description="Ano do documento"),
    tipo_documento: Optional[str] = Query(
        None, description="Tipo de documento (Lei, Projeto de Lei, etc)"),
    autoridade: Optional[str] = Query(
        None, description="Autoridade (Senado Federal, Câmara dos Deputados, etc)"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Buscar documentos no LexML por palavras-chave

    Busca simplificada usando palavras-chave e filtros opcionais.
    """
    try:
        results = await lexml_client.search_by_keywords(
            keywords=keywords,
            year=year,
            tipo_documento=tipo_documento,
            autoridade=autoridade,
            limit=limit
        )

        return {
            "total": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Erro ao buscar no LexML por palavras-chave: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lexml/projects")
async def get_lexml_projects(
    year: Optional[int] = Query(None, description="Ano dos projetos"),
    house: Optional[str] = Query(
        None, description="Casa legislativa: 'senado' ou 'camara'"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Buscar projetos de lei no LexML

    Retorna projetos de lei do Senado ou Câmara dos Deputados.
    """
    try:
        results = await lexml_client.search_projects_of_law(
            year=year,
            house=house,
            limit=limit
        )

        return {
            "total": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Erro ao buscar projetos no LexML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lexml/laws")
async def get_lexml_laws(
    year: Optional[int] = Query(None, description="Ano das leis"),
    keywords: Optional[str] = Query(None, description="Palavras-chave"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Buscar leis no LexML

    Retorna leis federais, estaduais ou municipais.
    """
    try:
        results = await lexml_client.search_laws(
            year=year,
            keywords=keywords,
            limit=limit
        )

        return {
            "total": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Erro ao buscar leis no LexML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lexml/by-urn/{urn:path}")
async def get_lexml_by_urn(urn: str):
    """
    Obter documento específico do LexML por URN

    Args:
        urn: URN do documento (ex: 'senado.federal pls 2008' ou URN completa)
    """
    try:
        document = await lexml_client.get_document_by_urn(urn)

        if not document:
            raise HTTPException(
                status_code=404, detail="Documento não encontrado no LexML")

        return document

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar documento por URN: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
