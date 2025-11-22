# Contribuindo com o Voz da Lei

Obrigado por considerar contribuir com o Voz da Lei! Este documento fornece diretrizes para contribuições.

## 🎯 Como Contribuir

### Reportar Bugs

1. Verifique se o bug já não foi reportado nas [Issues](https://github.com/matheusbnas/chatbot_povo/issues)
2. Crie uma nova issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. atual
   - Ambiente (OS, versões, etc.)

### Sugerir Funcionalidades

1. Verifique se a funcionalidade já não foi sugerida
2. Crie uma issue descrevendo:
   - O problema que resolve
   - Como funcionaria
   - Benefícios para os usuários

### Enviar Pull Requests

1. **Fork** o repositório
2. **Crie uma branch** para sua feature/fix:
   ```bash
   git checkout -b feature/minha-feature
   ```
3. **Faça suas alterações** seguindo as convenções:
   - Código limpo e bem documentado
   - Testes quando aplicável
   - Atualize documentação se necessário
4. **Commit** suas mudanças:
   ```bash
   git commit -m "feat: adiciona nova funcionalidade X"
   ```
5. **Push** para sua branch:
   ```bash
   git push origin feature/minha-feature
   ```
6. Abra um **Pull Request** no GitHub

## 📝 Convenções de Código

### Python (Backend)

- Use **Black** para formatação (se configurado)
- Siga **PEP 8**
- Adicione **type hints** quando possível
- Documente funções com **docstrings**
- Use **loguru** para logging

### TypeScript/React (Frontend)

- Use **ESLint** e **Prettier**
- Siga as convenções do Next.js
- Use **TypeScript** para tipagem
- Componentes funcionais com hooks

### Commits

Use o padrão [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Manutenção

Exemplo:
```
feat: adiciona busca por localização
fix: corrige erro de transcrição de áudio
docs: atualiza README com novas instruções
```

## 🧪 Testes

- Adicione testes para novas funcionalidades
- Mantenha cobertura de testes
- Execute testes antes de fazer commit:
  ```bash
  # Backend
  cd backend
  pytest
  
  # Frontend
  cd frontend
  npm test
  ```

## 📚 Documentação

- Atualize README.md se necessário
- Adicione comentários no código
- Documente APIs e endpoints
- Atualize CHANGELOG.md (se existir)

## ✅ Checklist antes de enviar PR

- [ ] Código segue as convenções
- [ ] Testes passam
- [ ] Documentação atualizada
- [ ] Commits seguem padrão
- [ ] Sem warnings ou erros
- [ ] Funciona localmente

## 🤝 Código de Conduta

- Seja respeitoso
- Aceite críticas construtivas
- Foque no que é melhor para o projeto
- Ajude outros contribuidores

## 🎉 Obrigado!

Sua contribuição é muito valiosa para democratizar o acesso à legislação brasileira!

