# Análise e Plano de Ação - Voz da Lei

## Alinhamento do Código com o Modelo de Negócio

---

## 📊 Status Atual vs. Modelo de Negócio

### ✅ **O QUE JÁ ESTÁ IMPLEMENTADO**

#### 1. **Chatbot Multimodal (Texto + Áudio)**

- ✅ Chat via texto (`/api/v1/chat/`)
- ✅ Transcrição de áudio (Whisper) - `/api/v1/audio/transcribe`
- ✅ Text-to-Speech (gTTS) - `/api/v1/audio/tts`
- ✅ Suporte a áudio no chat (`use_audio: true`)
- ✅ Interface web com chat

#### 2. **Simplificação Inteligente**

- ✅ Simplificação de textos jurídicos (`/api/v1/simplification/`)
- ✅ Níveis de simplificação (simple, moderate, technical)
- ✅ Integração com IA (OpenAI/Groq)
- ✅ Cálculo de tempo de leitura

#### 3. **Fontes de Dados**

- ✅ Câmara dos Deputados (API integrada)
- ✅ Senado Federal (API integrada e testada)
- ✅ LexML (API integrada com extração de texto)
- ✅ Querido Diário (cliente implementado)
- ⚠️ Base dos Dados (configurado, não usado)
- ❌ TSE (não implementado)
- ❌ DataJud CNJ (não implementado)

#### 4. **Infraestrutura**

- ✅ Backend FastAPI
- ✅ Frontend Next.js
- ✅ Banco de dados (PostgreSQL)
- ✅ Redis (configurado)
- ✅ Sistema de logs

---

## ❌ **GAPS CRÍTICOS PARA O MODELO DE NEGÓCIO**

### 1. **Canais Inclusivos**

#### ❌ SMS

- **Status**: Não implementado
- **Impacto**: Alto - Classes C, D, E dependem de SMS
- **Prioridade**: ALTA

#### ⚠️ Interface Mobile-First

- **Status**: Parcial - Frontend responsivo, mas não otimizado para baixa conectividade
- **Impacto**: Médio
- **Prioridade**: MÉDIA

### 2. **Funcionalidades Core Faltantes**

#### ❌ Radar Legislativo Local

- **Status**: Não implementado
- **Descrição**: Acompanhar projetos que afetam a região do usuário
- **Impacto**: ALTO - Essencial para engajamento cívico
- **Prioridade**: ALTA

#### ❌ Resumo de Projetos

- **Status**: Não implementado
- **Descrição**: Resumir automaticamente projetos de lei em linguagem simples
- **Impacto**: ALTO - Funcionalidade principal
- **Prioridade**: ALTA

#### ❌ Retorno ao Representante

- **Status**: Não implementado
- **Descrição**: Canal para enviar feedback ao deputado/senador
- **Impacto**: MÉDIO - Importante para engajamento
- **Prioridade**: MÉDIA

### 3. **Módulo de Equidade Algorítmica**

#### ❌ Análise de Viés

- **Status**: Não implementado
- **Descrição**: Garantir que respostas não tenham viés
- **Impacto**: ALTO - Crítico para confiança
- **Prioridade**: ALTA

#### ❌ Acessibilidade

- **Status**: Parcial
- **Descrição**: Suporte a leitores de tela, alto contraste, etc.
- **Impacto**: ALTO
- **Prioridade**: ALTA

### 4. **Integração de Dados no Chat**

#### ⚠️ Busca de Legislação no Chat

- **Status**: Parcial - APIs existem, mas não estão integradas ao chat
- **Descrição**: Chat deve buscar legislação real ao responder
- **Impacto**: ALTO
- **Prioridade**: ALTA

#### ❌ Contexto Local

- **Status**: Não implementado
- **Descrição**: Personalizar respostas baseado na localização do usuário
- **Impacto**: MÉDIO
- **Prioridade**: MÉDIA

---

## 🎯 PLANO DE AÇÃO PRIORITÁRIO

### **FASE 1: FUNCIONALIDADES CORE (2-3 semanas)**

#### 1.1 Integrar Busca de Legislação no Chat

**Objetivo**: Chat deve buscar e citar legislação real ao responder

**Tarefas**:

- [ ] Criar serviço de busca unificada (LexML + Senado + Câmara)
- [ ] Integrar busca no `ChatService`
- [ ] Adicionar citações de fontes nas respostas
- [ ] Testar com perguntas reais

**Arquivos a modificar**:

- `backend/app/ai/simplification.py` - Adicionar busca de legislação
- `backend/app/services/legislation_search.py` - Novo serviço unificado
- `backend/app/api/v1/chat.py` - Incluir fontes nas respostas

#### 1.2 Resumo Automático de Projetos

**Objetivo**: Resumir projetos de lei em linguagem simples

**Tarefas**:

- [ ] Criar endpoint `/api/v1/legislation/{id}/summary`
- [ ] Implementar resumo com IA
- [ ] Adicionar áudio do resumo
- [ ] Integrar na interface

**Arquivos a criar/modificar**:

- `backend/app/api/v1/legislation.py` - Adicionar endpoint de resumo
- `backend/app/services/project_summarizer.py` - Novo serviço
- `frontend/src/components/ProjectSummary.tsx` - Novo componente

#### 1.3 Radar Legislativo Local

**Objetivo**: Acompanhar projetos que afetam a região do usuário

**Tarefas**:

- [ ] Criar endpoint `/api/v1/legislation/local`
- [ ] Integrar com Querido Diário para diários municipais
- [ ] Filtrar por localização (estado/cidade)
- [ ] Criar interface de radar

**Arquivos a criar/modificar**:

- `backend/app/api/v1/legislation.py` - Endpoint de radar local
- `backend/app/services/local_radar.py` - Novo serviço
- `frontend/src/app/radar/page.tsx` - Nova página

---

### **FASE 2: CANAIS INCLUSIVOS (2 semanas)**

#### 2.1 Integração SMS

**Objetivo**: Permitir interação via SMS

**Tarefas**:

- [ ] Escolher provedor SMS (Twilio, Zenvia, etc.)
- [ ] Criar endpoint webhook para receber SMS
- [ ] Adaptar chat para SMS (respostas curtas)
- [ ] Implementar menu SMS interativo

**Arquivos a criar**:

- `backend/app/services/sms_service.py` - Serviço SMS
- `backend/app/api/v1/sms.py` - Endpoints SMS
- `backend/app/integrations/sms_providers.py` - Integração com provedores

#### 2.2 Otimização Mobile

**Objetivo**: Interface otimizada para baixa conectividade

**Tarefas**:

- [ ] Implementar PWA (Progressive Web App)
- [ ] Adicionar modo offline
- [ ] Reduzir tamanho de assets
- [ ] Otimizar carregamento

**Arquivos a modificar**:

- `frontend/next.config.js` - Configurar PWA
- `frontend/src/app/layout.tsx` - Adicionar manifest
- `frontend/public/manifest.json` - Criar manifest

---

### **FASE 3: EQUIDADE E ACESSIBILIDADE (2 semanas)**

#### 3.1 Módulo de Equidade Algorítmica

**Objetivo**: Garantir respostas sem viés

**Tarefas**:

- [ ] Criar serviço de análise de viés
- [ ] Validar respostas antes de enviar
- [ ] Adicionar métricas de equidade
- [ ] Dashboard de monitoramento

**Arquivos a criar**:

- `backend/app/services/bias_detection.py` - Detecção de viés
- `backend/app/services/equity_monitor.py` - Monitoramento
- `backend/app/api/v1/equity.py` - Endpoints de métricas

#### 3.2 Acessibilidade

**Objetivo**: Suporte completo a acessibilidade

**Tarefas**:

- [ ] Adicionar ARIA labels
- [ ] Suporte a leitores de tela
- [ ] Modo alto contraste
- [ ] Tamanho de fonte ajustável
- [ ] Navegação por teclado

**Arquivos a modificar**:

- `frontend/src/app/globals.css` - Estilos de acessibilidade
- `frontend/src/components/AccessibilityControls.tsx` - Novo componente
- Todos os componentes - Adicionar ARIA

---

### **FASE 4: ENGAGEMENT E RETORNO (1-2 semanas)**

#### 4.1 Retorno ao Representante

**Objetivo**: Canal de comunicação com deputados/senadores

**Tarefas**:

- [ ] Criar endpoint para enviar mensagens
- [ ] Integrar com APIs de contato de parlamentares
- [ ] Template de mensagens
- [ ] Interface de envio

**Arquivos a criar**:

- `backend/app/api/v1/representative.py` - Endpoints
- `backend/app/services/representative_contact.py` - Serviço
- `frontend/src/app/contact-representative/page.tsx` - Página

#### 4.2 Melhorias no Chat

**Objetivo**: Chat mais inteligente e contextualizado

**Tarefas**:

- [ ] Melhorar prompt do sistema para linguagem mais simples
- [ ] Adicionar exemplos práticos nas respostas
- [ ] Sugestões inteligentes baseadas no contexto
- [ ] Histórico persistente

**Arquivos a modificar**:

- `backend/app/ai/simplification.py` - Melhorar prompts
- `backend/app/api/v1/chat.py` - Adicionar persistência

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Prioridade ALTA (Fase 1)

- [ ] Integrar busca de legislação no chat
- [ ] Implementar resumo automático de projetos
- [ ] Criar radar legislativo local
- [ ] Melhorar prompts para linguagem mais simples

### Prioridade MÉDIA (Fase 2-3)

- [ ] Integração SMS
- [ ] Otimização mobile/PWA
- [ ] Módulo de equidade algorítmica
- [ ] Acessibilidade completa

### Prioridade BAIXA (Fase 4)

- [ ] Retorno ao representante
- [ ] Dashboard de métricas
- [ ] Integração TSE
- [ ] Integração DataJud CNJ

---

## 🎨 MELHORIAS DE UX PARA PÚBLICO-ALVO

### Interface Simplificada

- [ ] Design mais limpo e direto
- [ ] Menos opções visíveis (progressive disclosure)
- [ ] Ícones grandes e claros
- [ ] Cores de alto contraste

### Linguagem

- [ ] Evitar jargões técnicos na interface
- [ ] Mensagens de erro mais claras
- [ ] Tutoriais em vídeo/áudio
- [ ] Exemplos práticos em cada funcionalidade

### Performance

- [ ] Carregamento rápido (< 2s)
- [ ] Funciona em conexões 3G
- [ ] Cache agressivo
- [ ] Compressão de imagens

---

## 🔗 INTEGRAÇÕES PENDENTES

### Fontes de Dados

- [ ] TSE - Dados eleitorais
- [ ] DataJud CNJ - Dados judiciários
- [ ] Base dos Dados - Usar efetivamente

### Serviços Externos

- [ ] Provedor SMS (Twilio/Zenvia)
- [ ] CDN para assets
- [ ] Analytics (privacidade-first)

---

## 📊 MÉTRICAS DE SUCESSO

### Engajamento

- Taxa de retorno de usuários
- Número de perguntas por sessão
- Tempo médio na plataforma

### Acessibilidade

- Taxa de uso de áudio vs texto
- Taxa de uso de SMS
- Taxa de conclusão de tarefas

### Impacto

- Número de projetos acompanhados
- Mensagens enviadas a representantes
- Compartilhamentos

---

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

1. **Esta semana**: Integrar busca de legislação no chat
2. **Próxima semana**: Implementar resumo automático
3. **2 semanas**: Radar legislativo local
4. **1 mês**: SMS básico funcionando

---

## 📝 NOTAS IMPORTANTES

- **Público-alvo**: Classes C, D, E - sempre pensar em simplicidade
- **Linguagem**: Sempre usar linguagem simples, evitar jargões
- **Acessibilidade**: Não é opcional, é obrigatório
- **Performance**: Otimizar para conexões lentas
- **Privacidade**: Dados sensíveis, garantir segurança

---

**Última atualização**: 2025-11-22
**Status**: Análise completa - Pronto para implementação
