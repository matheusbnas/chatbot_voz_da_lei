# Documentação Técnica - Voz da Lei

## Arquitetura do Sistema

### Visão Geral

O sistema "Voz da Lei" é composto por três camadas principais:

1. **Frontend (Next.js)**: Interface do usuário
2. **Backend (FastAPI)**: API e lógica de negócio
3. **Serviços Externos**: APIs governamentais e IA

```
┌─────────────┐
│   Frontend  │
│  (Next.js)  │
└──────┬──────┘
       │ HTTP/REST
┌──────▼──────┐
│   Backend   │
│  (FastAPI)  │
└──────┬──────┘
       │
       ├─── PostgreSQL (Dados)
       ├─── Redis (Cache)
       ├─── OpenAI/Anthropic (IA)
       └─── APIs Governamentais
```

## Backend (Python/FastAPI)

### Estrutura de Diretórios

```
backend/
├── app/
│   ├── main.py                 # Aplicação principal
│   ├── core/
│   │   └── config.py          # Configurações
│   ├── models/
│   │   └── models.py          # Modelos SQLAlchemy
│   ├── schemas/
│   │   └── schemas.py         # Schemas Pydantic
│   ├── api/
│   │   └── v1/
│   │       ├── chat.py        # Rotas de chat
│   │       ├── legislation.py # Rotas de legislação
│   │       ├── simplification.py
│   │       ├── search.py
│   │       └── audio.py
│   ├── ai/
│   │   └── simplification.py  # Serviços de IA
│   ├── services/
│   │   └── audio.py           # Processamento de áudio
│   └── integrations/
│       └── legislative_apis.py # Integrações externas
└── requirements.txt
```

### Principais Tecnologias

- **FastAPI**: Framework web assíncrono
- **SQLAlchemy**: ORM para banco de dados
- **LangChain**: Framework para IA
- **Whisper**: Transcrição de áudio
- **gTTS**: Text-to-Speech

### Endpoints Principais

#### Chat
- `POST /api/v1/chat/` - Enviar mensagem
- `GET /api/v1/chat/suggestions` - Obter sugestões

#### Legislação
- `GET /api/v1/legislation/trending` - Legislações em destaque
- `GET /api/v1/legislation/{id}` - Detalhes de legislação
- `GET /api/v1/legislation/municipal/{state}/{city}` - Legislação municipal

#### Simplificação
- `POST /api/v1/simplification/` - Simplificar texto
- `POST /api/v1/simplification/batch` - Simplificar múltiplos textos

#### Busca
- `POST /api/v1/search/` - Buscar legislação
- `GET /api/v1/search/autocomplete` - Autocompletar

#### Áudio
- `POST /api/v1/audio/transcribe` - Transcrever áudio
- `POST /api/v1/audio/tts` - Text-to-Speech
- `GET /api/v1/audio/{filename}` - Obter arquivo de áudio

### Modelos de Dados

#### User
- ID, email, username, senha (hash)
- Perfil completo, status de verificação

#### Legislation
- Informações completas da legislação
- Texto original e simplificado
- Metadados (autor, data, status)

#### Query
- Histórico de consultas dos usuários
- Respostas geradas pela IA

### Integrações com APIs Externas

1. **Câmara dos Deputados**
   - URL: https://dadosabertos.camara.leg.br/api/v2
   - Proposições, votações, deputados

2. **Senado Federal**
   - URL: https://legis.senado.leg.br/dadosabertos
   - Matérias, senadores

3. **Querido Diário**
   - URL: https://queridodiario.ok.org.br/api
   - Diários oficiais municipais

4. **Base dos Dados**
   - Dados públicos tratados
   - Acesso via BigQuery

## Frontend (Next.js)

### Estrutura de Diretórios

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx           # Página inicial
│   │   ├── layout.tsx         # Layout principal
│   │   ├── globals.css        # Estilos globais
│   │   └── chat/
│   │       └── page.tsx       # Página de chat
│   ├── components/            # Componentes reutilizáveis
│   ├── services/
│   │   └── api.ts            # Cliente da API
│   ├── hooks/                # Hooks customizados
│   └── lib/                  # Utilitários
└── package.json
```

### Principais Tecnologias

- **Next.js 14**: Framework React com App Router
- **TypeScript**: Tipagem estática
- **Tailwind CSS**: Estilização
- **Axios**: Cliente HTTP
- **Zustand**: Gerenciamento de estado (se necessário)

### Páginas

1. **Home** (`/`): Landing page com apresentação
2. **Chat** (`/chat`): Interface de chat interativo
3. **Search** (`/search`): Busca de legislação
4. **Trending** (`/trending`): Legislações em destaque
5. **Detail** (`/legislation/[id]`): Detalhes de legislação

### Componentes Principais

- **ChatInterface**: Interface de chat com histórico
- **LegislationCard**: Card de exibição de legislação
- **SearchBar**: Barra de busca com autocomplete
- **AudioRecorder**: Gravação e transcrição de áudio
- **SimplificationPanel**: Painel de simplificação

## Banco de Dados

### PostgreSQL

Tabelas principais:
- `users`: Usuários do sistema
- `legislations`: Legislações armazenadas
- `queries`: Histórico de consultas
- `favorites`: Favoritos dos usuários
- `municipal_legislations`: Legislação municipal
- `ai_feedback`: Feedback sobre respostas da IA

### Redis

Uso:
- Cache de respostas frequentes
- Sessões de usuário
- Filas do Celery

## Serviços de IA

### Simplificação de Texto

Usa LangChain + OpenAI/Anthropic para:
- Traduzir juridiquês para linguagem simples
- Três níveis de simplificação (simple, moderate, technical)
- Manter precisão jurídica

### Chat Interativo

- Contextualização com histórico de conversa
- Geração de sugestões de perguntas
- Busca semântica em legislações

### Processamento de Áudio

- **Whisper**: Transcrição de áudio para texto
- **gTTS**: Conversão de texto para áudio
- Suporte a múltiplos formatos (MP3, WAV, OGG)

## Deployment

### Docker Compose (Desenvolvimento)

```bash
# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços
docker-compose down

# Ver logs
docker-compose logs -f
```

### Variáveis de Ambiente Necessárias

#### Backend
- `OPENAI_API_KEY`: Chave da API OpenAI
- `ANTHROPIC_API_KEY`: Chave da API Anthropic
- `DATABASE_URL`: URL do PostgreSQL
- `REDIS_URL`: URL do Redis

#### Frontend
- `NEXT_PUBLIC_API_URL`: URL da API backend

### Produção

Recomendações:
- **Backend**: Deploy em servidores com suporte a Python (Railway, Render, AWS)
- **Frontend**: Vercel, Netlify ou similar
- **Banco de Dados**: PostgreSQL gerenciado (AWS RDS, Supabase)
- **Cache**: Redis gerenciado
- **CDN**: Para arquivos de áudio

## Segurança

1. **Autenticação**: JWT tokens
2. **CORS**: Configurado para origens permitidas
3. **Rate Limiting**: Proteção contra abuso
4. **Validação**: Pydantic schemas no backend
5. **Sanitização**: Validação de entrada de usuário

## Monitoramento

- **Logs**: Loguru no backend
- **Métricas**: Acompanhar uso de APIs
- **Erros**: Rastreamento de exceções
- **Performance**: Tempo de resposta das requisições

## Testes

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

## Manutenção

### Limpeza de Arquivos Temporários

O serviço de áudio mantém arquivos por 7 dias. Para limpeza manual:

```python
from app.services.audio import audio_service
audio_service.cleanup_old_files(days=7)
```

### Atualização de Legislações

Recomenda-se executar job diário para:
1. Buscar novas proposições
2. Atualizar status de proposições existentes
3. Simplificar novos textos

## Performance

### Otimizações Implementadas

1. **Cache Redis**: Respostas frequentes
2. **Paginação**: Todas as listagens
3. **Lazy Loading**: Carregamento sob demanda
4. **Debounce**: Em buscas e autocomplete
5. **Async/Await**: Operações assíncronas

### Benchmarks Esperados

- Chat: < 2s para resposta
- Simplificação: < 3s para textos de até 5000 caracteres
- Busca: < 1s para resultados
- TTS: < 2s para textos de até 1000 caracteres

## Próximos Passos

1. Implementar autenticação completa
2. Adicionar sistema de notificações
3. Interface SMS via Twilio
4. Dashboard de analytics
5. Sistema de feedback aos representantes
6. App mobile (React Native)
7. Suporte a mais municípios
8. Integração com Base dos Dados via BigQuery

## Contato e Suporte

Para questões técnicas, abra uma issue no repositório ou entre em contato com a equipe de desenvolvimento.
