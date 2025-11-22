"""
Serviço para construir corpus de treinamento com pares pergunta-resposta
"""
from typing import List, Dict, Any, Optional
from loguru import logger
from sqlalchemy.orm import Session

from app.models.models import Legislation, LegislationChunk, TrainingCorpus
from app.services.text_processor import text_processor


class CorpusBuilder:
    """Serviço para construir corpus de treinamento"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def generate_qa_pairs(
        self,
        chunk: LegislationChunk,
        legislation: Legislation
    ) -> List[Dict[str, Any]]:
        """
        Gerar pares pergunta-resposta a partir de um chunk
        
        Args:
            chunk: Chunk de legislação
            legislation: Legislação completa
            
        Returns:
            Lista de pares pergunta-resposta
        """
        qa_pairs = []
        content = chunk.normalized_content or chunk.content
        
        # 1. Pergunta: "O que diz o artigo X?"
        if chunk.chunk_type == "article" and chunk.chunk_number:
            qa_pairs.append({
                "question": f"O que diz o artigo {chunk.chunk_number} da {legislation.type} {legislation.number}/{legislation.year}?",
                "answer": content,
                "answer_source": f"Art. {chunk.chunk_number}",
                "question_type": "o_que_diz"
            })
        
        # 2. Pergunta: "Qual o conteúdo do artigo X?"
        if chunk.chunk_type == "article" and chunk.chunk_number:
            qa_pairs.append({
                "question": f"Qual o conteúdo do artigo {chunk.chunk_number}?",
                "answer": content,
                "answer_source": f"Art. {chunk.chunk_number}",
                "question_type": "qual_conteudo"
            })
        
        # 3. Pergunta: "Sobre o que trata esta lei?"
        if chunk.chunk_type == "article" and chunk.chunk_number == "1":
            qa_pairs.append({
                "question": f"Sobre o que trata a {legislation.type} {legislation.number}/{legislation.year}?",
                "answer": content,
                "answer_source": f"Art. {chunk.chunk_number}",
                "question_type": "sobre_que_trata"
            })
        
        # 4. Pergunta: "Quem está sujeito a esta lei?"
        if "sujeito" in content.lower() or "obrigado" in content.lower():
            qa_pairs.append({
                "question": f"Quem está sujeito à {legislation.type} {legislation.number}/{legislation.year}?",
                "answer": content,
                "answer_source": f"Art. {chunk.chunk_number}",
                "question_type": "quem_sujeito"
            })
        
        # 5. Pergunta: "Qual a pena/multa?"
        if "pena" in content.lower() or "multa" in content.lower() or "sanção" in content.lower():
            qa_pairs.append({
                "question": f"Qual a pena prevista na {legislation.type} {legislation.number}/{legislation.year}?",
                "answer": content,
                "answer_source": f"Art. {chunk.chunk_number}",
                "question_type": "qual_pena"
            })
        
        # 6. Pergunta: "Quando esta lei entra em vigor?"
        if "vigor" in content.lower() or "vigência" in content.lower():
            qa_pairs.append({
                "question": f"Quando a {legislation.type} {legislation.number}/{legislation.year} entra em vigor?",
                "answer": content,
                "answer_source": f"Art. {chunk.chunk_number}",
                "question_type": "quando_vigor"
            })
        
        # 7. Pergunta genérica baseada no título
        if legislation.title:
            qa_pairs.append({
                "question": f"O que é a {legislation.type} {legislation.number}/{legislation.year} sobre {legislation.title[:50]}?",
                "answer": content,
                "answer_source": f"Art. {chunk.chunk_number}",
                "question_type": "o_que_e"
            })
        
        return qa_pairs
    
    def build_corpus_from_legislation(
        self,
        legislation_id: int,
        force_rebuild: bool = False
    ) -> Dict[str, Any]:
        """
        Construir corpus completo a partir de uma legislação
        
        Args:
            legislation_id: ID da legislação
            force_rebuild: Se True, recria mesmo se já existir
            
        Returns:
            Estatísticas do corpus criado
        """
        try:
            legislation = self.db.query(Legislation).filter_by(id=legislation_id).first()
            if not legislation:
                raise ValueError(f"Legislação {legislation_id} não encontrada")
            
            # Verificar se já existe corpus
            existing = self.db.query(TrainingCorpus).filter_by(
                legislation_id=legislation_id
            ).first()
            
            if existing and not force_rebuild:
                logger.info(f"Corpus já existe para legislação {legislation_id}")
                return {"status": "exists", "total": 0}
            
            # Buscar chunks da legislação
            chunks = self.db.query(LegislationChunk).filter_by(
                legislation_id=legislation_id
            ).all()
            
            if not chunks:
                logger.warning(f"Nenhum chunk encontrado para legislação {legislation_id}")
                return {"status": "no_chunks", "total": 0}
            
            # Gerar pares QA para cada chunk
            total_pairs = 0
            created_pairs = 0
            
            for chunk in chunks:
                qa_pairs = self.generate_qa_pairs(chunk, legislation)
                total_pairs += len(qa_pairs)
                
                for qa in qa_pairs:
                    # Verificar se já existe
                    existing = self.db.query(TrainingCorpus).filter_by(
                        legislation_id=legislation_id,
                        chunk_id=chunk.id,
                        question=qa["question"]
                    ).first()
                    
                    if existing and not force_rebuild:
                        continue
                    
                    # Criar novo par
                    corpus_entry = TrainingCorpus(
                        legislation_id=legislation_id,
                        chunk_id=chunk.id,
                        question=qa["question"],
                        answer=qa["answer"],
                        answer_source=qa["answer_source"],
                        question_type=qa["question_type"],
                        metadata={
                            "chunk_type": chunk.chunk_type,
                            "chunk_number": chunk.chunk_number
                        }
                    )
                    
                    self.db.add(corpus_entry)
                    created_pairs += 1
            
            self.db.commit()
            
            logger.info(
                f"Corpus criado para legislação {legislation_id}: "
                f"{created_pairs} pares criados de {total_pairs} gerados"
            )
            
            return {
                "status": "created",
                "total_generated": total_pairs,
                "total_created": created_pairs,
                "legislation_id": legislation_id
            }
            
        except Exception as e:
            logger.error(f"Erro ao construir corpus: {str(e)}")
            self.db.rollback()
            raise
    
    def build_corpus_batch(
        self,
        legislation_ids: Optional[List[int]] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Construir corpus para múltiplas legislações
        
        Args:
            legislation_ids: Lista de IDs (None = todas)
            limit: Limite de legislações
            
        Returns:
            Estatísticas gerais
        """
        try:
            query = self.db.query(Legislation)
            
            if legislation_ids:
                query = query.filter(Legislation.id.in_(legislation_ids))
            
            legislations = query.limit(limit).all()
            
            total_created = 0
            total_generated = 0
            processed = 0
            
            for legislation in legislations:
                result = self.build_corpus_from_legislation(legislation.id)
                total_created += result.get("total_created", 0)
                total_generated += result.get("total_generated", 0)
                processed += 1
            
            return {
                "processed": processed,
                "total_generated": total_generated,
                "total_created": total_created
            }
            
        except Exception as e:
            logger.error(f"Erro ao construir corpus em lote: {str(e)}")
            raise

