# 🔑 Como Configurar as Chaves de API

## Opção 1: Groq (GRATUITO - Recomendado) ⭐

1. **Obter chave do Groq:**

   - Acesse: https://console.groq.com/keys
   - Crie uma conta gratuita
   - Clique em "Create API Key"
   - Copie a chave (começa com `gsk_...`)

2. **Adicionar no arquivo `.env`:**
   ```bash
   cd backend
   # Abra o arquivo .env e adicione:
   GROQ_API_KEY=gsk_sua-chave-aqui
   ```

## Opção 2: OpenAI

1. **Obter chave da OpenAI:**

   - Acesse: https://platform.openai.com/api-keys
   - Faça login ou crie uma conta
   - Clique em "Create new secret key"
   - Copie a chave (começa com `sk-...`)

2. **Adicionar no arquivo `.env`:**
   ```bash
   OPENAI_API_KEY=sk-sua-chave-aqui
   ```

## ⚠️ Importante

- **Prioridade de uso:** OpenAI > Groq
- Configure pelo menos UMA das chaves acima
- Após adicionar a chave, **reinicie o servidor backend**
- O arquivo `.env` está no diretório `backend/`

## 🔄 Reiniciar o Servidor

Após configurar a chave, reinicie o servidor:

```bash
cd backend
# Se estiver usando ambiente virtual:
.venv\Scripts\Activate.ps1
# Reinicie o servidor:
python -m uvicorn app.main:app --reload
```

## ✅ Verificar se Funcionou

1. O servidor deve mostrar no log:
   - `Modelo OpenAI GPT-4o-mini inicializado` (se usar OpenAI)
   - `Modelo Groq (Llama 3.1 8B Instant) inicializado` (se usar Groq)
2. Teste no chat do frontend - o erro de autenticação deve desaparecer

## 📝 Modelos Disponíveis no Groq

O sistema usa automaticamente o modelo `llama-3.1-8b-instant` que é:

- ✅ Gratuito
- ✅ Rápido
- ✅ Atualizado (não descontinuado)

Outros modelos disponíveis no Groq (se quiser alterar no código):

- `llama-3.1-8b-instant` (padrão - recomendado)
- `mixtral-8x7b-32768`
- `gemma-7b-it`
