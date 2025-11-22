"""
Serviço para gerar embeddings de textos legislativos
"""
from typing import List, Dict, Any, Optional
import numpy as np
from loguru import logger
from sqlalchemy.orm import Session

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    logger.warning("sentence-transformers não disponível. Embeddings desabilitados.")

from app.models.models import LegislationChunk, TrainingCorpus


class EmbeddingService:
    """Serviço para gerar embeddings usando modelos de linguagem"""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Inicializar serviço de embeddings
        
        Args:
            model_name: Nome do modelo SentenceTransformer
        """
        self.model = None
        self.model_name = model_name
        
        if EMBEDDING_AVAILABLE:
            try:
                logger.info(f"Carregando modelo de embeddings: {model_name}")
                self.model = SentenceTransformer(model_name)
                logger.info("Modelo de embeddings carregado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar modelo de embeddings: {str(e)}")
                self.model = None
        else:
            logger.warning("sentence-transformers não disponível")
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Gerar embedding para um texto
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            Lista de floats (vetor de embedding) ou None
        """
        if not self.model:
            logger.warning("Modelo de embeddings não disponível")
            return None
        
        if not text or not text.strip():
            return None
        
        try:
            # Gerar embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Converter para lista de floats
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {str(e)}")
            return None
    
    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[Optional[List[float]]]:
        """
        Gerar embeddings para múltiplos textos
        
        Args:
            texts: Lista de textos
            batch_size: Tamanho do lote
            
        Returns:
            Lista de embeddings
        """
        if not self.model:
            return [None] * len(texts)
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            
            return [emb.tolist() for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings em lote: {str(e)}")
            return [None] * len(texts)
    
    def update_chunk_embeddings(
        self,
        db_session: Session,
        chunk_id: Optional[int] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Atualizar embeddings de chunks
        
        Args:
            db_session: Sessão do banco de dados
            chunk_id: ID específico do chunk (None = todos)
            limit: Limite de chunks a processar
            
        Returns:
            Estatísticas
        """
        try:
            query = db_session.query(LegislationChunk).filter(
                LegislationChunk.embedding.is_(None)
            )
            
            if chunk_id:
                query = query.filter_by(id=chunk_id)
            
            chunks = query.limit(limit).all()
            
            if not chunks:
                return {"updated": 0, "total": 0}
            
            texts = [chunk.normalized_content or chunk.content for chunk in chunks]
            embeddings = self.generate_embeddings_batch(texts)
            
            updated = 0
            for chunk, embedding in zip(chunks, embeddings):
                if embedding:
                    chunk.embedding = embedding
                    updated += 1
            
            db_session.commit()
            
            logger.info(f"Embeddings atualizados: {updated} de {len(chunks)} chunks")
            
            return {
                "updated": updated,
                "total": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Erro ao atualizar embeddings: {str(e)}")
            db_session.rollback()
            raise
    
    def update_corpus_embeddings(
        self,
        db_session: Session,
        corpus_id: Optional[int] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Atualizar embeddings de pares pergunta-resposta
        
        Args:
            db_session: Sessão do banco de dados
            corpus_id: ID específico (None = todos)
            limit: Limite a processar
            
        Returns:
            Estatísticas
        """
        try:
            query = db_session.query(TrainingCorpus).filter(
                TrainingCorpus.embedding.is_(None)
            )
            
            if corpus_id:
                query = query.filter_by(id=corpus_id)
            
            corpus_entries = query.limit(limit).all()
            
            if not corpus_entries:
                return {"updated": 0, "total": 0}
            
            questions = [entry.question for entry in corpus_entries]
            embeddings = self.generate_embeddings_batch(questions)
            
            updated = 0
            for entry, embedding in zip(corpus_entries, embeddings):
                if embedding:
                    entry.embedding = embedding
                    updated += 1
            
            db_session.commit()
            
            logger.info(f"Embeddings de corpus atualizados: {updated} de {len(corpus_entries)}")
            
            return {
                "updated": updated,
                "total": len(corpus_entries)
            }
            
        except Exception as e:
            logger.error(f"Erro ao atualizar embeddings do corpus: {str(e)}")
            db_session.rollback()
            raise
    
    def find_similar(
        self,
        query_text: str,
        embeddings: List[List[float]],
        texts: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Encontrar textos similares usando embeddings
        
        Args:
            query_text: Texto de consulta
            embeddings: Lista de embeddings dos textos
            texts: Lista de textos originais
            top_k: Número de resultados
            
        Returns:
            Lista de textos similares com scores
        """
        if not self.model:
            return []
        
        try:
            # Gerar embedding da query
            query_embedding = self.model.encode(query_text, convert_to_numpy=True)
            
            # Calcular similaridade (cosine similarity)
            similarities = []
            for emb, text in zip(embeddings, texts):
                if emb:
                    emb_array = np.array(emb)
                    similarity = np.dot(query_embedding, emb_array) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(emb_array)
                    )
                    similarities.append({
                        "text": text,
                        "score": float(similarity)
                    })
            
            # Ordenar por score e retornar top_k
            similarities.sort(key=lambda x: x["score"], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Erro ao buscar similares: {str(e)}")
            return []


# Instância global
embedding_service = EmbeddingService()

