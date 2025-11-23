# 🎯 Voz da Lei

> **A democracia que você entende, ouve e participa.**

Sistema baseado em Inteligência Artificial que reconecta o cidadão brasileiro às decisões legislativas por meio de uma plataforma acessível que utiliza chatbot multimodal (texto + áudio), linguagem simples e canais inclusivos.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Instalação e Configuração](#instalação-e-configuração)
- [Uso](#uso)
- [Documentação](#documentação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Roadmap](#roadmap)
- [Contribuindo](#contribuindo)
- [Licença](#licença)
- [Equipe](#equipe)

## 🎯 Sobre o Projeto

O **Voz da Lei** é uma solução de IA cívica inclusiva que visa:

- **Democratizar o acesso** à informação legislativa brasileira
- **Simplificar a linguagem jurídica** para cidadãos de todas as classes sociais
- **Oferecer acesso multimodal** via texto, áudio e SMS
- **Promover transparência** e participação democrática

### Público-Alvo

- **Primário**: Classes C, D e E, comunidades periféricas, jovens eleitores
- **Secundário**: ONGs, escolas públicas, câmaras municipais

## ✨ Funcionalidades

### 🤖 Chat Inteligente

- Conversação natural sobre legislação brasileira
- Busca automática em múltiplas fontes (LexML, Senado, Câmara)
- Respostas em linguagem simples e acessível
- Histórico de conversas

### 🔊 Multimodal

- **Texto**: Chat tradicional
- **Áudio**: Gravação de voz e transcrição automática
- **TTS**: Text-to-Speech para ouvir respostas

### 📚 Simplificação de Textos

- Conversão de linguagem jurídica para linguagem cidadã
- Múltiplos níveis de simplificação
- Cálculo de tempo de leitura

### 🔍 Busca Avançada

- Busca em legislação federal, estadual e municipal
- Filtros por tipo, data, autoridade
- Sugestões inteligentes

### 📊 Fontes de Dados

- **LexML**: Rede de Informação Legislativa e Jurídica
- **Senado Federal**: API de dados abertos
- **Câmara dos Deputados**: API de dados abertos
- **Querido Diário**: Diários oficiais municipais

## 🛠️ Tecnologias

### Backend

- **FastAPI** - Framework web moderno e rápido
- **Python 3.11+** - Linguagem principal
- **PostgreSQL** - Banco de dados relacional
- **Redis** - Cache e sessões
- **LangChain** - Integração com modelos de IA
- **OpenAI / Groq** - Modelos de linguagem
- **Whisper** - Transcrição de áudio
- **SQLAlchemy** - ORM

### Frontend

- **Next.js 14** - Framework React
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Estilização
- **Axios** - Cliente HTTP

### DevOps

- **Docker** - Containerização
- **Docker Compose** - Orquestração

## 🚀 Instalação e Configuração

### Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Docker e Docker Compose** (recomendado) - [Download](https://www.docker.com/)
- **Git** - [Download](https://git-scm.com/)

### Opção 1: Docker (Recomendado) 🐳

A forma mais simples de executar o projeto é usando Docker Compose:

```bash
# 1. Clone o repositório
git clone https://github.com/matheusbnas/chatbot_povo.git
cd chatbot_povo

# 2. Configure as variáveis de ambiente
# Copie o arquivo de exemplo e edite com suas chaves de API
cp backend/.env.example backend/.env

# Edite backend/.env e adicione suas chaves de API:
# OPENAI_API_KEY=sua_chave_aqui
# GROQ_API_KEY=sua_chave_aqui
# ANTHROPIC_API_KEY=sua_chave_aqui (opcional)

# 3. Inicie todos os serviços
docker-compose up -d

# 4. Aguarde alguns segundos para os serviços iniciarem
# Verifique os logs se necessário:
docker-compose logs -f

# 5. Acesse as aplicações:
# Frontend: http://localhost:3002
# Backend API: http://localhost:8000
# Documentação da API: http://localhost:8000/docs
```

**Parar os serviços:**

```bash
docker-compose down
```

**Ver logs:**

```bash
docker-compose logs -f [serviço]  # Ex: backend, frontend, postgres
```

### Opção 2: Instalação Manual

#### Configuração do Backend

```bash
# 1. Navegue até a pasta do backend
cd backend

# 2. Crie um ambiente virtual Python
python -m venv .venv

# 3. Ative o ambiente virtual
# Windows (PowerShell):
.venv\Scripts\activate
# Windows (CMD):
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API

# 6. Certifique-se de que PostgreSQL e Redis estão rodando
# Ou use Docker apenas para esses serviços:
docker run -d --name postgres -e POSTGRES_PASSWORD=senha -p 5432:5432 postgres:15
docker run -d --name redis -p 6379:6379 redis:7

# 7. Execute as migrações do banco (se necessário)
# alembic upgrade head

# 8. Inicie o servidor
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Configuração do Frontend

```bash
# 1. Navegue até a pasta do frontend
cd frontend

# 2. Instale as dependências
npm install

# 3. Configure as variáveis de ambiente (opcional)
# Crie .env.local se necessário:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# 4. Inicie o servidor de desenvolvimento
npm run dev

# O frontend estará disponível em http://localhost:3000
```

### 🔑 Configuração de API Keys

Para que o sistema funcione completamente, você precisa configurar as chaves de API no arquivo `backend/.env`:

```env
# APIs de Inteligência Artificial (obrigatório pelo menos uma)
OPENAI_API_KEY=sua_chave_openai_aqui
GROQ_API_KEY=sua_chave_groq_aqui
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui

# Banco de Dados
DATABASE_URL=postgresql://usuario:senha@localhost:5432/vozdalei_bd

# Redis (Cache)
REDIS_URL=redis://localhost:6379

# Segurança
SECRET_KEY=gerar_uma_chave_secreta_forte_aqui
```

**Como obter as chaves:**

- **OpenAI**: https://platform.openai.com/api-keys
- **Groq**: https://console.groq.com/keys
- **Anthropic**: https://console.anthropic.com/settings/keys

**Gerar SECRET_KEY:**

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -hex 32
```

📖 **Documentação detalhada**: Veja [`backend/app/docs/CONFIGURAR_API.md`](backend/app/docs/CONFIGURAR_API.md) para mais informações.

## 💻 Uso

### Como Usar o Sistema

1. **Acesse o Frontend**: Abra http://localhost:3002 (ou 3000 se instalado manualmente)

2. **Chat Inteligente**:

   - Digite perguntas sobre legislação brasileira
   - O sistema buscará automaticamente em múltiplas fontes
   - Receba respostas em linguagem simples

3. **Simplificação de Textos**:

   - Cole textos jurídicos complexos
   - Receba versões simplificadas e acessíveis
   - Ouça o texto simplificado em áudio

4. **Busca Avançada**:
   - Busque por leis, projetos e documentos
   - Filtre por tipo, data, autoridade
   - Explore resultados de forma intuitiva

### Endpoints da API

A documentação interativa da API está disponível em:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testando a API

```bash
# Exemplo: Testar endpoint de chat
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "O que é a Lei de Acesso à Informação?"}'
```

## 📚 Documentação

- **[QUICKSTART.md](QUICKSTART.md)** - Guia de início rápido detalhado
- **[ARQUITETURA.txt](ARQUITETURA.txt)** - Arquitetura do sistema
- **[COMANDOS.txt](COMANDOS.txt)** - Comandos úteis para desenvolvimento
- **Documentação Técnica**:
  - [Configurar APIs](backend/app/docs/CONFIGURAR_API.md)
  - [Como Coletar Dados](backend/docs/COMO_COLETAR.md)
  - [Guia LexML](backend/docs/README_LEXML.md)
  - [Guia Senado](backend/docs/SENADO_GUIA.md)
  - [Queries Avançadas](backend/docs/QUERIES_AVANCADAS.md)
- **Documentação de Negócio**: [docs/MODELO_NEGOCIO_ANALISE.md](docs/MODELO_NEGOCIO_ANALISE.md)
- **API Docs**: http://localhost:8000/docs (quando o servidor estiver rodando)

## 📁 Estrutura do Projeto

```
chatbot_povo/
├── backend/                 # Backend FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints da API
│   │   ├── ai/              # Serviços de IA
│   │   ├── core/            # Configurações e database
│   │   ├── integrations/   # Integrações com APIs externas
│   │   ├── models/          # Modelos de banco de dados
│   │   ├── schemas/         # Schemas Pydantic
│   │   └── services/        # Serviços de negócio
│   ├── tests/               # Testes
│   └── requirements.txt     # Dependências Python
│
├── frontend/                 # Frontend Next.js
│   ├── src/
│   │   ├── app/             # Páginas Next.js
│   │   ├── components/      # Componentes React
│   │   └── services/        # Serviços e API client
│   └── package.json         # Dependências Node
│
├── docker-compose.yml       # Orquestração Docker
├── README.md               # Este arquivo
└── docs/                   # Documentação adicional
```

## 🎯 Roadmap

### Fase 1: Funcionalidades Core ✅

- [x] Chat com busca de legislação
- [x] Simplificação de textos
- [x] Transcrição de áudio
- [x] Integração com LexML, Senado e Câmara

### Fase 2: Canais Inclusivos 🚧

- [ ] Integração SMS
- [ ] PWA (Progressive Web App)
- [ ] Modo offline

### Fase 3: Equidade e Acessibilidade 🚧

- [ ] Módulo de equidade algorítmica
- [ ] Acessibilidade completa (leitores de tela)
- [ ] Análise de viés

### Fase 4: Engagement 📋

- [ ] Radar legislativo local
- [ ] Retorno ao representante
- [ ] Resumo automático de projetos

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

Você é livre para:

- ✅ Usar o projeto para fins comerciais ou pessoais
- ✅ Modificar e adaptar conforme necessário
- ✅ Distribuir o código
- ✅ Usar em projetos privados

**Requisitos:**

- Manter o aviso de copyright e a licença em todas as cópias
- Incluir o arquivo LICENSE completo

Para mais informações, consulte o arquivo [LICENSE](LICENSE).

## 👥 Equipe

- **Matheus B. Nascimento** - [GitHub](https://github.com/matheusbnas) - matheusbnas@gmail.com
- **Alexandre Cruz** - Alexandrescruzwork@gmail.com
- **Samir** - scarneirojose@gmail.com

## 🙏 Agradecimentos

- OpenAI e Groq por fornecerem APIs de IA
- LexML, Senado Federal e Câmara dos Deputados por disponibilizarem dados abertos
- Comunidade open source

---

**Voz da Lei** - Democratizando o acesso à legislação brasileira 🎯
