"""
Script de teste para verificar extração de texto completo do LexML
"""
import asyncio
import sys
from pathlib import Path

# Adicionar o diretório app ao path (voltar um nível de tests/ para backend/)
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.legislative_apis import lexml_client


async def test_get_full_text():
    """Testar obtenção de texto completo usando uma URN real"""
    
    # URN de exemplo do LexML (PLS 489/2008 do Senado)
    test_urn = "urn:lex:br:senado.federal:projeto.lei;pls:2008;489"
    
    print("=" * 80)
    print("TESTE: Extração de Texto Completo do LexML")
    print("=" * 80)
    print(f"\nURN de teste: {test_urn}")
    print("\n1. Buscando documento por URN...")
    
    try:
        # Primeiro, buscar o documento
        document = await lexml_client.get_document_by_urn(test_urn)
        
        if document:
            print("[OK] Documento encontrado!")
            print(f"\nTitulo: {document.get('title', 'N/A')}")
            print(f"Tipo: {document.get('tipo_documento', 'N/A')}")
            print(f"Data: {document.get('date', 'N/A')}")
            print(f"URN: {document.get('urn', 'N/A')}")
            print(f"Descricao: {document.get('description', 'N/A')[:200]}...")
            
            # Verificar se tem texto completo
            full_text = document.get('full_text')
            if full_text:
                print("\n" + "=" * 80)
                print("[OK] TEXTO COMPLETO OBTIDO!")
                print("=" * 80)
                print(f"\nTamanho: {len(full_text)} caracteres")
                print(f"\nPrimeiros 500 caracteres:\n{full_text[:500]}...")
                print(f"\nUltimos 200 caracteres:\n...{full_text[-200:]}")
            else:
                print("\n[AVISO] Texto completo nao disponivel")
                print("Tentando buscar texto completo diretamente...")
                
                # Tentar buscar texto completo diretamente
                urn_from_doc = document.get('urn')
                if urn_from_doc:
                    full_text = await lexml_client._get_document_full_text(urn_from_doc)
                    if full_text:
                        print("\n[OK] Texto completo obtido diretamente!")
                        print(f"Tamanho: {len(full_text)} caracteres")
                        print(f"\nPrimeiros 500 caracteres:\n{full_text[:500]}...")
                    else:
                        print("\n[ERRO] Nao foi possivel obter texto completo")
                        print("Possiveis razoes:")
                        print("- Endpoint nao disponivel")
                        print("- Formato XML diferente do esperado")
                        print("- Documento nao tem texto completo disponivel")
        else:
            print("[ERRO] Documento nao encontrado")
            
    except Exception as e:
        print(f"\n[ERRO] Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_search_and_extract():
    """Testar busca e extração de texto de múltiplos documentos"""
    
    print("\n" + "=" * 80)
    print("TESTE: Busca e Extração de Múltiplos Documentos")
    print("=" * 80)
    
    try:
        # Buscar projetos de lei recentes
        print("\n1. Buscando projetos de lei do ano 2008...")
        projects = await lexml_client.search_projects_of_law(year=2008, limit=3)
        
        print(f"[OK] Encontrados {len(projects)} projetos")
        
        for i, doc in enumerate(projects, 1):
            print(f"\n--- Documento {i} ---")
            print(f"Titulo: {doc.get('title', 'N/A')}")
            print(f"URN: {doc.get('urn', 'N/A')}")
            
            # Tentar obter texto completo
            urn = doc.get('urn')
            if urn:
                print("   Tentando obter texto completo...")
                full_text = await lexml_client._get_document_full_text(urn)
                if full_text:
                    print(f"   [OK] Texto obtido ({len(full_text)} caracteres)")
                    print(f"   Preview: {full_text[:200]}...")
                else:
                    print("   [AVISO] Texto completo nao disponivel")
            
    except Exception as e:
        print(f"\n[ERRO] Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n[TESTE] Iniciando testes do LexML...\n")
    
    # Executar testes
    asyncio.run(test_get_full_text())
    asyncio.run(test_search_and_extract())
    
    print("\n" + "=" * 80)
    print("[OK] Testes concluidos!")
    print("=" * 80)

