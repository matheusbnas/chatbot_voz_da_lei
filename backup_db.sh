#!/bin/bash

# Script de Backup do Banco de Dados - Voz da Lei
# Uso: ./backup_db.sh

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Criar diretório de backups se não existir
mkdir -p $BACKUP_DIR

echo -e "${GREEN}💾 Iniciando backup do banco de dados...${NC}"

# Carregar variáveis de ambiente se .env.prod existir
if [ -f ".env.prod" ]; then
    export $(cat .env.prod | grep -v '^#' | xargs)
fi

# Fazer backup
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U ${POSTGRES_USER:-vozdalei} ${POSTGRES_DB:-vozdalei_bd} > $BACKUP_FILE

# Comprimir backup
echo -e "${GREEN}📦 Comprimindo backup...${NC}"
gzip $BACKUP_FILE
BACKUP_FILE="${BACKUP_FILE}.gz"

# Verificar se backup foi criado
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup criado com sucesso!${NC}"
    echo -e "   Arquivo: $BACKUP_FILE"
    echo -e "   Tamanho: $SIZE"
else
    echo -e "${YELLOW}⚠️  Erro ao criar backup!${NC}"
    exit 1
fi

# Manter apenas últimos 7 dias de backups
echo -e "${GREEN}🧹 Removendo backups antigos (mais de 7 dias)...${NC}"
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo -e "${GREEN}✅ Backup concluído!${NC}"

