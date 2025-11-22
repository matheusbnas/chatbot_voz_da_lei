"""
Endpoints para o pipeline de preparação de dados
"""
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import Optional, List
from loguru import logger
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.pipeline_service import PipelineService
from app.services.data_collector import DataCollector
from app.services.corpus_builder import CorpusBuilder
from app.services.embedding_service import embedding_service
from app.models.models import DataCollectionJob

router = APIRouter()


def get_db():
    """Dependency para obter sessão do banco"""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/collect/lexml")
async def collect_lexml(
    year: Optional[int] = Query(None),
    tipo_documento: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Coletar dados do LexML
    
    Inicia uma coleta de dados do LexML e armazena no banco.
    """
    try:
        collector = DataCollector(db)
        
        # Criar job
        job = collector.create_collection_job(
            job_type="lexml",
            parameters={
                "year": year,
                "tipo_documento": tipo_documento,
                "limit": limit
            }
        )
        
        # Executar em background
        if background_tasks:
            background_tasks.add_task(
                collector.run_collection_job,
                job.id
            )
            return {
                "job_id": job.id,
                "status": "started",
                "message": "Coleta iniciada em background"
            }
        else:
            result = await collector.run_collection_job(job.id)
            return {
                "job_id": job.id,
                "status": "completed",
                "result": result
            }
            
    except Exception as e:
        logger.error(f"Erro ao coletar dados do LexML: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect/camara")
async def collect_camara(
    year: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Coletar dados da Câmara dos Deputados
    """
    try:
        collector = DataCollector(db)
        
        job = collector.create_collection_job(
            job_type="camara",
            parameters={"year": year, "limit": limit}
        )
        
        if background_tasks:
            background_tasks.add_task(
                collector.run_collection_job,
                job.id
            )
            return {
                "job_id": job.id,
                "status": "started",
                "message": "Coleta iniciada em background"
            }
        else:
            result = await collector.run_collection_job(job.id)
            return {
                "job_id": job.id,
                "status": "completed",
                "result": result
            }
            
    except Exception as e:
        logger.error(f"Erro ao coletar dados da Câmara: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline/run")
async def run_pipeline(
    source: str = Query("lexml", regex="^(lexml|camara)$"),
    year: Optional[int] = Query(None),
    tipo_documento: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Executar pipeline completo de preparação de dados
    
    Pipeline inclui:
    - Coleta de dados
    - Pré-processamento e chunking
    - Construção de corpus
    - Geração de embeddings
    """
    try:
        pipeline = PipelineService(db)
        
        if background_tasks:
            background_tasks.add_task(
                pipeline.run_full_pipeline,
                source=source,
                year=year,
                tipo_documento=tipo_documento,
                limit=limit
            )
            return {
                "status": "started",
                "message": "Pipeline iniciado em background"
            }
        else:
            result = await pipeline.run_full_pipeline(
                source=source,
                year=year,
                tipo_documento=tipo_documento,
                limit=limit
            )
            return {
                "status": "completed",
                "result": result
            }
            
    except Exception as e:
        logger.error(f"Erro ao executar pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/corpus/build/{legislation_id}")
async def build_corpus(
    legislation_id: int,
    force_rebuild: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Construir corpus para uma legislação específica
    """
    try:
        builder = CorpusBuilder(db)
        result = builder.build_corpus_from_legislation(
            legislation_id,
            force_rebuild=force_rebuild
        )
        return result
        
    except Exception as e:
        logger.error(f"Erro ao construir corpus: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embeddings/generate")
async def generate_embeddings(
    entity_type: str = Query(..., regex="^(chunks|corpus)$"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Gerar embeddings para chunks ou corpus
    """
    try:
        if entity_type == "chunks":
            result = embedding_service.update_chunk_embeddings(db, limit=limit)
        else:
            result = embedding_service.update_corpus_embeddings(db, limit=limit)
        
        return result
        
    except Exception as e:
        logger.error(f"Erro ao gerar embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Obter status de um job de coleta
    """
    try:
        job = db.query(DataCollectionJob).filter_by(id=job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job não encontrado")
        
        return {
            "id": job.id,
            "job_type": job.job_type,
            "status": job.status,
            "total_items": job.total_items,
            "processed_items": job.processed_items,
            "failed_items": job.failed_items,
            "error_message": job.error_message,
            "started_at": job.started_at,
            "completed_at": job.completed_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status do job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

