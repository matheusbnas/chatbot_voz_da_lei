"""
Serviço orquestrador para o pipeline completo de preparação de dados
"""
from typing import Dict, Any, Optional, List
from loguru import logger
from sqlalchemy.orm import Session

from app.models.models import Legislation, LegislationChunk, TrainingCorpus
from app.services.data_collector import DataCollector
from app.services.text_processor import text_processor
from app.services.corpus_builder import CorpusBuilder
from app.services.embedding_service import embedding_service


class PipelineService:
    """Serviço para orquestrar o pipeline completo de preparação de dados"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.data_collector = DataCollector(db_session)
        self.corpus_builder = CorpusBuilder(db_session)

    async def run_full_pipeline(
        self,
        source: str = "lexml",
        year: Optional[int] = None,
        tipo_documento: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Executar pipeline completo:
        1. Coleta de dados
        2. Pré-processamento e chunking
        3. Construção de corpus
        4. Geração de embeddings

        Args:
            source: Fonte de dados (lexml, camara, senado)
            year: Ano para filtrar
            tipo_documento: Tipo de documento
            limit: Limite de documentos

        Returns:
            Estatísticas do pipeline
        """
        try:
            logger.info(
                f"Iniciando pipeline completo - fonte: {source}, ano: {year}")

            stats = {
                "collected": 0,
                "processed": 0,
                "chunks_created": 0,
                "corpus_pairs": 0,
                "embeddings_generated": 0
            }

            # 1. Coleta de dados
            logger.info("Etapa 1: Coleta de dados")
            if source == "lexml":
                collection_result = await self.data_collector.collect_from_lexml(
                    year=year,
                    tipo_documento=tipo_documento,
                    limit=limit
                )
            elif source == "camara":
                collection_result = await self.data_collector.collect_from_camara(
                    year=year,
                    limit=limit
                )
            else:
                raise ValueError(f"Fonte desconhecida: {source}")

            stats["collected"] = collection_result.get("collected", 0)
            logger.info(f"Coletados {stats['collected']} documentos")

            # 2. Pré-processamento e chunking
            logger.info("Etapa 2: Pré-processamento e chunking")
            recent_legislations = self.db.query(Legislation).order_by(
                Legislation.created_at.desc()
            ).limit(stats["collected"]).all()

            for legislation in recent_legislations:
                if not legislation.full_text:
                    # Tentar obter texto completo (se disponível)
                    continue

                # Processar texto
                chunks = text_processor.process_legislation_text(
                    legislation.full_text,
                    legislation.id
                )

                # Salvar chunks
                for chunk_data in chunks:
                    chunk = LegislationChunk(
                        legislation_id=legislation.id,
                        chunk_type=chunk_data["type"],
                        chunk_number=chunk_data.get("number"),
                        content=chunk_data["content"],
                        normalized_content=chunk_data["normalized_content"],
                        meta_data=chunk_data.get("metadata", {})
                    )
                    self.db.add(chunk)
                    stats["chunks_created"] += 1

                stats["processed"] += 1

            self.db.commit()
            logger.info(
                f"Processados {stats['processed']} legislações, criados {stats['chunks_created']} chunks")

            # 3. Construção de corpus
            logger.info("Etapa 3: Construção de corpus")
            corpus_result = self.corpus_builder.build_corpus_batch(
                legislation_ids=[l.id for l in recent_legislations],
                limit=stats["processed"]
            )
            stats["corpus_pairs"] = corpus_result.get("total_created", 0)
            logger.info(
                f"Criados {stats['corpus_pairs']} pares pergunta-resposta")

            # 4. Geração de embeddings
            logger.info("Etapa 4: Geração de embeddings")

            # Embeddings dos chunks
            chunk_emb_result = embedding_service.update_chunk_embeddings(
                self.db,
                limit=stats["chunks_created"]
            )

            # Embeddings do corpus
            corpus_emb_result = embedding_service.update_corpus_embeddings(
                self.db,
                limit=stats["corpus_pairs"]
            )

            stats["embeddings_generated"] = (
                chunk_emb_result.get("updated", 0) +
                corpus_emb_result.get("updated", 0)
            )
            logger.info(f"Gerados {stats['embeddings_generated']} embeddings")

            logger.info("Pipeline completo finalizado com sucesso")
            return stats

        except Exception as e:
            logger.error(f"Erro no pipeline: {str(e)}")
            self.db.rollback()
            raise

    async def process_single_legislation(
        self,
        legislation_id: int
    ) -> Dict[str, Any]:
        """
        Processar uma única legislação completa

        Args:
            legislation_id: ID da legislação

        Returns:
            Estatísticas do processamento
        """
        try:
            legislation = self.db.query(Legislation).filter_by(
                id=legislation_id).first()
            if not legislation:
                raise ValueError(f"Legislação {legislation_id} não encontrada")

            stats = {
                "chunks_created": 0,
                "corpus_pairs": 0,
                "embeddings_generated": 0
            }

            # Processar texto se disponível
            if legislation.full_text:
                chunks = text_processor.process_legislation_text(
                    legislation.full_text,
                    legislation.id
                )

                for chunk_data in chunks:
                    chunk = LegislationChunk(
                        legislation_id=legislation.id,
                        chunk_type=chunk_data["type"],
                        chunk_number=chunk_data.get("number"),
                        content=chunk_data["content"],
                        normalized_content=chunk_data["normalized_content"],
                        meta_data=chunk_data.get("metadata", {})
                    )
                    self.db.add(chunk)
                    stats["chunks_created"] += 1

                self.db.commit()

            # Construir corpus
            corpus_result = self.corpus_builder.build_corpus_from_legislation(
                legislation_id)
            stats["corpus_pairs"] = corpus_result.get("total_created", 0)

            # Gerar embeddings
            chunk_emb_result = embedding_service.update_chunk_embeddings(
                self.db,
                limit=stats["chunks_created"]
            )
            corpus_emb_result = embedding_service.update_corpus_embeddings(
                self.db,
                limit=stats["corpus_pairs"]
            )

            stats["embeddings_generated"] = (
                chunk_emb_result.get("updated", 0) +
                corpus_emb_result.get("updated", 0)
            )

            return stats

        except Exception as e:
            logger.error(
                f"Erro ao processar legislação {legislation_id}: {str(e)}")
            self.db.rollback()
            raise
