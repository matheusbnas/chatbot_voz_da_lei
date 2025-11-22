from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from loguru import logger

from app.schemas.schemas import LegislationSimplified, LegislationDetail
from app.integrations.legislative_apis import (
    camara_client,
    querido_diario_client,
    lexml_client
)

router = APIRouter()


@router.get("/trending", response_model=List[LegislationSimplified])
async def get_trending_legislation(limit: int = Query(10, ge=1, le=50)):
    """
    Obter legislações em destaque

    Retorna as proposições mais recentes e relevantes.
    Busca no LexML e na Câmara dos Deputados.
    """
    try:
        result = []

        # Buscar no LexML - projetos de lei recentes
        from datetime import datetime
        current_year = datetime.now().year

        lexml_projects = await lexml_client.search_projects_of_law(
            year=current_year,
            limit=limit // 2
        )

        for doc in lexml_projects:
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

            result.append(LegislationSimplified(
                id=doc.get("lexml_id", hash(urn)),
                type=doc.get("tipo_documento", "PL"),
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

        # Buscar da Câmara como complemento
        if len(result) < limit:
            propositions = await camara_client.get_trending_topics(limit=limit - len(result))

            for prop in propositions:
                result.append(LegislationSimplified(
                    id=prop.get("id"),
                    type=prop.get("siglaTipo", "PL"),
                    number=str(prop.get("numero", "")),
                    year=prop.get("ano", 0),
                    title=prop.get("ementa", ""),
                    summary=prop.get("ementa", "")[:200] + "...",
                    status=None,
                    author=None,
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
    Obter detalhes de uma legislação específica

    Args:
        legislation_id: ID da proposição
    """
    try:
        # Buscar detalhes
        details = await camara_client.get_proposition_details(legislation_id)

        if not details:
            raise HTTPException(
                status_code=404, detail="Legislação não encontrada")

        # Buscar autores
        authors = await camara_client.get_proposition_authors(legislation_id)
        author_names = [a.get("nome", "") for a in authors[:3]]

        return LegislationDetail(
            id=details.get("id"),
            type=details.get("siglaTipo", ""),
            number=str(details.get("numero", "")),
            year=details.get("ano", 0),
            title=details.get("ementa", ""),
            summary=details.get("ementa", ""),
            full_text=None,  # TODO: Implementar extração de texto
            simplified_text=None,
            status=details.get("statusProposicao", {}).get(
                "descricaoTramitacao"),
            author=", ".join(author_names) if author_names else None,
            presentation_date=details.get("dataApresentacao"),
            last_update=details.get("statusProposicao", {}).get("dataHora"),
            tags=details.get("keywords"),
            raw_data=details
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
    Buscar legislação municipal

    Args:
        state: Sigla do estado (ex: SP, RJ)
        city: Nome da cidade
        keywords: Palavras-chave para buscar
        limit: Número de resultados
    """
    try:
        gazettes = await querido_diario_client.search_gazettes(
            city=city,
            state=state,
            keywords=keywords
        )

        return {
            "state": state,
            "city": city,
            "total": len(gazettes),
            "results": gazettes[:limit]
        }

    except Exception as e:
        logger.error(f"Erro ao buscar legislação municipal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{legislation_id}/votes")
async def get_legislation_votes(legislation_id: int):
    """
    Obter votações de uma legislação

    Args:
        legislation_id: ID da proposição
    """
    try:
        votes = await camara_client.get_proposition_votes(legislation_id)

        return {
            "legislation_id": legislation_id,
            "total_votes": len(votes),
            "votes": votes
        }

    except Exception as e:
        logger.error(f"Erro ao buscar votações: {str(e)}")
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
