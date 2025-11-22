from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Modelo de usuário"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relacionamentos
    queries = relationship("Query", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")


class Legislation(Base):
    """Modelo de legislação (PL, PEC, etc)"""
    __tablename__ = "legislations"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # ID da API externa
    source = Column(String, nullable=False)  # camara, senado, municipal
    type = Column(String, nullable=False)  # PL, PEC, PLV, etc
    number = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    full_text = Column(Text)
    simplified_text = Column(Text)  # Texto simplificado pela IA
    status = Column(String)
    author = Column(String)
    presentation_date = Column(DateTime)
    last_update = Column(DateTime)
    tags = Column(JSON)  # Tags para categorização
    raw_data = Column(JSON)  # Dados brutos da API
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relacionamentos
    favorites = relationship("Favorite", back_populates="legislation")


class Query(Base):
    """Modelo de consulta do usuário"""
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query_text = Column(Text, nullable=False)
    query_type = Column(String)  # text, audio
    response = Column(Text)
    simplified_response = Column(Text)
    audio_url = Column(String)  # URL do áudio de resposta
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    user = relationship("User", back_populates="queries")


class Favorite(Base):
    """Modelo de favoritos do usuário"""
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    legislation_id = Column(Integer, ForeignKey(
        "legislations.id"), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    user = relationship("User", back_populates="favorites")
    legislation = relationship("Legislation", back_populates="favorites")


class MunicipalLegislation(Base):
    """Modelo de legislação municipal"""
    __tablename__ = "municipal_legislations"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    publication_date = Column(DateTime)
    content = Column(Text, nullable=False)
    simplified_content = Column(Text)
    source_url = Column(String)
    tags = Column(JSON)
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)


class AIFeedback(Base):
    """Modelo de feedback sobre respostas da IA"""
    __tablename__ = "ai_feedback"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False)
    rating = Column(Integer)  # 1-5
    feedback_text = Column(Text)
    is_helpful = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)


class LegislationChunk(Base):
    """Modelo para armazenar chunks (pedaços) de legislação processados"""
    __tablename__ = "legislation_chunks"

    id = Column(Integer, primary_key=True, index=True)
    legislation_id = Column(Integer, ForeignKey(
        "legislations.id"), nullable=False, index=True)
    # artigo, paragrafo, inciso, seção
    chunk_type = Column(String, nullable=False)
    chunk_number = Column(String)  # número do artigo/parágrafo
    content = Column(Text, nullable=False)
    normalized_content = Column(Text)  # conteúdo normalizado
    # metadados adicionais (citações, referências, etc)
    metadata = Column(JSON)
    embedding = Column(JSON)  # embedding vetorial (armazenado como JSON array)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento
    legislation = relationship("Legislation")


class TrainingCorpus(Base):
    """Modelo para armazenar pares pergunta-resposta para treinamento"""
    __tablename__ = "training_corpus"

    id = Column(Integer, primary_key=True, index=True)
    legislation_id = Column(Integer, ForeignKey(
        "legislations.id"), nullable=True, index=True)
    chunk_id = Column(Integer, ForeignKey(
        "legislation_chunks.id"), nullable=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    answer_source = Column(Text)  # trecho da lei que originou a resposta
    # o_que_e, quem, quando, como, qual_pena, etc
    question_type = Column(String)
    metadata = Column(JSON)  # metadados adicionais
    embedding = Column(JSON)  # embedding da pergunta
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relacionamentos
    legislation = relationship("Legislation")
    chunk = relationship("LegislationChunk")


class DataCollectionJob(Base):
    """Modelo para rastrear jobs de coleta de dados"""
    __tablename__ = "data_collection_jobs"

    id = Column(Integer, primary_key=True, index=True)
    # lexml, camara, senado, municipal
    job_type = Column(String, nullable=False)
    # pending, running, completed, failed
    status = Column(String, nullable=False)
    parameters = Column(JSON)  # parâmetros da coleta
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
