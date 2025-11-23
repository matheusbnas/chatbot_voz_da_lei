# 🚀 Deploy no Coolify - Voz da Lei

Guia passo a passo para fazer deploy do projeto no **Coolify**.

## 📋 Pré-requisitos

1. **Coolify instalado e rodando** (self-hosted ou cloud)
2. **Acesso ao painel do Coolify**
3. **Repositório Git**: https://github.com/matheusbnas/chatbot_voz_da_lei

## 🎯 Passo a Passo

### 1. Criar Aplicação Backend

1. No painel do Coolify, clique em **"New Resource"** → **"Application"**
2. Escolha **"Git Repository"**
3. Configure:
   - **Repository URL**: `https://github.com/matheusbnas/chatbot_voz_da_lei`
   - **Branch**: `main`
   - **Build Pack**: `Dockerfile`
   - **Base Directory**: `backend/` ⚠️ **IMPORTANTE**: Use `backend/` como base!
   - **Dockerfile Location**: `Dockerfile` (relativo ao Base Directory)
   - **Docker Build Stage Target**: `production`
   - **Port**: `8080` (porta interna do container)
   - **Name**: `vozdalei-backend` (ou outro nome de sua preferência)

### 2. Configurar Variáveis de Ambiente do Backend

Na seção **"Environment Variables"** do backend, adicione:

```env
# Database (use o serviço PostgreSQL do Coolify ou externo)
DATABASE_URL=postgresql://vozdalei:SUA_SENHA@postgres:5432/vozdalei_bd

# Redis (use o serviço Redis do Coolify ou externo)
REDIS_URL=redis://:SUA_SENHA@redis:6379

# API Keys
GROQ_API_KEY=sua_chave_groq_aqui
OPENAI_API_KEY=sua_chave_openai_aqui

# Security
SECRET_KEY=GERE_UMA_CHAVE_SECRETA_FORTE_AQUI
DEBUG=false

# CORS (ajuste com seu domínio)
CORS_ORIGINS=https://seudominio.com,https://www.seudominio.com
```

**⚠️ IMPORTANTE**:

- Gere `SECRET_KEY` com: `openssl rand -hex 32`
- Se usar serviços do Coolify, o host será o nome do serviço (ex: `postgres`, `redis`)

### 3. Configurar Build do Backend

Na seção **"General"** → **"Build"**:

- **Base Directory**: `/` (raiz do projeto)
- **Dockerfile Location**: `backend/Dockerfile`
- **Docker Build Stage Target**: `production` ⚠️ **IMPORTANTE**: Preencha este campo!

**Nota**: O Coolify vai fazer o build a partir da raiz, mas o Dockerfile está em `backend/`, então o build context será a pasta `backend/`.

### 4. Criar Serviço PostgreSQL (se não tiver)

1. **New Resource** → **"Database"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `postgres` (importante para o DATABASE_URL)
   - **Database**: `vozdalei_bd`
   - **User**: `vozdalei`
   - **Password**: (senha forte)
3. Anote a senha para usar no `DATABASE_URL` do backend

### 5. Criar Serviço Redis (se não tiver)

1. **New Resource** → **"Database"** → **"Redis"**
2. Configure:
   - **Name**: `redis` (importante para o REDIS_URL)
   - **Password**: (senha forte)
3. Anote a senha para usar no `REDIS_URL` do backend

### 6. Criar Aplicação Frontend

1. **New Resource** → **"Application"**
2. Escolha **"Git Repository"**
3. Configure:
   - **Repository URL**: `https://github.com/matheusbnas/chatbot_voz_da_lei`
   - **Branch**: `main`
   - **Build Pack**: `Dockerfile`
   - **Base Directory**: `frontend/` ⚠️ **IMPORTANTE**: Use `frontend/` como base!
   - **Dockerfile Location**: `Dockerfile` (relativo ao Base Directory)
   - **Docker Build Stage Target**: `production`
   - **Port**: `3002`
   - **Name**: `vozdalei-frontend` (ou outro nome de sua preferência)

### 7. Configurar Variáveis de Ambiente do Frontend

Na seção **"Environment Variables"** do frontend, adicione:

```env
# URL da API backend (use o domínio do backend no Coolify)
NEXT_PUBLIC_API_URL=https://backend.seudominio.com
# ou se backend e frontend no mesmo domínio:
# NEXT_PUBLIC_API_URL=https://seudominio.com/api

NODE_ENV=production
```

### 8. Configurar Build do Frontend

Na seção **"General"** → **"Build"**:

- **Base Directory**: `/` (raiz do projeto)
- **Dockerfile Location**: `frontend/Dockerfile`
- **Docker Build Stage Target**: `production` ⚠️ **IMPORTANTE**: Preencha este campo!

### 9. Configurar Domínio (Opcional)

Para cada aplicação (backend e frontend):

1. Vá em **"Settings"** → **"Domains"**
2. Adicione seu domínio:
   - Backend: `api.seudominio.com` ou `backend.seudominio.com`
   - Frontend: `seudominio.com` ou `www.seudominio.com`
3. O Coolify gerencia SSL automaticamente (Let's Encrypt)

### 10. Deploy

1. Clique em **"Deploy"** em cada aplicação
2. O Coolify irá:
   - Clonar o repositório
   - Fazer build da imagem Docker
   - Iniciar o container
   - Configurar SSL (se tiver domínio)

### 11. Verificar Deploy

**Backend:**

```bash
# Health check
curl https://api.seudominio.com/health

# Docs
curl https://api.seudominio.com/docs
```

**Frontend:**

```bash
curl https://seudominio.com
```

## 🔧 Configurações Avançadas

### Health Checks

1. Vá em **"Configuration"** → **"Healthcheck"**
2. Configure:
   - **Backend**:
     - **Path**: `/health`
     - **Port**: `8080`
   - **Frontend**:
   - **Path**: `/`
   - **Port**: `3002`

### Custom Docker Options (Opcional)

Se precisar de opções customizadas (como no seu caso), vá em **"General"** → **"Build"** → **"Custom Docker Options"**:

Para backend (se necessário):

```
--build-arg BUILD_TARGET=production
```

**Nota**: Geralmente não é necessário, pois o target já está configurado.

### Recursos (Resources)

Configure limites de recursos se necessário:

- **CPU**: 1-2 cores
- **RAM**: 512MB - 1GB
- **Storage**: Conforme necessário

### Variáveis de Ambiente Sensíveis

Use **"Secrets"** do Coolify para variáveis sensíveis:

1. Vá em **"Settings"** → **"Secrets"**
2. Adicione secrets (ex: `GROQ_API_KEY`, `SECRET_KEY`)
3. Use nos environment variables como: `${{ secrets.GROQ_API_KEY }}`

## 🔄 Atualizar Aplicação

1. Faça push para o repositório Git
2. No Coolify, clique em **"Redeploy"** na aplicação
3. Ou configure **"Auto Deploy"** para deploy automático em cada push

## 📊 Monitoramento

O Coolify fornece:

- **Logs** em tempo real
- **Métricas** de CPU/RAM
- **Status** dos containers
- **Health checks** automáticos

## 🐛 Troubleshooting

### Build Falha

1. Verifique os logs de build no Coolify
2. Confirme que o Dockerfile está correto
3. Verifique se todas as dependências estão no repositório

### Aplicação não inicia

1. Verifique os logs da aplicação
2. Confirme variáveis de ambiente
3. Verifique conexão com PostgreSQL/Redis

### Erro de conexão com banco

1. Confirme que o serviço PostgreSQL está rodando
2. Verifique o `DATABASE_URL` (host deve ser o nome do serviço)
3. Confirme usuário, senha e nome do banco

### Frontend não conecta ao backend

1. Verifique `NEXT_PUBLIC_API_URL` no frontend
2. Confirme CORS no backend (`CORS_ORIGINS`)
3. Verifique se o backend está acessível

## ✅ Checklist

- [ ] Backend criado no Coolify
- [ ] **Dockerfile Location**: `backend/Dockerfile` configurado
- [ ] **Docker Build Stage Target**: `production` preenchido
- [ ] **Port**: `8080` configurado
- [ ] Frontend criado no Coolify
- [ ] **Dockerfile Location**: `frontend/Dockerfile` configurado
- [ ] **Docker Build Stage Target**: `production` preenchido
- [ ] **Port**: `3002` configurado
- [ ] PostgreSQL configurado (ou serviço externo)
- [ ] Redis configurado (ou serviço externo)
- [ ] Variáveis de ambiente configuradas
- [ ] Domínios configurados (opcional)
- [ ] SSL funcionando (automático no Coolify)
- [ ] Health checks configurados
- [ ] Health checks passando
- [ ] Backend respondendo
- [ ] Frontend acessível
- [ ] Frontend conectando ao backend

## 📝 Notas Importantes

1. **Repositório**: https://github.com/matheusbnas/chatbot_voz_da_lei
2. **Porta Backend**: `8080` (interna do container)
3. **Porta Frontend**: `3002` (interna do container)
4. **Banco de Dados**: `vozdalei_bd`
5. **Dockerfile Target**: Use `production` para ambos
6. **Base Directory**: `/` (raiz do projeto)
7. **Dockerfile Location Backend**: `backend/Dockerfile`
8. **Dockerfile Location Frontend**: `frontend/Dockerfile`

## ⚠️ Problema Comum: Build Context

Se o build falhar com erro de arquivo não encontrado:

**Solução**: O Coolify precisa que o Dockerfile esteja configurado corretamente:

- **Base Directory**: `/` (raiz)
- **Dockerfile Location**: `backend/Dockerfile` ou `frontend/Dockerfile`

O Dockerfile já está configurado para usar o contexto correto (`COPY . .` dentro da pasta backend/frontend).

---

**Boa sorte com o deploy no Coolify! 🚀**
