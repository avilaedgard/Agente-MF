# Agente de Monitoramento de Médias Móveis

Sistema automatizado para monitoramento de cruzamentos de médias móveis (SMA17 x SMA72) em ações, ETFs e commodities.

## 🚀 Funcionalidades

- **Monitoramento Automático**: Execução automática a cada hora (10h-19h BRT) via GitHub Actions
- **Relatório HTML**: Geração de relatório visual com gráficos interativos
- **Alertas por Email**: Notificações automáticas quando detecta cruzamentos de médias
- **Análise com IA**: Integração com Google Gemini para análise dos sinais

## 📊 Carteiras Monitoradas

- **Carteira Ações**: ITSA4.SA, NEOE3.SA, BBDC4.SA, LREN3.SA, RDOR3.SA, GOAU4.SA, KLBN4.SA, EGIE3.SA, RECV3.SA, JHSF3.SA
- **Carteira ETF**: IVVB11.SA, GOLD11.SA, DIVO11.SA, HASH11.SA
- **Watchlist**: VALE3.SA, PETR3.SA, BTC-USD, GOLD, SILVER
- **Especulação**: CEAB3.SA, S1BS34.SA

## ⚙️ Configuração de Alertas por Email

Para receber alertas por email quando houver cruzamentos de médias, você precisa configurar os **GitHub Secrets**:

### Passo 1: Gerar Senha de App do Gmail

1. Acesse sua conta do Google
2. Vá em: https://myaccount.google.com/apppasswords
3. Ative a **verificação em 2 etapas** se ainda não estiver ativa
4. Gere uma nova **senha de app**:
   - Selecione "App": **Email**
   - Selecione "Dispositivo": **Outro (nome personalizado)**
   - Digite: **GitHub Actions Monitor**
5. Copie a senha gerada (16 caracteres sem espaços)

### Passo 2: Configurar Secrets no GitHub

1. Acesse seu repositório no GitHub
2. Vá em: **Settings** → **Secrets and variables** → **Actions**
3. Clique em **New repository secret**
4. Adicione os seguintes secrets:

| Nome | Descrição | Exemplo |
|------|-----------|---------|
| `EMAIL_SENDER` | Seu email do Gmail | `seu.email@gmail.com` |
| `EMAIL_PASSWORD` | Senha de app gerada no passo 1 | `abcd efgh ijkl mnop` |
| `EMAIL_RECIPIENT` | Email que receberá os alertas | `seu.email@gmail.com` |

### Passo 3: Configurar Gemini AI (Opcional)

Para análise inteligente dos sinais com IA:

1. Obtenha uma chave API do Google Gemini: https://makersuite.google.com/app/apikey
2. Adicione o secret:

| Nome | Descrição |
|------|-----------|
| `GEMINI_API_KEY` | Chave API do Google Gemini |

## 🔍 Como Funciona

1. **Coleta de Dados**: Busca dados históricos de 5 anos via Yahoo Finance
2. **Cálculo de Médias**: Calcula SMA17 e SMA72 para cada ativo
3. **Detecção de Cruzamentos**: Identifica cruzamentos nos últimos 14 dias
4. **Análise com IA**: Gemini analisa os sinais detectados (se configurado)
5. **Notificação**: Envia email com os alertas após 19h BRT
6. **Relatório**: Atualiza o HTML disponível em: https://avilaedgard.github.io/Agente-MF/relatorio_monitor.html

## 📧 Exemplo de Email de Alerta

Quando detectado um cruzamento, você receberá um email com:

- **Tabela de Sinais**: Ativo, carteira, tipo de sinal (COMPRA/VENDA), preço e data
- **Análise IA**: Interpretação dos sinais pelo Gemini
- **Link**: Acesso direto ao relatório completo

## 🛠️ Desenvolvimento Local

### Requisitos

```bash
pip install -r requirements.txt
```

### Executar Localmente

```bash
# Configurar variáveis de ambiente (opcional)
export EMAIL_SENDER="seu.email@gmail.com"
export EMAIL_PASSWORD="sua-senha-de-app"
export EMAIL_RECIPIENT="destinatario@gmail.com"
export GEMINI_API_KEY="sua-chave-gemini"

# Executar uma vez
RUN_ONCE=1 python monitor.py

# Ou executar em loop (verifica a cada 30s)
python monitor.py
```

## 🔄 Agendamento Automático

O workflow GitHub Actions está configurado para executar:

- **Horários**: 10h, 11h, 12h, 13h, 14h, 15h, 16h, 17h, 18h, 19h BRT
- **Envio de Email**: Apenas na execução das 19h ou posterior

## 📝 Logs e Debugging

Para verificar se os emails estão sendo enviados:

1. Acesse: **Actions** → **Atualizar HTML do Monitor**
2. Clique na execução mais recente
3. Abra o job **gerar-html**
4. Procure por:
   - `[EMAIL] Alerta enviado com sucesso` ✅
   - `[ERRO] Falha ao enviar email` ❌
   - `[AVISO] Usando credenciais padrão` ⚠️

## 🐛 Solução de Problemas

### Erro: "Username and Password not accepted"

**Causa**: Secrets não configurados ou senha incorreta

**Solução**:
1. Verifique se os secrets estão configurados no GitHub
2. Use uma **senha de app** do Gmail, não sua senha normal
3. Certifique-se de que a verificação em 2 etapas está ativa

### Email não chega

**Causa**: Email pode estar na caixa de spam ou secrets não configurados

**Solução**:
1. Verifique a pasta de spam
2. Adicione o remetente aos contatos confiáveis
3. Verifique os logs do GitHub Actions para mensagens de erro

## 📄 Licença

Este projeto é de uso pessoal.
