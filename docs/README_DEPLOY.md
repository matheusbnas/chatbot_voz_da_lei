# 🚀 Guia de Deploy - Voz da Lei

Este guia fornece instruções completas para fazer o deploy do projeto **Voz da Lei** em um servidor de produção.

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Preparação do Servidor](#preparação-do-servidor)
- [Configuração](#configuração)
- [Deploy](#deploy)
- [Pós-Deploy](#pós-deploy)
- [Monitoramento](#monitoramento)
- [Backup e Restauração](#backup-e-restauração)
- [Troubleshooting](#troubleshooting)

## 🔧 Pré-requisitos

### Servidor

- **Sistema Operacional**: Ubuntu 20.04+ ou Debian 11+ (recomendado)
- **RAM**: Mínimo 4GB (recomendado 8GB+)
- **CPU**: Mínimo 2 cores (recomendado 4+ cores)
- **Disco**: Mínimo 20GB de espaço livre
- **Rede**: Acesso à internet e porta 80/443 abertas

### Software Necessário

```bash
# Docker e Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Git (para clonar o repositório)
sudo apt install -y git

# Certbot (para SSL - opcional)
sudo apt install -y certbot python3-certbot-nginx
```

## 🖥️ Preparação do Servidor

### 1. Criar Usuário para Deploy (Recomendado)

```bash
# Criar usuário
sudo adduser vozdalei
sudo usermod -aG docker vozdalei
sudo usermod -aG sudo vozdalei

# Fazer login como novo usuário
su - vozdalei
```

### 2. Clonar o Repositório

```bash
cd /home/vozdalei
git clone https://github.com/matheusbnas/chatbot_voz_da_lei.git
cd chatbot_voz_da_lei
```

### 3. Configurar Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Ou iptables (Debian)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

## ⚙️ Configuração

### 1. Criar Arquivo de Variáveis de Ambiente

```bash
cd /home/vozdalei/chatbot_voz_da_lei
cp .env.example .env.prod
nano .env.prod
```

### 2. Configurar Variáveis de Ambiente

Edite o arquivo `.env.prod` com as seguintes variáveis:

```env
# Database
POSTGRES_USER=vozdalei
POSTGRES_PASSWORD=SUA_SENHA_FORTE_AQUI
POSTGRES_DB=vozdalei_bd
POSTGRES_PORT=5432
DATABASE_URL=postgresql://vozdalei:SUA_SENHA_FORTE_AQUI@postgres:5432/vozdalei_bd

# Redis
REDIS_PASSWORD=SUA_SENHA_REDIS_AQUI
REDIS_PORT=6379
REDIS_URL=redis://:SUA_SENHA_REDIS_AQUI@redis:6379

# API Keys
OPENAI_API_KEY=sua_chave_openai_aqui
GROQ_API_KEY=sua_chave_groq_aqui

# Security
SECRET_KEY=$(openssl rand -hex 32)

# CORS (ajuste com seu domínio)
CORS_ORIGINS=https://seudominio.com,https://www.seudominio.com

# Frontend
NEXT_PUBLIC_API_URL=https://api.seudominio.com
# ou se backend e frontend no mesmo domínio:
# NEXT_PUBLIC_API_URL=https://seudominio.com/api
```

**⚠️ IMPORTANTE**:

- Use senhas fortes (mínimo 16 caracteres)
- Gere SECRET_KEY com: `openssl rand -hex 32`
- Nunca commite o arquivo `.env.prod` no Git

### 3. Configurar Nginx (Opcional - para domínio próprio)

Crie o diretório e arquivo de configuração:

```bash
mkdir -p nginx/ssl
nano nginx/nginx.conf
```

Exemplo de configuração Nginx:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8080;
    }

    upstream frontend {
        server frontend:3002;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name seudominio.com www.seudominio.com;
        return 301 https://$server_name$request_uri;
    }

    # Frontend
    server {
        listen 443 ssl http2;
        server_name seudominio.com www.seudominio.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
    }

    # Backend API
    server {
        listen 443 ssl http2;
        server_name api.seudominio.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        location / {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 4. Obter Certificado SSL (Let's Encrypt)

```bash
# Parar nginx temporariamente
docker-compose -f docker-compose.prod.yml stop nginx

# Obter certificado
sudo certbot certonly --standalone -d seudominio.com -d www.seudominio.com -d api.seudominio.com

# Copiar certificados para o diretório do projeto
sudo cp /etc/letsencrypt/live/seudominio.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/seudominio.com/privkey.pem nginx/ssl/
sudo chmod 644 nginx/ssl/fullchain.pem
sudo chmod 600 nginx/ssl/privkey.pem
```

## 🚀 Deploy

### Opção 1: Deploy Completo (Recomendado)

```bash
cd /home/vozdalei/chatbot_voz_da_lei

# Carregar variáveis de ambiente
export $(cat .env.prod | xargs)

# Build e iniciar serviços
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Verificar status
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Opção 2: Deploy Passo a Passo

```bash
# 1. Build das imagens
docker-compose -f docker-compose.prod.yml --env-file .env.prod build

# 2. Iniciar banco de dados e Redis
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d postgres redis

# 3. Aguardar serviços estarem prontos
sleep 10

# 4. Executar migrações (se houver)
docker-compose -f docker-compose.prod.yml --env-file .env.prod run --rm backend alembic upgrade head

# 5. Iniciar todos os serviços
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 6. Verificar saúde dos serviços
docker-compose -f docker-compose.prod.yml ps
```

### Script de Deploy Automatizado

Crie um script `deploy.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Iniciando deploy do Voz da Lei..."

# Carregar variáveis
export $(cat .env.prod | xargs)

# Parar serviços antigos
echo "⏹️  Parando serviços..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod down

# Build
echo "🔨 Construindo imagens..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache

# Iniciar serviços
echo "▶️  Iniciando serviços..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Aguardar serviços
echo "⏳ Aguardando serviços iniciarem..."
sleep 15

# Verificar saúde
echo "🏥 Verificando saúde dos serviços..."
docker-compose -f docker-compose.prod.yml ps

echo "✅ Deploy concluído!"
echo "📊 Acesse os logs com: docker-compose -f docker-compose.prod.yml logs -f"
```

Tornar executável:

```bash
chmod +x deploy.sh
./deploy.sh
```

## 📊 Pós-Deploy

### 1. Verificar Serviços

```bash
# Status dos containers
docker-compose -f docker-compose.prod.yml ps

# Logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f

# Logs de um serviço específico
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 2. Testar Endpoints

```bash
# Health check do backend
curl http://localhost:3001/health

# Health check do frontend
curl http://localhost:3002

# API Docs
curl http://localhost:3001/docs
```

### 3. Verificar Banco de Dados

```bash
# Conectar ao PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres psql -U vozdalei -d vozdalei_bd

# Verificar tabelas
\dt

# Sair
\q
```

### 4. Verificar Redis

```bash
# Conectar ao Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a SUA_SENHA_REDIS_AQUI

# Testar
PING
KEYS *
```

## 📈 Monitoramento

### 1. Logs

```bash
# Todos os logs
docker-compose -f docker-compose.prod.yml logs -f

# Logs específicos
docker-compose -f docker-compose.prod.yml logs -f backend | grep ERROR
```

### 2. Recursos do Sistema

```bash
# Uso de recursos dos containers
docker stats

# Espaço em disco
df -h
docker system df
```

### 3. Health Checks

Os containers têm health checks configurados. Verifique com:

```bash
docker-compose -f docker-compose.prod.yml ps
```

Status `healthy` indica que o serviço está funcionando corretamente.

### 4. Monitoramento Avançado (Opcional)

Considere usar ferramentas como:

- **Prometheus** + **Grafana** para métricas
- **Sentry** para rastreamento de erros
- **Uptime Robot** para monitoramento de disponibilidade

## 💾 Backup e Restauração

### Backup do Banco de Dados

```bash
# Backup manual
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U vozdalei vozdalei_bd > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup automático (criar script)
cat > backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/vozdalei/chatbot_voz_da_lei/backups"
mkdir -p $BACKUP_DIR
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U vozdalei vozdalei_bd > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql
# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x backup_db.sh

# Adicionar ao crontab (backup diário às 2h)
crontab -e
# Adicionar linha:
# 0 2 * * * /home/vozdalei/chatbot_voz_da_lei/backup_db.sh
```

### Restauração do Banco de Dados

```bash
# Restaurar backup
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U vozdalei vozdalei_bd < backup_20240101_120000.sql
```

### Backup do Redis

```bash
# Redis salva automaticamente (AOF habilitado)
# Para backup manual:
docker-compose -f docker-compose.prod.yml exec redis redis-cli -a SUA_SENHA BGSAVE
```

## 🔧 Troubleshooting

### Problema: Container não inicia

```bash
# Ver logs detalhados
docker-compose -f docker-compose.prod.yml logs backend

# Verificar variáveis de ambiente
docker-compose -f docker-compose.prod.yml config

# Reiniciar container
docker-compose -f docker-compose.prod.yml restart backend
```

### Problema: Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
docker-compose -f docker-compose.prod.yml ps postgres

# Verificar logs do PostgreSQL
docker-compose -f docker-compose.prod.yml logs postgres

# Testar conexão
docker-compose -f docker-compose.prod.yml exec postgres psql -U vozdalei -d vozdalei_bd -c "SELECT 1;"
```

### Problema: Frontend não carrega

```bash
# Verificar build
docker-compose -f docker-compose.prod.yml logs frontend

# Rebuild
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

### Problema: Porta já em uso

```bash
# Verificar qual processo está usando a porta
sudo lsof -i :3001
sudo lsof -i :3002

# Parar processo ou mudar porta no docker-compose.prod.yml
```

### Limpar e Recomeçar

```bash
# Parar tudo
docker-compose -f docker-compose.prod.yml down

# Remover volumes (CUIDADO: apaga dados!)
docker-compose -f docker-compose.prod.yml down -v

# Limpar imagens antigas
docker system prune -a

# Rebuild completo
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

## 🔄 Atualização

Para atualizar o projeto:

```bash
cd /home/vozdalei/chatbot_voz_da_lei

# Fazer backup
./backup_db.sh

# Atualizar código
git pull origin main

# Rebuild e restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Verificar
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

## 📝 Checklist de Deploy

- [ ] Servidor configurado com Docker e Docker Compose
- [ ] Firewall configurado (portas 80, 443, 22)
- [ ] Arquivo `.env.prod` configurado com todas as variáveis
- [ ] Senhas fortes definidas
- [ ] SECRET_KEY gerado
- [ ] API Keys configuradas (OpenAI, Groq)
- [ ] CORS configurado com domínio correto
- [ ] Certificado SSL obtido (se usando domínio)
- [ ] Nginx configurado (se usando domínio)
- [ ] Backup automático configurado
- [ ] Health checks funcionando
- [ ] Logs sendo monitorados
- [ ] Testes de endpoints realizados

## 🆘 Suporte

Em caso de problemas:

1. Verifique os logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Verifique o status: `docker-compose -f docker-compose.prod.yml ps`
3. Consulte a documentação: `README.md`, `ARQUITETURA.txt`
4. Abra uma issue no GitHub

---

**Boa sorte com o deploy! 🚀**
