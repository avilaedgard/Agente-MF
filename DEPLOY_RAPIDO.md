# 🚀 QUICK START - Deploy Online em 10 Minutos

Coloque sua aplicação VIGILANTE online e acessível de qualquer lugar.

## Dois componentes a deploiar:

1. **Backend (Python API)** → Railway.app ou Render.com
2. **Frontend (HTML/CSS/JS)** → GitHub Pages (grátis!)

---

## ✅ Passo 1: GitHub Repository (2 min)

```bash
# No seu projeto, faça:
cd "c:\Users\edgard.avila\OneDrive - Rede D'Or\Agente - MF"
git init
git add .
git commit -m "VIGILANTE v1.0"
```

Crie novo repo em https://github.com/new
- Nome: `Agente-MF`
- Visibilidade: **Public** (importante!)
- Clique em **Create**

```bash
# Conecte seu repo local:
git remote add origin https://github.com/SEU_USUARIO/Agente-MF.git
git branch -M main
git push -u origin main
```

✅ **Seu código está no GitHub!**

---

## ✅ Passo 2: Deploy Backend (3 min)

### Opção A: Railway (Recomendado)

1. Acesse https://railway.app
2. Sign up com GitHub
3. Clique em **+ New Project**
4. **Deploy from GitHub repo**
5. Selecione seu repositório `Agente-MF`
6. Railway configura automaticamente
7. Aguarde deploy (2-3 min)

**Você recebe uma URL assim:** `https://seu-app.railway.app`

Teste em seu navegador:
```
https://seu-app.railway.app/health
```

Copie a URL base (sem `/health`).

### Opção B: Render.com

1. Acesse https://render.com
2. Sign up + conecte GitHub
3. **+ New**  > **Web Service**
4. Escolha seu repositório
5. Configure:
   - Name: `vigilante-api`
   - Environment: `Python 3`
   - Build: `pip install -r requirements.txt && pip install -r api/requirements-api.txt`
   - Start: `cd api && python app_production.py`
6. Deploy

**Você recebe uma URL assim:** `https://vigilante-api.onrender.com`

---

## ✅ Passo 3: Configurar Frontend (2 min)

Abra `frontend/config.js` e substituir a URL:

```javascript
// Linha 13 - Alterar de:
apiBase: 'https://seu-app.railway.app/api',

// Para sua URL real:
apiBase: 'https://seu-app.railway.app/api',  // Railway
// OU
apiBase: 'https://vigilante-api.onrender.com/api',  // Render
```

Salve o arquivo.

---

## ✅ Passo 4: Fazer Push (2 min)

```bash
git add frontend/config.js
git commit -m "Configure API endpoint for production"
git push origin main
```

---

## ✅ Passo 5: Habilitar GitHub Pages (1 min)

1. Seu repositório no GitHub
2. **Settings** (aba)
3. **Pages** (menu esquerdo)
4. Source: **GitHub Actions**

GitHub Pages estará em:
```
https://seu-usuario.github.io/Agente-MF
```

---

## ✅ Pronto! Teste

1. Acesse: `https://seu-usuario.github.io/Agente-MF`
2. Aguarde carregar (primeira vez ~10s)
3. Verifique se os dados aparecem:
   - ✅ Aba "Análise Atual" = dados em tempo real
   - ✅ Aba "Backtest" = inicia (leva 10 min primeira vez)
   - ✅ Aba "Notícias" = links de notícias

---

## 🔄 Próximas Atualizações

Qualquer mudança que você make:

```bash
# Editar arquivo
# Fazer push
git add .
git commit -m "Description of changes"
git push origin main

# Em 2-3 minutos, mudanças aparecem online
```

---

## 📱 Acessar de Qualquer Lugar

```
https://seu-usuario.github.io/Agente-MF
```

✅ No PC  
✅ No celular  
✅ No tablet  
✅ Em qualquer dispositivo com internet

---

## 💰 Costo Total

- Railway: **$5/mês** (ou grátis com crédito inicial de $5)
- Render: **GRÁTIS** (com algumas limitações)
- GitHub Pages: **GRÁTIS**

**Total: $0 - $5/mês**

---

## 🆘 Problemas Comuns

**"Nada carrega"**
- Verifique se API_URL está correta em `config.js`
- Se API está online: `https://seu-app.railway.app/health`
- Abra F12 no navegador e veja console para erros

**"API error"**
- Railway/Render podem levar 30s para acordar (free tier)
- Aguarde 30s e tente novamente

**"CORS error"**
- Significa frontend não consegue acessar API
- Verifique se `config.js` tem a URL correta
- Verifique CORS em `api/app.py`

---

## 📚 Documentação Completa

Leia `DEPLOY_ONLINE.md` para mais detalhes, troubleshooting e configurações avançadas.

---

**Você está online!** 🎉

Acesse de qualquer lugar usando: `https://seu-usuario.github.io/Agente-MF`
