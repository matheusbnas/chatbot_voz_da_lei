# Como Criar o Banco de Dados PostgreSQL

O erro "password authentication failed" indica que o usuário `vozdalei` não existe no PostgreSQL. Siga estes passos para criar:

## 🔧 Opção 1: Usando pgAdmin 4 (Mais Fácil)

1. **Conecte-se como superusuário** (geralmente `postgres`):
   - No pgAdmin, clique com botão direito em "Servers" → "Create" → "Server..."
   - Use as credenciais do seu PostgreSQL (geralmente usuário `postgres` e a senha que você configurou)

2. **Abra o Query Tool**:
   - Clique com botão direito no servidor conectado → "Query Tool"

3. **Execute este SQL**:
   ```sql
   -- Criar usuário
   CREATE USER vozdalei WITH PASSWORD 'vozdalei123';
   
   -- Criar banco de dados
   CREATE DATABASE vozdalei OWNER vozdalei;
   
   -- Conceder privilégios
   GRANT ALL PRIVILEGES ON DATABASE vozdalei TO vozdalei;
   ```

4. **Conecte ao banco vozdalei e conceda privilégios no schema**:
   - Conecte-se ao banco `vozdalei` (clique duas vezes nele)
   - Abra o Query Tool novamente
   - Execute:
   ```sql
   GRANT ALL ON SCHEMA public TO vozdalei;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vozdalei;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vozdalei;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO vozdalei;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO vozdalei;
   ```

## 🔧 Opção 2: Usando psql (Linha de Comando)

1. **Abra o PowerShell ou Prompt de Comando**

2. **Conecte-se ao PostgreSQL como superusuário**:
   ```bash
   psql -U postgres
   ```
   (Digite a senha do usuário postgres quando solicitado)

3. **Execute os comandos SQL**:
   ```sql
   CREATE USER vozdalei WITH PASSWORD 'vozdalei123';
   CREATE DATABASE vozdalei OWNER vozdalei;
   GRANT ALL PRIVILEGES ON DATABASE vozdalei TO vozdalei;
   \q
   ```

4. **Conecte-se ao banco vozdalei e conceda privilégios**:
   ```bash
   psql -U postgres -d vozdalei
   ```
   ```sql
   GRANT ALL ON SCHEMA public TO vozdalei;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vozdalei;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vozdalei;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO vozdalei;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO vozdalei;
   \q
   ```

## 🔧 Opção 3: Usando Arquivo SQL

1. **Conecte-se ao PostgreSQL como superusuário** no pgAdmin

2. **Abra o Query Tool** e execute o conteúdo do arquivo:
   - `backend/create_database_simple.sql` (versão simples)
   - `backend/create_database.sql` (versão completa com verificações)

## ✅ Verificar se Funcionou

Após criar o usuário e banco:

1. **No pgAdmin, tente conectar novamente** com:
   - Host: `localhost`
   - Port: `5432`
   - Username: `vozdalei`
   - Password: `vozdalei123`
   - Database: `vozdalei`

2. **Se conectar com sucesso**, inicialize as tabelas:
   ```bash
   cd backend
   python -c "from app.core.database import init_db; init_db()"
   ```

## ⚠️ Problemas Comuns

### "role 'vozdalei' already exists"
O usuário já existe. Você pode:
- Usar o usuário existente (se souber a senha)
- Ou alterar a senha: `ALTER USER vozdalei WITH PASSWORD 'vozdalei123';`

### "database 'vozdalei' already exists"
O banco já existe. Você pode:
- Usar o banco existente
- Ou deletar e recriar (CUIDADO: apaga todos os dados):
  ```sql
  DROP DATABASE vozdalei;
  CREATE DATABASE vozdalei OWNER vozdalei;
  ```

### Não consegue conectar como postgres
- Verifique se você tem as credenciais do superusuário
- No Windows, o PostgreSQL geralmente usa a senha que você configurou durante a instalação
- Se não lembrar, pode ser necessário redefinir a senha do postgres

