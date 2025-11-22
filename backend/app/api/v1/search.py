from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from loguru import logger

from app.schemas.schemas import SearchRequest, SearchResponse, LegislationSimplified
from app.integrations.legislative_apis import camara_client

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search_legislation(request: SearchRequest):
    """
    Buscar legislação por palavras-chave
    
    Busca em múltiplas fontes (Câmara, Senado, municípios).
    """
    try:
        # Buscar na Câmara dos Deputados
        propositions = await camara_client.search_propositions(
            keywords=request.query,
            year=request.filters.get("year") if request.filters else None,
            limit=request.page_size
        )
        
        # Converter para formato padronizado
        results = []
        for prop in propositions:
            results.append(LegislationSimplified(
                id=prop.get("id"),
                type=prop.get("siglaTipo", ""),
                number=str(prop.get("numero", "")),
                year=prop.get("ano", 0),
                title=prop.get("ementa", ""),
                summary=prop.get("ementa", "")[:200] + "..." if prop.get("ementa") else None,
                status=None,
                author=None,
                presentation_date=None,
                tags=None
            ))
        
        return SearchResponse(
            total=len(results),
            page=request.page,
            page_size=request.page_size,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Erro na busca: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/autocomplete")
async def autocomplete(q: str = Query(..., min_length=2)):
    """
    Autocompletar termos de busca
    
    Args:
        q: Termo parcial para autocompletar
    """
    # Sugestões baseadas em termos comuns
    suggestions = [
        "educação",
        "saúde",
        "transporte",
        "meio ambiente",
        "trabalho",
        "previdência",
        "impostos",
        "segurança",
        "cultura",
        "esporte"
    ]
    
    filtered = [s for s in suggestions if q.lower() in s.lower()]
    
    return {"suggestions": filtered[:5]}


@router.get("/filters")
async def get_available_filters():
    """
    Obter filtros disponíveis para busca
    """
    return {
        "types": ["PL", "PEC", "PLP", "PLV"],
        "years": list(range(2020, 2026)),
        "sources": ["camara", "senado", "municipal"],
        "status": [
            "Em tramitação",
            "Aprovado",
            "Rejeitado",
            "Arquivado"
        ]
    }
