# 📊 VIGILANTE - Análise Inteligente de Médias Móveis

Uma aplicação profissional para monitorar e analisar estratégias de trading baseadas em cruzamento de médias móveis (SMA17 × SMA72) com interface moderna estilo app financeiro.

## 🎯 Funcionalidades

### 1. **Análise Atual** 📈
- Relatório em tempo real de todas as carteiras
- Sinais de compra/venda com base em cruzamentos SMA17 × SMA72
- Cards interativos com dados de preço, mínimo/máximo de 5 anos
- Alertas de cruzamentos nos últimos 14 dias
- Análise com IA (Gemini) dos sinais detectados

### 2. **Backtest Histórico** 📊
- Análise de 15 anos de dados históricos
- Estratégia: Compra no cruzamento SMA17 acima de SMA72, nunca vende
- Estatísticas detalhadas por ativo:
  - Total de entradas
  - Taxa de acerto
  - Rentabilidade media
  - Comparação com buy & hold
- Execução automática 1x por semana (domingo 03:00 BRT)
- Opção para forçar execução via API

### 3. **Notícias em Tempo Real** 📰
- Feed de notícias dos ativos relevantes
- Priorização por recência e importância de movimentos
- Links diretos para Google News

## 🏗️ Arquitetura

### Backend (Python)
```
api/
├── app.py                 # API Flask com 3 endpoints principais
├── backtest_engine.py     # Engine de backtest (15 anos)
└── requirements-api.txt   # Dependências adicionais
```

### Frontend (JavaScript/HTML/CSS)
```
frontend/
├── index.html             # SPA com 3 abas
├── style.css              # Design navy blue dark
└── script.js              # Lógica do frontend (vanilla JS)
```

## 🚀 Como Rodar

### 1. **Instalar Dependências**

```bash
# Instalar dependências da API
pip install -r api/requirements-api.txt

# Ou instalar tudo junto
pip install flask flask-cors apscheduler python-dotenv
```

### 2. **Configurar Variáveis de Ambiente**

Crie um arquivo `.env` na raiz do projeto:

```env
# APIs
ALPHA_VANTAGE_KEY=EX6OIZP8MT79GC9N
GEMINI_API_KEY=sua_chave_gemini_aqui

# Email (opcional)
EMAIL_SENDER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_app

# Debug
TEST_EMAIL=0
RUN_ONCE=0
```

### 3. **Iniciar o Servidor**

```bash
# Rodar API Flask
cd api
python app.py

# Abrirá em http://localhost:5000
```

### 4. **Acessar a Aplicação**

Abra seu navegador em:
```
http://localhost:5000
```

## 📡 API REST

### GET `/api/current-analysis`
Retorna análise atual de todas as carteiras com sinais recentes.

**Exemplo:**
```json
{
  "timestamp": "2026-02-11T18:30:00",
  "carteiras": {
    "Carteira Ações": [
      {
        "ativo": "ITSA4.SA",
        "preco": 8.45,
        "sinal": "COMPRA",
        "sma17": 8.50,
        "sma72": 8.20,
        "distancia": 0.30
      }
    ]
  },
  "sinais_recentes": [...]
}
```

### GET `/api/backtest`
Retorna resultados do backtest (cached, atualiza 1x/semana).

**Status:** 
- `200` - Backtest pronto
- `202` - Backtest em processamento
- Resposta inclui estatísticas completas por ativo

### POST `/api/backtest/forcar`
Força execução imediata do backtest.

**Resposta:**
```json
{
  "status": "iniciado",
  "mensagem": "Backtest iniciado. Pode levar alguns minutos..."
}
```

### GET `/api/news/<symbol>`
Retorna links de notícias de um ativo específico.

## 🎨 Design

### Tema: Navy Blue Dark
- **Cores principais:**
  - Navy Dark: `#0f1419`
  - Accent Blue: `#0d7fb7`
  - Accent Cyan: `#00d9ff`
  - Accent Green: `#10b981`
  - Accent Red: `#ef4444`

- **Componentes:**
  - Header sticky com logo e status
  - 3 abas navegáveis (Análise, Backtest, Notícias)
  - Cards responsivos em grid
  - Animações suaves
  - Design mobile-first

## ⚙️ Scheduler

O backtest é executado automaticamente:
- **Frequência:** Toda semana
- **Dia:** Domingo
- **Horário:** 03:00 BRT
- **Timezone:** America/Sao_Paulo

Para modificar, edite em `api/app.py` na função `agendar_backtest()`:

```python
scheduler.add_job(
    executar_backtest_async,
    trigger='cron',
    day_of_week='sun',  # Domingo
    hour=3,             # 03:00
    minute=0,
    id='backtest_semanal'
)
```

## 📊 Estratégia de Trading Testada

### Regras Simples, Poderosas
1. **Entrada:** SMA17 cruza acima de SMA72 = COMPRA
2. **Saída:** Nunca vende no cruzamento para baixo = HOLD
3. **Holding:** Mantém a posição até o final do período (15 anos)

### Métricas Calculadas
- **Taxa de Acerto:** % de operações positivas
- **ROI Estratégia:** Rentabilidade total de todas as operações
- **Retorno Médio/Op:** Average return per trade
- **Maior Ganho/Perda:** Extremos registrados
- **Comparação Buy & Hold:** Retorno se tivesse comprado e segurando

## 🔄 Fluxo de Atualização

```
Monitor.py (roda todos os dias 18:30)
    ↓
Gera relatório HTML (relatorio_monitor.html)
    ↓
API Flask (http://localhost:5000)
    ├─ /api/current-analysis → Dados atuais
    ├─ /api/backtest → Histórico (cache semanal)
    ├─ /api/news/<symbol> → Notícias
    └─ Frontend SPA → Exibe dados
```

## 🛠️ Desenvolvimento

### Modo Debug
Abra o console do navegador e use:

```javascript
// Ver dados carregados
window.DEBUG.currentData()

// Forçar recarregar análise
window.DEBUG.forceAnalise()

// Forçar backtest
window.DEBUG.forceBacktest()

// Forçar notícias
window.DEBUG.forceNoticias()
```

### Logs
- **Backend:** Console do servidor Flask
- **Frontend:** Console do navegador (F12)

## 📋 Carteiras Monitoradas

### Carteira Ações
- ITSA4.SA, NEOE3.SA, BBDC4.SA, LREN3.SA, RDOR3.SA
- GOAU4.SA, KLBN4.SA, EGIE3.SA, RECV3.SA, JHSF3.SA

### Carteira ETF
- IVVB11.SA, GOLD11.SA, DIVO11.SA, HASH11.SA

### Watchlist
- VALE3.SA, PETR3.SA, BTC-USD, GOLD, SILVER

### Especulação
- CEAB3.SA, S1BS34.SA

*(Editar em `monitor.py` para modificar)*

## ⚠️ Disclaimer

**Este é um modelo educacional de análise.**

- Não é recomendação de investimento
- Sempre consulte profissionais antes de investir
- Histórico não garante resultados futuros
- Use por sua conta e risco

## 📝 Licença

MIT License - Sinta-se livre para usar e modificar!

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas! 

---

**Desenvolvido com ❤️ para análise inteligente de mercado**
