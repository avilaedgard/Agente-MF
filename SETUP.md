# 🚀 GUIA DE SETUP - VIGILANTE

Passo a passo completo para configurar e rodar a aplicação profissional de análise de médias móveis.

## 📋 Pré-requisitos

- **Python 3.8+** instalado (recomendado 3.11+)
- **pip** (gerenciador de pacotes)
- Navegador moderno (Chrome, Firefox, Edge, Safari)
- Conexão com internet

## 🔧 Instalação

### Passo 1: Instalar Dependências

Abra o terminal/prompt na pasta do projeto e execute:

```bash
(Windows)
pip install -r requirements.txt

(Linux/Mac)
pip3 install -r requirements.txt
```

Ou, para instalar apenas as dependências da API:

```bash
pip install flask flask-cors apscheduler python-dotenv
```

### Passo 2: Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edite o arquivo `.env` com suas chaves:

```env
# Essencial para análise
ALPHA_VANTAGE_KEY=EX6OIZP8MT79GC9N  # (já configurado)
GEMINI_API_KEY=sua_chave_aqui        # Obter em: https://ai.google.dev

# Opcional: para receber alertas por email
EMAIL_SENDER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_app         # Usar "Senha de app" do Gmail
EMAIL_RECIPIENT=email_destino@gmail.com
```

**Como gerar Gemini API Key:**
1. Acesse https://ai.google.dev
2. Clique em "Get API Key"
3. Crie uma nova chave e copie
4. Cole em `GEMINI_API_KEY=`

**Como gerar Senha de App Gmail:**
1. Ative 2-step verification em sua conta Google
2. Acesse https://myaccount.google.com/apppasswords
3. Copie a senha gerada
4. Cole em `EMAIL_PASSWORD=`

## ▶️ Como Executar

### Opção 1: Scripts Automáticos (Recomendado)

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
bash start.sh
```

### Opção 2: Manual

**Terminal 1 - Executar Monitor Tradicional (Opcional):**
```bash
python monitor.py
```

**Terminal 2 - Executar API Flask:**
```bash
cd api
python app.py
```

**Resultado esperado:**
```
Running on http://localhost:5000
Press CTRL+C to quit
```

### Opção 3: Teste Rápido (Sem loop)

```bash
RUN_ONCE=1 python monitor.py
```

## 🌐 Acessando a Aplicação

Abra seu navegador e acesse:

```
http://localhost:5000
```

Você verá a interface com 3 abas:
- 📈 **Análise Atual** - Dados em tempo real
- 📊 **Backtest (15 anos)** - Histórico completo
- 📰 **Notícias** - Feed de notícias dos ativos

## 📊 Primeira Execução

Na primeira vez que rodar, o sistema irá:

1. **Carregar dados** de todos os ativos (1-2 minutos)
2. **Gerar análise atual** com sinais e alertas
3. **Executar backtest de 15 anos** (5-10 minutos dependendo do hardware)
4. **Exibir interface** profissional no navegador

Aguarde até que todas as seções apareçam.

## 🔄 Scheduler Automático

O backtest é configurado para rodar automaticamente:

**Quando:** Todo domingo às 03:00 (BRT)
**Duração:** Geralmente 5-10 minutos
**Local:** Sem interferência, roda em background

Para modificar o horário, edite `api/app.py`:

```python
scheduler.add_job(
    executar_backtest_async,
    trigger='cron',
    day_of_week='sun',  # 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
    hour=3,             # Horário (0-23)
    minute=0,           # Minuto
    id='backtest_semanal'
)
```

## 🖥️ Estrutura de Pastas

```
Agente - MF/
├── monitor.py              # Script original de monitoramento
├── main.py                 # (vazio, não usado)
├── teste_mercado.py        # Scripts de teste
├── requirements.txt        # Dependências Python
├── .env.example           # Template de configuração
├── .env                   # Configuração (não tracked)
├── index.html             # Redirecionador (legado)
├── relatorio_monitor.html # Relatório HTML (gerado)
│
├── api/                   # Pasta da API Backend
│   ├── app.py            # API Flask (3 endpoints + scheduler)
│   ├── backtest_engine.py # Engine de backtest (15 anos)
│   └── requirements-api.txt
│
├── frontend/             # Pasta do Frontend SPA
│   ├── index.html        # Página principal (3 abas)
│   ├── style.css         # Estilos navy blue dark
│   └── script.js         # Lógica JavaScript vanilla
│
├── API_README.md         # Documentação completa da API
├── SETUP.md              # Este arquivo
├── start.bat             # Script de inicialização (Windows)
└── start.sh              # Script de inicialização (Linux/Mac)
```

## 🧪 Testando Components

### Teste 1: Verify API Status

```bash
curl http://localhost:5000/api/current-analysis
```

Deve retornar JSON com dados atuais.

### Teste 2: Forçar Backtest (Imediato)

```bash
curl -X POST http://localhost:5000/api/backtest/forcar
```

Retorna: `{"status": "iniciado", "mensagem": "..."}`

### Teste 3: Verificar Notícias

```bash
curl http://localhost:5000/api/news/ITSA4.SA
```

Deve retornar links de notícias.

### Teste 4: Debug no Console

Abra **F12** no navegador e no console execute:

```javascript
// Ver todos os dados carregados
window.DEBUG.currentData()

// Forçar recarregar análise
window.DEBUG.forceAnalise()

// Forçar backtest
window.DEBUG.forceBacktest()

// Forçar notícias
window.DEBUG.forceNoticias()
```

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"

**Solução:** Instale as dependências:
```bash
pip install -r requirements.txt -r api/requirements-api.txt
```

### Erro: Port 5000 já está em uso

**Solução:** Mate o processo anterior:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Backtest Muito Lento

**Normal!** A primeira execução pode levar 10+ minutos pois:
- Baixa 15 anos de dados para 20+ ativos
- Calcula médias móveis para cada dia
- Simula operações e computa estatísticas

Cache é usado após a primeira execução.

### Notícias não aparecem

- Verifique conexão com internet
- Google News API pode estar rate-limited
- Tente novamente em alguns minutos

### Análise Gemini vazia

- Verifique se `GEMINI_API_KEY` está correto em `.env`
- Verifique se a quota diária não foi excedida
- Sistema tem fallback para análise padrão (sem IA)

## 📱 Acessando de Outro Computador

Se quiser acessar a aplicação de outro PC na rede:

```bash
# No seu PC (servidor)
cd api
python app.py

# Em outro PC (cliente)
http://seu-ip-aqui:5000
# Exemplo: http://192.168.1.100:5000
```

Descubra seu IP:
```bash
# Windows
ipconfig

# Linux/Mac
ifconfig
```

## 🔐 Segurança

**IMPORTANTE:** Este setup é para **desenvolvimento/pesquisa local**.

Para produção:
- Use variáveis de ambiente reais (não .env)
- Configure HTTPS
- Use autenticação/autorização
- Implemente rate-limiting
- Use um WSGI server (gunicorn, waitress)
- Configure CORS corretamente

## 📚 Documentação Completa

Leia `API_README.md` para:
- Descrição detalhada dos endpoints
- Estrutura de resposta JSON
- Configuração do scheduler
- Estratégia de trading explicada
- Disclaimer legal

## 🆘 Suporte & Dúvidas

1. Verifique os logs no console
2. Consulte `API_README.md`
3. Ative modo debug (`window.DEBUG.*` no console)
4. Verifique variáveis de ambiente

## ✨ Próximas Melhorias (Sugestões)

- [ ] WebSocket para updates em tempo real
- [ ] Banco de dados para histórico de sinais
- [ ] Alertas por Telegram/Discord
- [ ] UI de configuração dinâmica
- [ ] Múltiplas estratégias (P&L, BB, RSI, etc)
- [ ] Backtesting parallelizado com multiprocessing
- [ ] Exportar relatórios em PDF/Excel
- [ ] API de webhook para integração

---

**Versão:** 1.0  
**Última atualização:** Fevereiro 2026  
**Desenvolvido com ❤️ para análise inteligente**
