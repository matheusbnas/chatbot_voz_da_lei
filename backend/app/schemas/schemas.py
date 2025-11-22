from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Legislation Schemas
class LegislationBase(BaseModel):
    type: str
    number: str
    year: int
    title: str
    summary: Optional[str] = None


class LegislationSimplified(BaseModel):
    id: int
    type: str
    number: str
    year: int
    title: str
    simplified_text: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    author: Optional[str] = None
    presentation_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class LegislationDetail(LegislationSimplified):
    full_text: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    last_update: Optional[datetime] = None


# Query Schemas
class QueryRequest(BaseModel):
    query_text: str = Field(..., min_length=3, max_length=2000)
    query_type: str = Field(default="text", pattern="^(text|audio)$")
    user_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    id: int
    query_text: str
    response: str
    simplified_response: Optional[str] = None
    audio_url: Optional[str] = None
    related_legislations: Optional[List[LegislationSimplified]] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chat Schemas
class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: Optional[List[ChatMessage]] = []
    use_audio: bool = False


class ChatResponse(BaseModel):
    message: str
    audio_url: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = []
    suggestions: Optional[List[str]] = []


# Simplification Schemas
class SimplificationRequest(BaseModel):
    text: str = Field(..., min_length=10)
    target_level: str = Field(default="simple", pattern="^(simple|moderate|technical)$")
    include_audio: bool = False


class SimplificationResponse(BaseModel):
    original_text: str
    simplified_text: str
    audio_url: Optional[str] = None
    reading_time_minutes: int


# Search Schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3)
    filters: Optional[Dict[str, Any]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[LegislationSimplified]


# Favorite Schemas
class FavoriteCreate(BaseModel):
    legislation_id: int
    notes: Optional[str] = None


class FavoriteResponse(BaseModel):
    id: int
    legislation: LegislationSimplified
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Feedback Schemas
class FeedbackCreate(BaseModel):
    query_id: int
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_text: Optional[str] = None
    is_helpful: Optional[bool] = None


class FeedbackResponse(BaseModel):
    id: int
    query_id: int
    rating: Optional[int] = None
    is_helpful: Optional[bool] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Audio Schemas
class AudioTranscriptionRequest(BaseModel):
    audio_base64: str
    language: str = "pt"


class AudioTranscriptionResponse(BaseModel):
    text: str
    confidence: Optional[float] = None
    language: str


# Municipal Legislation Schemas
class MunicipalSearchRequest(BaseModel):
    city: str
    state: str
    keywords: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class MunicipalLegislationResponse(BaseModel):
    id: int
    city: str
    state: str
    content: str
    simplified_content: Optional[str] = None
    publication_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    
    class Config:
        from_attributes = True
