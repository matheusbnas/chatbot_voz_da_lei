"""
Serviço para coleta e armazenamento de dados legislativos
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.models import (
    Legislation,
    LegislationChunk,
    DataCollectionJob,
    Base
)
from app.integrations.legislative_apis import lexml_client


class DataCollector:
    """Serviço para coletar dados de APIs legislativas e armazenar no banco"""

    def __init__(self, db_session: Any):
        self.db = db_session

    async def collect_from_lexml(
        self,
        year: Optional[int] = None,
        tipo_documento: Optional[str] = None,
        limit: int = 100,
        job_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Coletar dados do LexML

        Args:
            year: Ano para filtrar
            tipo_documento: Tipo de documento (Lei, Projeto de Lei, etc)
            limit: Limite de documentos
            job_id: ID do job de coleta
        """
        try:
            logger.info(
                f"Iniciando coleta do LexML - tipo: {tipo_documento}, ano: {year}")

            # Buscar documentos
            if tipo_documento == "Projeto de Lei":
                documents = await lexml_client.search_projects_of_law(
                    year=year,
                    limit=limit
                )
            elif tipo_documento == "Lei":
                documents = await lexml_client.search_laws(
                    year=year,
                    limit=limit
                )
            else:
                documents = await lexml_client.search_by_keywords(
                    keywords="",
                    year=year,
                    tipo_documento=tipo_documento,
                    limit=limit
                )

            collected = 0
            failed = 0

            for doc in documents:
                try:
                    # Verificar se já existe
                    existing = self.db.query(Legislation).filter(
                        Legislation.external_id == doc.get("lexml_id")
                    ).first()

                    if existing:
                        logger.debug(
                            f"Documento {doc.get('lexml_id')} já existe, pulando")
                        continue

                    # Criar novo registro
                    legislation = Legislation(
                        external_id=doc.get("lexml_id", ""),
                        source="lexml",
                        type=doc.get("tipo_documento", "Documento"),
                        number=self._extract_number(doc.get("title", "")),
                        year=int(doc.get("date", datetime.now().year)),
                        title=doc.get("title", ""),
                        summary=doc.get("description", ""),
                        full_text=None,  # Será preenchido depois
                        author=doc.get("autoridade"),
                        raw_data=doc,
                        created_at=datetime.utcnow()
                    )

                    self.db.add(legislation)
                    self.db.commit()
                    collected += 1

                    # Atualizar progresso do job
                    if job_id:
                        job = self.db.query(DataCollectionJob).filter_by(
                            id=job_id).first()
                        if job:
                            job.processed_items = collected
                            self.db.commit()

                except Exception as e:
                    logger.error(
                        f"Erro ao salvar documento {doc.get('lexml_id')}: {str(e)}")
                    failed += 1
                    self.db.rollback()

            logger.info(
                f"Coleta do LexML concluída: {collected} coletados, {failed} falhas")
            return {
                "collected": collected,
                "failed": failed,
                "total": len(documents)
            }

        except Exception as e:
            logger.error(f"Erro na coleta do LexML: {str(e)}")
            raise


    def _extract_number(self, title: str) -> str:
        """Extrair número do título (ex: 'PLS nº 489/2008' -> '489')"""
        try:
            if "nº" in title or "Nº" in title:
                parts = title.split(
                    "nº") if "nº" in title else title.split("Nº")
                if len(parts) > 1:
                    number_part = parts[1].split("/")[0].strip()
                    return number_part
            return ""
        except:
            return ""

    def create_collection_job(
        self,
        job_type: str,
        parameters: Dict[str, Any]
    ) -> DataCollectionJob:
        """
        Criar um job de coleta de dados
        """
        job = DataCollectionJob(
            job_type=job_type,
            status="pending",
            parameters=parameters,
            created_at=datetime.utcnow()
        )
        self.db.add(job)
        self.db.commit()
        return job

    async def run_collection_job(self, job_id: int):
        """
        Executar um job de coleta
        """
        job = self.db.query(DataCollectionJob).filter_by(id=job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} não encontrado")

        job.status = "running"
        job.started_at = datetime.utcnow()
        self.db.commit()

        try:
            if job.job_type == "lexml":
                result = await self.collect_from_lexml(
                    year=job.parameters.get("year"),
                    tipo_documento=job.parameters.get("tipo_documento"),
                    limit=job.parameters.get("limit", 100),
                    job_id=job_id
                )
            else:
                raise ValueError(f"Tipo de job desconhecido: {job.job_type}. Apenas 'lexml' é suportado.")

            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.total_items = result.get("total", 0)
            job.processed_items = result.get("collected", 0)
            job.failed_items = result.get("failed", 0)
            self.db.commit()

            return result

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            raise
