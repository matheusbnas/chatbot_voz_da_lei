#!/usr/bin/env python3
"""
Script para testar a conexão e funcionamento do banco de dados
"""
from app.models.models import Base
from app.core.database import engine, SessionLocal, init_db
from sqlalchemy import text, inspect
import sys
from pathlib import Path

# Adicionar diretório do backend ao path
sys.path.insert(0, str(Path(__file__).parent))


def test_database_connection():
    """Testar conexão com o banco de dados"""
    print("=" * 70)
    print("TESTE DE CONEXÃO COM BANCO DE DADOS")
    print("=" * 70)
    print()

    # Teste 1: Verificar conexão
    print("1. Testando conexao com o banco...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"   [OK] Conexao estabelecida com sucesso!")
            print(f"   PostgreSQL versao: {version}")
    except Exception as e:
        error_msg = str(e)
        print(f"   [ERRO] Erro ao conectar: {error_msg}")
        if "password authentication failed" in error_msg:
            print("   -> Problema de autenticacao. Verifique:")
            print("      - Se o PostgreSQL esta rodando")
            print("      - Se o usuario 'vozdalei' existe")
            print("      - Se a senha esta correta")
            print("      - Se o banco 'vozdalei' foi criado")
        elif "could not connect" in error_msg or "Connection refused" in error_msg:
            print("   -> PostgreSQL nao esta rodando ou nao esta acessivel")
            print("      Execute: docker-compose up -d postgres")
        return False

    print()

    # Teste 2: Verificar se o banco existe
    print("2. Verificando se o banco de dados existe...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"   [OK] Banco de dados atual: {db_name}")
    except Exception as e:
        print(f"   [ERRO] Erro: {str(e)}")
        return False

    print()

    # Teste 3: Verificar tabelas existentes
    print("3. Verificando tabelas existentes...")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if tables:
            print(f"   [OK] Encontradas {len(tables)} tabela(s):")
            for table in sorted(tables):
                print(f"     - {table}")
        else:
            print(
                "   [AVISO] Nenhuma tabela encontrada. O banco precisa ser inicializado.")
    except Exception as e:
        print(f"   [ERRO] Erro ao verificar tabelas: {str(e)}")
        return False

    print()

    # Teste 4: Verificar se as tabelas do modelo existem
    print("4. Verificando tabelas esperadas do modelo...")
    expected_tables = [
        "users", "legislations", "queries", "favorites",
        "municipal_legislations", "ai_feedback", "legislation_chunks",
        "training_corpus", "data_collection_jobs"
    ]

    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        expected_set = set(expected_tables)

        missing = expected_set - existing_tables
        present = expected_set & existing_tables

        if present:
            print(f"   [OK] Tabelas presentes ({len(present)}):")
            for table in sorted(present):
                print(f"     - {table}")

        if missing:
            print(f"   [AVISO] Tabelas faltando ({len(missing)}):")
            for table in sorted(missing):
                print(f"     - {table}")
            print(
                "   -> Execute: python -c 'from app.core.database import init_db; init_db()'")
    except Exception as e:
        print(f"   [ERRO] Erro: {str(e)}")
        return False

    print()

    # Teste 5: Testar operação de escrita/leitura
    print("5. Testando operação de escrita/leitura...")
    try:
        db = SessionLocal()
        try:
            # Teste simples de query
            result = db.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            if test_value == 1:
                print("   [OK] Operacao de leitura funcionando")
            else:
                print(f"   [ERRO] Valor inesperado: {test_value}")
                return False
        finally:
            db.close()
    except Exception as e:
        print(f"   [ERRO] Erro na operacao: {str(e)}")
        return False

    print()
    print("=" * 70)
    print("RESULTADO: Banco de dados esta funcionando corretamente! [OK]")
    print("=" * 70)
    return True


if __name__ == "__main__":
    try:
        success = test_database_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nErro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
