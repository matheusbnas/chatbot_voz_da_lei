# 🚀 Deploy Frontend no Vercel + Backend no Servidor

Este guia mostra como fazer deploy do **frontend no Vercel** enquanto o **backend fica no seu servidor** (Coolify).

## ✅ Vantagens

- **Frontend no Vercel**: Deploy automático, CDN global, SSL gratuito, muito rápido
- **Backend no seu servidor**: Controle total, banco de dados local, sem custos extras
- **Funciona perfeitamente**: Frontend e backend se comunicam via HTTP/HTTPS

---

## 📋 Pré-requisitos

1. ✅ Backend rodando no seu servidor (Coolify) e acessível via URL pública
2. ✅ Conta no [Vercel](https://vercel.com) (grátis)
3. ✅ Repositório no GitHub

---

## 🔧 Passo 1: Configurar CORS no Backend

O backend precisa aceitar requisições do domínio do Vercel.

### Opção A: Permitir qualquer origem (desenvolvimento/teste)

No Coolify, adicione esta variável de ambiente no backend:

```bash
CORS_ORIGINS=["*"]
```

### Opção B: Permitir apenas o domínio do Vercel (recomendado para produção)

1. Faça deploy do frontend no Vercel primeiro (para obter a URL)
2. No Coolify, adicione a variável de ambiente:

```bash
CORS_ORIGINS=["https://seu-app.vercel.app","https://www.seu-dominio.com"]
```

**Nota**: O backend já está configurado para ler `CORS_ORIGINS` do arquivo `.env` ou variáveis de ambiente.

---

## 🎨 Passo 2: Deploy do Frontend no Vercel

### 2.1. Conectar Repositório

1. Acesse [vercel.com](https://vercel.com)
2. Clique em **"Add New Project"**
3. Conecte seu repositório GitHub: `matheusbnas/chatbot_voz_da_lei`
4. Selecione o repositório

### 2.2. Configurar Projeto

**⚠️ IMPORTANTE**: Configure o **Root Directory** no painel do Vercel!

1. No painel do Vercel, vá em **Settings** → **General**
2. Role até **Root Directory**
3. Digite: `frontend`
4. Clique em **Save**

**Configurações do Build (serão aplicadas automaticamente após configurar Root Directory):**

- **Framework Preset**: `Next.js` (detectado automaticamente)
- **Root Directory**: `frontend` ⚠️ **CONFIGURE NO PAINEL!**
- **Build Command**: `npm run build` (padrão)
- **Output Directory**: `.next` (padrão)
- **Install Command**: `npm install` (padrão)

**💡 Dica**: O arquivo `vercel.json` na raiz tem comandos que fazem `cd frontend`, mas a melhor forma é configurar o **Root Directory** no painel do Vercel. Isso faz o Vercel executar todos os comandos dentro de `frontend/` automaticamente.

**🔧 Se o build falhar com erro de CSS/Webpack:**

1. **Limpe o cache do Vercel:**
   - Vá em **Settings** → **General**
   - Role até **Build & Development Settings**
   - Clique em **Clear Build Cache**
   - Confirme a ação

2. **Verifique se o Root Directory está configurado:**
   - Deve estar como `frontend` (não `/frontend` ou `./frontend`)

3. **Faça um novo deploy:**
   - Vá em **Deployments**
   - Clique nos 3 pontos do último deploy
   - Selecione **Redeploy**
   - Marque **"Use existing Build Cache"** como **desmarcado**

### 2.3. Variáveis de Ambiente

Adicione estas variáveis de ambiente no Vercel:

| Nome                  | Valor              | Exemplo                                              |
| --------------------- | ------------------ | ---------------------------------------------------- |
| `NEXT_PUBLIC_API_URL` | URL do seu backend | `https://api.seudominio.com` ou `http://seu-ip:3001` |

**Como adicionar:**

1. Na página de configuração do projeto, role até **"Environment Variables"**
2. Clique em **"Add"**
3. Adicione:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: URL completa do seu backend (ex: `https://backend.seudominio.com` ou `http://192.168.1.100:3001`)
   - **Environments**: Marque todas (Production, Preview, Development)

**⚠️ IMPORTANTE:**

- Use `http://` se o backend não tiver SSL
- Use `https://` se o backend tiver SSL
- Não inclua `/api/v1` na URL (o frontend já adiciona isso)

### 2.4. Deploy

1. Clique em **"Deploy"**
2. Aguarde o build (2-3 minutos)
3. ✅ Pronto! Seu frontend estará no ar

---

## 🔗 Passo 3: Verificar Conexão

### 3.1. Testar no Navegador

1. Acesse a URL do Vercel (ex: `https://seu-app.vercel.app`)
2. Abra o **Console do Navegador** (F12)
3. Tente usar uma funcionalidade (ex: fazer uma pergunta no chat)
4. Verifique se não há erros de CORS

### 3.2. Verificar Logs

**No Vercel:**

- Vá em **"Deployments"** → Clique no último deploy → **"Functions"** → Veja os logs

**No Backend (Coolify):**

- Veja os logs do container do backend
- Deve aparecer requisições chegando do domínio do Vercel

---

## 🐛 Troubleshooting

### Erro: "CORS policy: No 'Access-Control-Allow-Origin'"

**Solução:**

1. Verifique se `CORS_ORIGINS` no backend inclui a URL do Vercel
2. Reinicie o container do backend no Coolify
3. Verifique se a URL está correta (com `https://` se aplicável)

### Erro: "Network Error" ou "Backend não está disponível"

**Solução:**

1. Verifique se `NEXT_PUBLIC_API_URL` está configurada corretamente no Vercel
2. Teste se o backend está acessível: abra `http://seu-backend:3001/health` no navegador
3. Verifique se o firewall permite conexões do Vercel

### Frontend não encontra o backend

**Solução:**

1. Verifique se a variável `NEXT_PUBLIC_API_URL` está configurada no Vercel
2. O prefixo `NEXT_PUBLIC_` é obrigatório para variáveis acessíveis no browser
3. Faça um novo deploy após adicionar a variável

### Build falha no Vercel

**Solução:**

1. Verifique se o **Root Directory** está configurado como `frontend`
2. Verifique se `package.json` está em `frontend/package.json`
3. Veja os logs de build no Vercel para mais detalhes

---

## 🔄 Atualizações Automáticas

### Frontend (Vercel)

- ✅ Deploy automático a cada push no `main`
- ✅ Preview deployments para cada PR

### Backend (Coolify)

- Configure webhook do GitHub no Coolify para deploy automático
- Ou faça deploy manual quando necessário

---

## 📝 Checklist Final

- [ ] Backend rodando e acessível publicamente
- [ ] CORS configurado no backend para aceitar o domínio do Vercel
- [ ] Frontend deployado no Vercel
- [ ] Variável `NEXT_PUBLIC_API_URL` configurada no Vercel
- [ ] Testado no navegador e funcionando
- [ ] Sem erros de CORS no console

---

## 🎯 Exemplo de Configuração Completa

### Backend (Coolify)

```
URL: https://api.seudominio.com
Porta interna: 8080
Porta externa: 3001
CORS_ORIGINS: ["https://seu-app.vercel.app"]
```

### Frontend (Vercel)

```
URL: https://seu-app.vercel.app
NEXT_PUBLIC_API_URL: https://api.seudominio.com
Root Directory: frontend
```

---

## 💡 Dicas

1. **Domínio Customizado**: Configure um domínio no Vercel para ficar mais profissional
2. **SSL**: Se o backend não tiver SSL, o navegador pode bloquear requisições. Considere usar um proxy reverso (Nginx) com SSL
3. **Monitoramento**: Use os logs do Vercel e Coolify para monitorar erros
4. **Performance**: O Vercel já otimiza automaticamente (CDN, cache, etc.)

---

## ✅ Resultado

Agora você tem:

- ✅ Frontend super rápido no Vercel (CDN global)
- ✅ Backend no seu servidor (controle total)
- ✅ Tudo funcionando perfeitamente conectado! 🚀
