"""
Script de teste para verificar integração com a API do Senado Federal

Este teste valida:
1. Busca de legislação
2. Obtenção de detalhes de legislação
3. Obtenção de texto completo (quando disponível)
4. Busca de projetos de lei (PLS)
"""
from app.integrations.legislative_apis import senado_client
import asyncio
import sys
from pathlib import Path

# Adicionar o diretório app ao path (voltar um nível de tests/ para backend/)
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_search_legislation():
    """Testar busca de legislação no Senado"""

    print("=" * 80)
    print("TESTE: Busca de Legislação no Senado")
    print("=" * 80)

    try:
        # Buscar legislação recente
        print("\n1. Buscando legislação do ano 2023...")
        results = await senado_client.search_legislation(year=2023, limit=5)

        if results:
            print(f"[OK] Encontradas {len(results)} legislações")
            for i, leg in enumerate(results[:3], 1):
                print(f"\n--- Legislação {i} ---")
                print(f"Estrutura completa (primeiros campos):")
                # Mostrar estrutura real
                for key in list(leg.keys())[:10]:
                    value = leg.get(key)
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  {key}: {value[:100]}...")
                    else:
                        print(f"  {key}: {value}")
                print(f"\nCampos principais:")
                print(
                    f"  ID: {leg.get('id', leg.get('codigo', leg.get('Codigo', 'N/A')))}")
                print(
                    f"  Tipo: {leg.get('tipo', leg.get('siglaTipo', leg.get('SiglaTipo', 'N/A')))}")
                print(
                    f"  Numero: {leg.get('numero', leg.get('numeroMateria', leg.get('NumeroMateria', 'N/A')))}")
                print(
                    f"  Ano: {leg.get('ano', leg.get('anoMateria', leg.get('AnoMateria', 'N/A')))}")
                print(
                    f"  Ementa: {leg.get('ementa', leg.get('Ementa', leg.get('descricao', 'N/A')))[:100]}...")
        else:
            print("[AVISO] Nenhuma legislação encontrada")
            print("Isso pode ser normal se a API estiver usando endpoints diferentes")

    except Exception as e:
        print(f"\n[ERRO] Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_search_projects_of_law():
    """Testar busca de projetos de lei (PLS)"""

    print("\n" + "=" * 80)
    print("TESTE: Busca de Projetos de Lei (PLS) no Senado")
    print("=" * 80)

    try:
        print("\n1. Buscando PLS do ano 2022...")
        projects = await senado_client.search_projects_of_law(year=2022, limit=3)

        if projects:
            print(f"[OK] Encontrados {len(projects)} projetos")
            for i, project in enumerate(projects, 1):
                print(f"\n--- Projeto {i} ---")
                print(f"ID: {project.get('id', 'N/A')}")
                print(f"Numero: {project.get('numero', 'N/A')}")
                print(f"Ano: {project.get('ano', 'N/A')}")
                print(f"Ementa: {project.get('ementa', 'N/A')[:150]}...")

                # Tentar obter texto completo se tiver ID
                project_id = project.get('id')
                if project_id:
                    print(f"   Tentando obter texto completo...")
                    full_text = await senado_client.get_legislation_full_text(str(project_id))
                    if full_text:
                        print(
                            f"   [OK] Texto obtido ({len(full_text)} caracteres)")
                        print(f"   Preview: {full_text[:200]}...")
                    else:
                        print("   [AVISO] Texto completo nao disponivel")
        else:
            print("[AVISO] Nenhum projeto encontrado")

    except Exception as e:
        print(f"\n[ERRO] Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_get_legislation_details():
    """Testar obtenção de detalhes de uma legislação específica"""

    print("\n" + "=" * 80)
    print("TESTE: Detalhes de Legislação Específica")
    print("=" * 80)

    try:
        # Primeiro buscar uma legislação para ter um ID
        print("\n1. Buscando legislação para obter um ID de teste...")
        results = await senado_client.search_legislation(year=2022, limit=1)

        if results and results[0].get('id'):
            test_id = str(results[0]['id'])
            print(f"[OK] ID de teste: {test_id}")

            print(f"\n2. Obtendo detalhes da legislação {test_id}...")
            details = await senado_client.get_legislation_by_id(test_id)

            if details:
                print("[OK] Detalhes obtidos!")
                print(f"\nEstrutura completa (primeiros campos):")
                # Mostrar estrutura real
                for key in list(details.keys())[:15]:
                    value = details.get(key)
                    if isinstance(value, str) and len(value) > 100:
                        print(f"  {key}: {value[:100]}...")
                    elif isinstance(value, (dict, list)):
                        print(
                            f"  {key}: {type(value).__name__} ({len(value) if hasattr(value, '__len__') else 'N/A'})")
                    else:
                        print(f"  {key}: {value}")
                print(f"\nCampos principais:")
                print(
                    f"  Tipo: {details.get('tipo', details.get('siglaTipo', details.get('SiglaTipo', 'N/A')))}")
                print(
                    f"  Numero: {details.get('numero', details.get('numeroMateria', details.get('NumeroMateria', 'N/A')))}")
                print(
                    f"  Ano: {details.get('ano', details.get('anoMateria', details.get('AnoMateria', 'N/A')))}")
                print(
                    f"  Ementa: {details.get('ementa', details.get('Ementa', details.get('descricao', 'N/A')))[:200]}...")
            else:
                print("[AVISO] Detalhes nao disponiveis")
        else:
            print("[AVISO] Nao foi possivel obter um ID para teste")

    except Exception as e:
        print(f"\n[ERRO] Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n[TESTE] Iniciando testes da API do Senado...\n")

    # Executar testes
    asyncio.run(test_search_legislation())
    asyncio.run(test_search_projects_of_law())
    asyncio.run(test_get_legislation_details())

    print("\n" + "=" * 80)
    print("[OK] Testes concluidos!")
    print("=" * 80)
    print("\nNOTA: A API do Senado pode usar endpoints diferentes.")
    print("Se os testes retornarem vazios, verifique a documentação:")
    print("https://legis.senado.leg.br/dadosabertos/api-docs/swagger-ui/index.html")
