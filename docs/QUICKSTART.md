# Guia de Início Rápido - Voz da Lei

## 🚀 Começando em 5 Minutos

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- Docker e Docker Compose (recomendado)

### Opção 1: Docker (Recomendado)

1. **Clone o repositório e entre na pasta**

```bash
cd voz-da-lei
```

2. **Configure as variáveis de ambiente**

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env.local

# Edite os arquivos e adicione suas chaves de API:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY
```

3. **Inicie todos os serviços**

```bash
docker-compose up -d
```

4. **Acesse as aplicações**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentação da API: http://localhost:8000/docs

### Opção 2: Instalação Manual

#### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Iniciar PostgreSQL e Redis localmente
# Ou use Docker para estes serviços:
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=vozdalei123 postgres:15
docker run -d -p 6379:6379 redis:7

# Iniciar servidor
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
# Edite o arquivo .env.local

# Iniciar servidor de desenvolvimento
npm run dev
```

## 🔑 Obtendo Chaves de API

### OpenAI

1. Acesse https://platform.openai.com/
2. Faça login ou crie uma conta
3. Vá em "API Keys"
4. Clique em "Create new secret key"
5. Copie a chave e adicione no `.env`

### Anthropic

1. Acesse https://console.anthropic.com/
2. Faça login ou crie uma conta
3. Vá em "API Keys" nas configurações
4. Clique em "Create Key"
5. Copie a chave e adicione no `.env`

## 📝 Testando a Aplicação

### Testar Backend

```bash
# Verificar saúde da API
curl http://localhost:8000/health

# Testar chat
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "O que é um projeto de lei?"}'

# Buscar legislações em destaque
curl http://localhost:8000/api/v1/legislation/trending?limit=5
```

### Testar Frontend

1. Abra http://localhost:3000 no navegador
2. Clique em "Começar Agora" ou vá para /chat
3. Faça uma pergunta sobre legislação
4. Experimente as funcionalidades de áudio e busca

## 📚 Próximos Passos

1. **Explore a API**: http://localhost:8000/docs
2. **Leia a documentação**: Veja os arquivos em `backend/docs/`
3. **Customize**: Ajuste cores, textos e funcionalidades
4. **Adicione funcionalidades**: Use a estrutura modular

## 🆘 Problemas Comuns

### Erro de conexão com banco de dados

- Verifique se o PostgreSQL está rodando
- Confirme as credenciais no `.env`

### Erro "Module not found"

- Backend: `pip install -r requirements.txt`
- Frontend: `npm install`

### Porta já em uso

- Backend: Mude a porta em `uvicorn app.main:app --port 8001`
- Frontend: Use `npm run dev -- -p 3001`

### Erro com chaves de API

- Verifique se as chaves estão corretas
- Confirme que têm créditos disponíveis
- Teste com uma requisição simples

## 📞 Suporte

- Issues: Abra uma issue no GitHub
- Documentação: Veja `backend/docs/` para documentação técnica
- Email: matheusbnas@gmail.com

## 🎉 Pronto!

Agora você tem o Voz da Lei rodando localmente. Explore, customize e contribua!
