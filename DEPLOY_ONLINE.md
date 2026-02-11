# 🚀 GUIA DE DEPLOYMENT - VIGILANTE Online

Como colocar a aplicação VIGILANTE online e acessível de qualquer lugar, assim como o `relatorio_monitor.html` atual.

## Arquitetura de Deploy

```
┌──────────────────────────────┐
│   GitHub Pages               │
│   (seu-usuario.github.io)    │
│   Frontend: HTML/CSS/JS      │
└────────────┬─────────────────┘
             │ Faz requisições para
┌────────────┴─────────────────┐
│   Railway ou Render          │
│   Backend: Python Flask API  │
│   /api/current-analysis      │
│   /api/backtest              │
│   /api/news/<symbol>         │
└──────────────────────────────┘
```

---

## 📋 Pré-requisitos

- [x] Conta GitHub (gratuita)
- [x] Conta Railway.app OU Render.com (ambas gratuitas)
- [x] Git instalado
- [x] Código pronto em seu PC

---

## PARTE 1: Preparar Repositório Git

### 1.1 Inicializar repositório 

Abra o terminal na pasta do projeto:

```bash
cd "c:\Users\edgard.avila\OneDrive - Rede D'Or\Agente - MF"
git init
git add .
git commit -m "VIGILANTE v1.0 - Deploy"
```

### 1.2 Criar repositório no GitHub

1. Acesse https://github.com/new
2. Nome: `Agente-MF` (ou outro nome de sua preferência)
3. Descrição: "Análise Inteligente de Médias Móveis com SMA17×SMA72"
4. Escolha: **Public** (para GitHub Pages funcionar)
5. Clique em **Create repository**

### 1.3 Conectar repositório local

Após criar no GitHub, você verá um comando como:

```bash
git remote add origin https://github.com/SEU_USUARIO/Agente-MF.git
git branch -M main
git push -u origin main
```

Execute esses comandos.

---

## PARTE 2: Deploy do Backend (API)

### Opção A: Railway.app (Recomendado)

#### Passo 1: Criar conta
1. Acesse https://railway.app
2. Sign up com GitHub (mais fácil)
3. Autorize conexão

#### Passo 2: Novo projeto
1. Clique em **+ New Project**
2. Escolha **Deploy from GitHub repo**
3. Selecione seu repositório `Agente-MF`

#### Passo 3: Configurar
1. Railway detecta Python automaticamente
2. Marque a pasta `api/` como root (ou deixe na raiz)
3. Adicione variáveis de ambiente:
   - `PYTHONUNBUFFERED=1`
   - `GEMINI_API_KEY=sua_chave_aqui`
   - `ALPHA_VANTAGE_KEY=EX6OIZP8MT79GC9N`

#### Passo 4: Deploy
1. Railway faz deploy automático
2. Você verá uma URL tipo: `https://seu-app.railway.app`
3. Teste: `https://seu-app.railway.app/health`

---

### Opção B: Render.com

#### Passo 1: Criar conta
1. Acesse https://render.com
2. Sign up
3. Conecte seu GitHub

#### Passo 2: Novo Web Service
1. Dashboard > **+ New**
2. **Web Service**
3. Selecione repositório `Agente-MF`
4. Configure:
   - **Name:** `vigilante-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && pip install -r api/requirements-api.txt`
   - **Start Command:** `cd api && python app_production.py`

#### Passo 3: Variáveis de ambiente
No painel do Render, adicione:
```
GEMINI_API_KEY=sua_chave_aqui
ALPHA_VANTAGE_KEY=EX6OIZP8MT79GC9N
```

#### Passo 4: Deploy
1. Clique em **Create Web Service**
2. Aguarde ~5 minutos
3. Você terá uma URL tipo: `https://vigilante-api.onrender.com`

---

## PARTE 3: Deploy do Frontend (GitHub Pages)

### Passo 1: Habilitar GitHub Pages

1. Acesse seu repositório no GitHub
2. Vá em **Settings**
3. Clique em **Pages** (no menu esquerdo)
4. Em "Build and deployment", escolha:
   - **Source:** GitHub Actions
5. GitHub criará um workflow automático

### Passo 2: Configurar API Endpoint

O frontend precisa saber para qual API fazer requisições.

**Opção A: Adicionar no HTML (mais simples)**

Edite `frontend/index.html` e adicione antes de `<script src="script.js">`:

```html
<script>
    window.API_ENDPOINT = 'https://seu-app.railway.app/api';
    // Ou se usar Render:
    // window.API_ENDPOINT = 'https://vigilante-api.onrender.com/api';
</script>
```

**Opção B: Arquivo de config (mais profissional)**

Crie `frontend/config.js`:

```javascript
window.API_CONFIG = {
    production: 'https://seu-app.railway.app/api',
    development: 'http://localhost:5000/api'
};

window.API_ENDPOINT = window.API_CONFIG.production;
```

E adicione em `index.html` antes de `script.js`:

```html
<script src="config.js"></script>
```

### Passo 3: Estrutura para GitHub Pages

GitHub Pages serve arquivos da raiz do repositório ou da pasta `/docs`.

**Opção 1: Arquivos na raiz**

Mova os arquivos do frontend para raiz:

```bash
# Copiar arquivos para raiz
cp frontend/index.html ./
cp frontend/style.css ./
cp frontend/script.js ./

# Deletar pasta frontend (ou manter ambos)
```

**Opção 2: Servir da pasta frontend**

1. Em GitHub **Settings > Pages**
2. Source: GitHub Actions
3. Crie arquivo `.github/workflows/static.yml`:

```yaml
name: Deploy Frontend

on:
  push:
    branches: ["main"]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Pages
        uses: actions/configure-pages@v3
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: 'frontend/'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

### Passo 4: Push alterações

```bash
git add .
git commit -m "Configure API endpoint and GitHub Pages"
git push origin main
```

GitHub Pages fará deploy automático em ~2 minutos.

---

## PARTE 4: Testar Tudo Online

### 1. Verificar se API está online

```bash
curl https://seu-app.railway.app/health
# Ou
curl https://vigilante-api.onrender.com/health
```

Deve retornar:
```json
{"status": "ok", "timestamp": "..."}
```

### 2. Acessar o Frontend

GitHub Pages estará em:
```
https://seu-usuario.github.io/Agente-MF
```

Ou se habilitou custom domain:
```
https://vigilante.seudominio.com
```

### 3. Testar funcionalidades

- ✅ Aba "Análise Atual" carrega em ~2s
- ✅ Aba "Backtest" inicia (primeira vez leva ~10 min)
- ✅ Aba "Notícias" mostra links
- ✅ Logs aparecem no console (F12)

---

## 🔄 Atualizações Automáticas

Após setup inicial, as atualizações são automáticas:

### Frontend
```bash
# Editar arquivos em frontend/
# Fazer push
git add frontend/
git commit -m "Update frontend"
git push origin main

# GitHub Pages atualiza automaticamente em ~2 min
```

### Backend
```bash
# Editar arquivos do backend
# Fazer push
git add api/
git commit -m "Update API"
git push origin main

# Railway/Render atualiza automaticamente em ~2 min
```

---

## 📊 Monitoramento

### Railway Dashboard
- https://railway.app/dashboard
- Ver logs em tempo real
- Monitorar CPU/RAM/Rede

### Render Dashboard
- https://dashboard.render.com
- Ver logs de deployment
- Status do serviço

### GitHub Pages
- https://github.com/seu-usuario/Agente-MF/actions
- Ver workflows de deploy
- Status de cada build

---

## 🔒 Segurança em Produção

### Antes de colocar online, configure:

1. **Variáveis de ambiente** (Railway/Render):
   - ✅ Nunca commitar `.env` com chaves reais
   - ✅ Usar secrets do Railway/Render

2. **CORS no Backend**:
   - ✅ Configurado para aceitar qualquer requisição (desenvolvimento)
   - ⚠️ Em produção, adicionar origem específica:

```python
CORS(app, resources={r"/api/*": {
    "origins": ["https://seu-usuario.github.io"]
}})
```

3. **Rate limiting** (opcional):

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/current-analysis')
@limiter.limit("10 per minute")
def api_analise_atual():
    ...
```

---

## 🆘 Troubleshooting

### "API não responde"

```bash
# Verificar status da API
curl -v https://seu-app.railway.app/health

# Ver logs no Railway/Render
# Dashboard > Logs tab
```

### "Frontend não carrega dados"

1. Abra F12 (developer tools)
2. Vá em **Console**
3. Procure mensagens de erro
4. Verifique se `window.API_ENDPOINT` está correto:

```javascript
// No console, execute:
console.log(window.API_ENDPOINT)
```

### "CORS error"

Isso significa o frontend não consegue acessar a API.

Solução rápida no `api/app.py`:

```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

Solução segura:
```python
CORS(app, resources={r"/api/*": {
    "origins": [
        "https://seu-usuario.github.io",
        "http://localhost:5000"
    ]
}})
```

---

## 📱 Acessar de Qualquer Lugar

Após setup, você pode acessar de:

✅ **PC em casa:** https://seu-usuario.github.io/Agente-MF  
✅ **Celular:** https://seu-usuario.github.io/Agente-MF  
✅ **Tablet:** https://seu-usuario.github.io/Agente-MF  
✅ **Qualquer dispositivo com internet**

Funciona 100% como esperado, 24/7.

---

## 💰 Custos

### Opção A: Railway
- Plano gratuito: $5/mês de crédito
- 1 API Flask pequena cabe facilmente
- Se exceder, aviso antes de cobrar

### Opção B: Render
- Plano gratuito: até 750 horas/mês
- API Python funciona no free tier
- Hiberna após 15 min sem uso (pode acordar em 30s)

### GitHub Pages
- **GRATUITO** para repos públicos
- Ilimitado

**Custo total = $0 - $5/mês**

---

## ✨ Exemplo Final

Seu projeto ficará assim:

```
https://seu-usuario.github.io/Agente-MF/
├─ Análise Atual (carrega em 2s)
├─ Backtest (15 anos)
└─ Notícias

(Conectado a Railway em background)
├─ https://seu-app.railway.app/api/current-analysis
├─ https://seu-app.railway.app/api/backtest
└─ https://seu-app.railway.app/api/news/<symbol>
```

Pode compartilhar a URL com qualquer pessoa!

---

## 🎯 Checklist Final

- [ ] Repositório criado no GitHub
- [ ] Código feito push (git push origin main)
- [ ] Railway/Render conectado
- [ ] API endpoint definido no `script.js`
- [ ] GitHub Pages habilitado
- [ ] Teste `/health` da API
- [ ] Teste acesso pelo GitHub Pages
- [ ] Funcionalidades funcionando

---

**Você está online! 🚀**

Qualquer dúvida durante o processo, é só avisar!
