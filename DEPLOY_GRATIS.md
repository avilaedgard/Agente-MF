# 🎉 DEPLOY 100% GRÁTIS - Somente GitHub

Aqui estão **3 formas de fazer tudo grátis** usando apenas GitHub.

---

## 🏆 OPÇÃO 1: GitHub Actions + GitHub Pages (RECOMENDADO)

O backend roda como **automação no GitHub Actions** a cada dia, gerando arquivos JSON que o frontend consome.

### Vantagens:
✅ **100% gratuito** (GitHub Actions = 2000 min/mês grátis)  
✅ Sem servidor externo  
✅ Tudo no GitHub  
✅ Sem custo aparente  

### Desvantagens
⚠️ Backtest só roda 1x/dia (não real-time)  
⚠️ Atualização de análise leva ~5 min  
⚠️ Não há "pull" de dados, só "push"

### Setup (20 minutos)

#### Passo 1: Estrutura de pastas

```
.github/
  workflows/
    daily-analysis.yml    # Roda análise 1x/dia
    weekly-backtest.yml   # Roda backtest 1x/semana

data/
  current-analysis.json   # Gerado pelo workflow
  backtest.json          # Gerado pelo workflow
  
frontend/
  index.html
  config.js              # Aponta para files no repo
  script.js
  style.css
```

#### Passo 2: Criar workflows

Crie `.github/workflows/daily-analysis.yml`:

```yaml
name: Daily Analysis Update

on:
  schedule:
    # A cada dia às 18:30 BRT (21:30 UTC)
    - cron: '30 21 * * *'
  
  # Também executar manualmente via GitHub UI
  workflow_dispatch:

jobs:
  analyze:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r api/requirements-api.txt
      
      - name: Run analysis
        run: |
          python -c "
          import sys
          sys.path.insert(0, '.')
          from monitor import agora_brt, CARTEIRAS, fetch_data
          import json
          import pandas as pd
          from datetime import timedelta, timezone
          
          BRT = timezone(timedelta(hours=-3))
          
          relatorio = {
              'timestamp': agora_brt().isoformat(),
              'carteiras': {}
          }
          
          sinais = []
          
          for carteira, ativos in CARTEIRAS.items():
              relatorio['carteiras'][carteira] = []
              for ativo in ativos:
                  try:
                      df = fetch_data(ativo)
                      if df is None or len(df) < 72:
                          continue
                      
                      df['SMA17'] = df['Close'].rolling(window=17).mean()
                      df['SMA72'] = df['Close'].rolling(window=72).mean()
                      
                      sma17 = float(df['SMA17'].iloc[-1])
                      sma72 = float(df['SMA72'].iloc[-1])
                      preco = float(df['Close'].iloc[-1])
                      abertura = float(df['Open'].iloc[-1])
                      minimo = float(df['Low'].min())
                      maximo = float(df['High'].max())
                      
                      if sma17 > sma72:
                          sinal = 'COMPRA'
                      elif sma17 < sma72:
                          sinal = 'VENDA'
                      else:
                          sinal = 'NEUTRO'
                      
                      df['Cruzamento'] = (df['SMA17'] > df['SMA72']).astype(int).diff()
                      cruzamentos = df[df['Cruzamento'] != 0]
                      
                      if len(cruzamentos) > 0:
                          ultima_data_cruzamento = cruzamentos.index[-1].strftime('%d/%m/%Y')
                      else:
                          ultima_data_cruzamento = 'Sem dados'
                      
                      item = {
                          'ativo': ativo,
                          'preco': round(preco, 2),
                          'abertura': round(abertura, 2),
                          'sinal': sinal,
                          'sma17': round(sma17, 2),
                          'sma72': round(sma72, 2),
                          'distancia': round(abs(sma17 - sma72), 2),
                          'ultimo_cruzamento': ultima_data_cruzamento,
                          'minimo_5y': round(minimo, 2),
                          'maximo_5y': round(maximo, 2)
                      }
                      
                      relatorio['carteiras'][carteira].append(item)
                  except Exception as e:
                      print(f'Erro {ativo}: {e}')
          
          with open('data/current-analysis.json', 'w') as f:
              json.dump(relatorio, f, indent=2, ensure_ascii=False)
          "
      
      - name: Commit and push
        run: |
          git config --local user.email 'action@github.com'
          git config --local user.name 'GitHub Action'
          git add data/current-analysis.json
          git commit -m 'Update analysis - $(date)' || exit 0
          git push
```

Crie `.github/workflows/weekly-backtest.yml`:

```yaml
name: Weekly Backtest

on:
  schedule:
    # A cada domingo às 03:00 BRT (06:00 UTC)
    - cron: '0 6 * * 0'
  
  workflow_dispatch:

jobs:
  backtest:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r api/requirements-api.txt
      
      - name: Run backtest
        run: |
          python -c "
          import sys
          sys.path.insert(0, '.')
          from api.backtest_engine import executar_backtest
          import json
          
          resultado = executar_backtest(anos=15)
          
          with open('data/backtest.json', 'w') as f:
              json.dump(resultado, f, indent=2, ensure_ascii=False)
          "
      
      - name: Commit and push
        run: |
          git config --local user.email 'action@github.com'
          git config --local user.name 'GitHub Action'
          git add data/backtest.json
          git commit -m 'Update backtest - $(date)' || exit 0
          git push
```

#### Passo 3: Atualizar frontend para ler JSONs

Edite `frontend/config.js`:

```javascript
// Configuração para ler dados do repositório GitHub
window.APP_CONFIG = {
    // URL base dos dados (raw GitHub)
    dataBase: 'https://raw.githubusercontent.com/SEU_USUARIO/Agente-MF/main/data/',
    
    // URLs específicas
    urls: {
        currentAnalysis: 'https://raw.githubusercontent.com/SEU_USUARIO/Agente-MF/main/data/current-analysis.json',
        backtest: 'https://raw.githubusercontent.com/SEU_USUARIO/Agente-MF/main/data/backtest.json'
    },
    
    debug: window.location.hostname === 'localhost'
};

// Cache local (para não fazer requisição a cada 5 min)
window.DATA_CACHE = {
    expiresIn: 5 * 60 * 1000  // 5 minutos
};
```

#### Passo 4: Atualizar script.js

```javascript
// Substituir função de fetch
async function loadAnaliseAtual() {
    const statusIndicator = document.getElementById('statusIndicator');
    
    try {
        statusIndicator.textContent = '● Carregando...';
        statusIndicator.classList.remove('offline');
        
        // Usar GitHub raw content em vez de API
        const response = await fetch(window.APP_CONFIG.urls.currentAnalysis);
        const data = await response.json();
        
        currentData.analiseAtual = data;
        renderAnaliseAtual(data);
        
        statusIndicator.textContent = '● Conectado';
        statusIndicator.classList.remove('offline');
    } catch (error) {
        console.error('Erro ao carregar análise:', error);
        statusIndicator.textContent = '● Desconectado';
        statusIndicator.classList.add('offline');
    }
}

async function loadBacktest() {
    const container = document.getElementById('backtestResultsContainer');
    const statusContainer = document.getElementById('backtestStatusContainer');
    
    statusContainer.style.display = 'block';
    container.style.display = 'none';
    
    try {
        const response = await fetch(window.APP_CONFIG.urls.backtest);
        const data = await response.json();
        
        currentData.backtest = data;
        renderBacktest(data);
        
        statusContainer.style.display = 'none';
        container.style.display = 'block';
        
    } catch (error) {
        console.error('Erro ao carregar backtest:', error);
        statusContainer.style.display = 'none';
        container.innerHTML = `Backtest ainda não foi rodado. Aguarde próxima execução automática no GitHub Actions (dom 03:00 BRT)`;
    }
}
```

#### Passo 5: Push para GitHub

```bash
mkdir -p .github/workflows data
# Copiar os arquivos yml acima para .github/workflows/

git add .github/ data/ frontend/
git commit -m "Setup GitHub Actions for free deployment"
git push origin main
```

---

## 🚀 OPÇÃO 2: Vercel (MAIS SIMPLES)

**Vercel é 100% grátis** para Python e pode hospedar tanto backend quanto frontend.

### Setup (5 minutos)

1. Acesse https://vercel.com
2. Sign up com GitHub
3. Import seu repositório `Agente-MF`
4. Vercel configura automaticamente
5. Deploy em 2 minutos

**Result:** Uma URL grátis como `https://agente-mf.vercel.app`

**Vantagem:** Simples, sem configuração, funciona igual à solução com Railway.

---

## 📱 OPÇÃO 3: Render.com Tier Grátis

**Render oferece tier grátis** (hibernates após 15 min sem uso):

1. https://render.com
2. New > Web Service
3. Seu repositório
4. Deploy automático

**Limitação:** Acordar leva 30 segundos.

---

## 🏆 RECOMENDAÇÃO FINAL

| Opção | Custo | Setup | Tempo Real | Recomendo |
|-------|-------|-------|-----------|-----------|
| GitHub Actions + Pages | 🆓 | 20 min | ❌ (1x/dia) | ✅ If OK atualizar 1x/dia |
| Vercel | 🆓 | 5 min | ✅ (real-time) | ✅✅✅ SIMPLES |
| Render | 🆓 | 10 min | ✅ (real-time) | ✅ Alternativa |

**Minha sugestão:** **VERCEL** = 5 minutos, grátis, sem configuração, tempo real.

---

## 🎯 Quer que eu implemente?

Qual você quer?

1. **GitHub Actions** (mais controle, aprende automação)
2. **Vercel** (mais simples)
3. **Render Grátis** (alternativa)

Dizia e faço o setup pronto! 🚀
