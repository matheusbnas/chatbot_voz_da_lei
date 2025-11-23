# 🎯 Voz da Lei

> **A democracia que você entende, ouve e participa.**

Sistema baseado em Inteligência Artificial que reconecta o cidadão brasileiro às decisões legislativas por meio de uma plataforma acessível que utiliza chatbot multimodal (texto + áudio), linguagem simples e canais inclusivos.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Início Rápido](#início-rápido)
- [Documentação](#documentação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

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

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- Docker e Docker Compose (opcional, mas recomendado)
- PostgreSQL (ou via Docker)
- Redis (ou via Docker)

### Opção 1: Docker (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/matheusbnas/chatbot_povo.git
cd chatbot_povo

# 2. Configure as variáveis de ambiente
cp backend/.env.example backend/.env
# Edite backend/.env e adicione suas chaves de API

# 3. Inicie os serviços
docker-compose up -d

# 4. Acesse
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Opção 2: Instalação Manual

#### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite .env com suas chaves de API

# Iniciar servidor
python -m uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
# Edite .env.local se necessário

# Iniciar servidor de desenvolvimento
npm run dev
```

### Configuração de API Keys

Edite `backend/.env` e adicione:

```env
OPENAI_API_KEY=sua_chave_aqui
GROQ_API_KEY=sua_chave_aqui
```

Veja mais detalhes em [`backend/app/docs/CONFIGURAR_API.md`](backend/app/docs/CONFIGURAR_API.md)

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

Este projeto está protegido por direitos autorais. Todos os direitos reservados.

**É PROIBIDO** copiar, modificar, distribuir, vender ou usar comercialmente sem autorização prévia.

Veja o arquivo [LICENSE](LICENSE) para mais detalhes sobre as restrições e como solicitar permissão de uso.

## 👥 Autores

- **Matheus B. Nascimento** - [GitHub](https://github.com/matheusbnas)

## 🙏 Agradecimentos

- OpenAI e Groq por fornecerem APIs de IA
- LexML, Senado Federal e Câmara dos Deputados por disponibilizarem dados abertos
- Comunidade open source

---

**Voz da Lei** - Democratizando o acesso à legislação brasileira 🎯
