#!/bin/bash

# Script de Deploy Automatizado - Voz da Lei
# Uso: ./deploy.sh

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens
print_info() {
    echo -e "${GREEN}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Verificar se está no diretório correto
if [ ! -f "docker-compose.prod.yml" ]; then
    print_error "Arquivo docker-compose.prod.yml não encontrado!"
    print_info "Execute este script do diretório raiz do projeto."
    exit 1
fi

# Verificar se .env.prod existe
if [ ! -f ".env.prod" ]; then
    print_warning "Arquivo .env.prod não encontrado!"
    print_info "Copiando .env.example para .env.prod..."
    if [ -f ".env.example" ]; then
        cp .env.example .env.prod
        print_warning "Por favor, edite o arquivo .env.prod com suas configurações antes de continuar!"
        exit 1
    else
        print_error "Arquivo .env.example também não encontrado!"
        exit 1
    fi
fi

print_info "🚀 Iniciando deploy do Voz da Lei..."

# Carregar variáveis de ambiente
print_info "📋 Carregando variáveis de ambiente..."
export $(cat .env.prod | grep -v '^#' | xargs)

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    print_error "Docker não está rodando ou você não tem permissão!"
    exit 1
fi

# Parar serviços antigos
print_info "⏹️  Parando serviços existentes..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod down || true

# Limpar imagens antigas (opcional - descomente se necessário)
# print_info "🧹 Limpando imagens antigas..."
# docker system prune -f

# Build das imagens
print_info "🔨 Construindo imagens Docker..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache

# Iniciar serviços de infraestrutura primeiro
print_info "🗄️  Iniciando PostgreSQL e Redis..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d postgres redis

# Aguardar serviços estarem prontos
print_info "⏳ Aguardando serviços de infraestrutura iniciarem..."
sleep 15

# Verificar saúde do PostgreSQL
print_info "🏥 Verificando saúde do PostgreSQL..."
for i in {1..30}; do
    if docker-compose -f docker-compose.prod.yml --env-file .env.prod exec -T postgres pg_isready -U ${POSTGRES_USER:-vozdalei} > /dev/null 2>&1; then
        print_success "PostgreSQL está pronto!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "PostgreSQL não iniciou a tempo!"
        exit 1
    fi
    sleep 1
done

# Verificar saúde do Redis
print_info "🏥 Verificando saúde do Redis..."
for i in {1..30}; do
    if docker-compose -f docker-compose.prod.yml --env-file .env.prod exec -T redis redis-cli --raw incr ping > /dev/null 2>&1; then
        print_success "Redis está pronto!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Redis não iniciou a tempo!"
        exit 1
    fi
    sleep 1
done

# Executar migrações (se houver)
if [ -f "backend/alembic.ini" ]; then
    print_info "🔄 Executando migrações do banco de dados..."
    docker-compose -f docker-compose.prod.yml --env-file .env.prod run --rm backend alembic upgrade head || print_warning "Nenhuma migração encontrada ou erro ao executar."
fi

# Iniciar todos os serviços
print_info "▶️  Iniciando todos os serviços..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Aguardar serviços iniciarem
print_info "⏳ Aguardando serviços iniciarem completamente..."
sleep 20

# Verificar status dos serviços
print_info "📊 Verificando status dos serviços..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod ps

# Verificar saúde dos serviços
print_info "🏥 Verificando saúde dos serviços..."
sleep 10

# Testar endpoints
print_info "🧪 Testando endpoints..."

# Backend health check
if curl -f http://localhost:3001/health > /dev/null 2>&1; then
    print_success "Backend está respondendo!"
else
    print_warning "Backend pode não estar totalmente pronto ainda."
fi

# Frontend health check
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend está respondendo!"
else
    print_warning "Frontend pode não estar totalmente pronto ainda."
fi

# Resumo
echo ""
print_success "Deploy concluído!"
echo ""
print_info "📋 Próximos passos:"
echo "  1. Verifique os logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  2. Acesse o frontend: http://localhost:3000"
echo "  3. Acesse a API: http://localhost:3001"
echo "  4. Documentação da API: http://localhost:3001/docs"
echo ""
print_info "📊 Para ver o status: docker-compose -f docker-compose.prod.yml ps"
print_info "📝 Para ver logs: docker-compose -f docker-compose.prod.yml logs -f [servico]"
echo ""

