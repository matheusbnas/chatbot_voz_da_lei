# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Não Publicado]

### Adicionado
- Integração com busca unificada de legislação (LexML + Senado + Câmara)
- Melhorias no prompt do sistema para linguagem mais acessível
- Suporte a transcrição de áudio via microfone no frontend
- Tratamento de erros melhorado no serviço de áudio
- Fallback para usar Whisper diretamente quando ffmpeg não está disponível
- Documentação de modelo de negócio e análise

### Modificado
- Prompt do sistema otimizado para público-alvo (Classes C, D, E)
- Chat agora busca legislação real antes de responder
- Melhorias no tratamento de formatos de áudio
- README.md atualizado com informações completas

### Corrigido
- Erro de arquivo em uso durante transcrição de áudio
- Problemas com ffmpeg não encontrado
- Melhorias na limpeza de arquivos temporários

## [0.1.0] - 2025-01-XX

### Adicionado
- Sistema inicial de chat com IA
- Integração com OpenAI e Groq
- Simplificação de textos jurídicos
- Transcrição de áudio (Whisper)
- Text-to-Speech (gTTS)
- Integração com LexML
- Integração com Senado Federal
- Integração com Câmara dos Deputados
- Integração com Querido Diário
- Frontend Next.js com chat interativo
- Sistema de busca de legislação
- Docker Compose para desenvolvimento
- Documentação completa

---

## Tipos de Mudanças

- **Adicionado** para novas funcionalidades
- **Modificado** para mudanças em funcionalidades existentes
- **Depreciado** para funcionalidades que serão removidas
- **Removido** para funcionalidades removidas
- **Corrigido** para correções de bugs
- **Segurança** para vulnerabilidades

