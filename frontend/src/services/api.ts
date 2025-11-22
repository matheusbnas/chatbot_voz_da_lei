import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Format error message for better display
    if (error.response) {
      // Server responded with error status
      const errorMessage = error.response.data?.detail || error.response.data?.message || error.message;
      error.formattedMessage = errorMessage;
    } else if (error.request) {
      // Request was made but no response received
      error.formattedMessage = 'Erro de conexão. Verifique se o servidor está rodando.';
    } else {
      // Something else happened
      error.formattedMessage = error.message || 'Erro desconhecido';
    }
    return Promise.reject(error);
  }
);

// Types
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  conversation_history?: ChatMessage[];
  use_audio?: boolean;
}

export interface ChatResponse {
  message: string;
  audio_url?: string;
  sources?: any[];
  suggestions?: string[];
}

export interface Legislation {
  id: number;
  type: string;
  number: string;
  year: number;
  title: string;
  summary?: string;
  simplified_text?: string;
  status?: string;
  author?: string;
  presentation_date?: string;
  tags?: string[];
}

export interface SimplificationRequest {
  text: string;
  target_level?: 'simple' | 'moderate' | 'technical';
  include_audio?: boolean;
}

export interface SimplificationResponse {
  original_text: string;
  simplified_text: string;
  audio_url?: string;
  reading_time_minutes: number;
}

export interface SearchRequest {
  query: string;
  filters?: Record<string, any>;
  page?: number;
  page_size?: number;
}

export interface SearchResponse {
  total: number;
  page: number;
  page_size: number;
  results: Legislation[];
}

// API Functions
export const chatApi = {
  sendMessage: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/chat/', data);
    return response.data;
  },
  
  getSuggestions: async (): Promise<string[]> => {
    const response = await api.get('/chat/suggestions');
    return response.data.suggestions;
  },
};

export const legislationApi = {
  getTrending: async (limit: number = 10): Promise<Legislation[]> => {
    const response = await api.get(`/legislation/trending?limit=${limit}`);
    return response.data;
  },
  
  getDetail: async (id: number): Promise<Legislation> => {
    const response = await api.get(`/legislation/${id}`);
    return response.data;
  },
  
  getMunicipal: async (state: string, city: string, keywords?: string) => {
    const params = new URLSearchParams();
    if (keywords) params.append('keywords', keywords);
    
    const response = await api.get(
      `/legislation/municipal/${state}/${city}?${params.toString()}`
    );
    return response.data;
  },
};

export const simplificationApi = {
  simplify: async (data: SimplificationRequest): Promise<SimplificationResponse> => {
    const response = await api.post('/simplification/', data);
    return response.data;
  },
};

export const searchApi = {
  search: async (data: SearchRequest): Promise<SearchResponse> => {
    const response = await api.post('/search/', data);
    return response.data;
  },
  
  autocomplete: async (query: string): Promise<string[]> => {
    const response = await api.get(`/search/autocomplete?q=${query}`);
    return response.data.suggestions;
  },
  
  getFilters: async () => {
    const response = await api.get('/search/filters');
    return response.data;
  },
};

export const audioApi = {
  transcribe: async (audioBase64: string, language: string = 'pt') => {
    const response = await api.post('/audio/transcribe', {
      audio_base64: audioBase64,
      language,
    });
    return response.data;
  },
  
  textToSpeech: async (text: string, language: string = 'pt') => {
    const response = await api.post('/audio/tts', null, {
      params: { text, language },
    });
    return response.data;
  },
};

export default api;
