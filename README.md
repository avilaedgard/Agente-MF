# 📊 VIGILANTE - Monitor de Médias Móveis

**Sistema automatizado para monitoramento de cruzamentos SMA17 × SMA72** com atualização horária e alertas diários por email.

## ⚡ Como Funciona

### 🔄 Ciclo Automático (GitHub Actions)

1. **Executa a cada hora** (10h-19h BRT) automaticamente
2. **Busca dados** dos ativos via Yahoo Finance
3. **Calcula SMA17 e SMA72** para cada ativo
4. **Gera HTML** com relatório visual atualizado
5. **Detecta cruzamentos** nos últimos 14 dias
6. **Envia email** diariamente após 19:00 BRT (se houver sinais)

### 📍 Relatório Online

🌐 **Acesse aqui**: https://avilaedgard.github.io/Agente-MF/relatorio_monitor.html

*Atualizado automaticamente a cada hora*

## 📊 Carteiras Monitoradas

| Carteira | Ativos |
|----------|--------|
| **Ações** | ITSA4.SA, BBSE3.SA, ODPV3.SA, BBDC4.SA, LREN3.SA, RDOR3.SA, GOAU4.SA, KLBN4.SA, EGIE3.SA, RECV3.SA, JHSF3.SA |
| **ETFs** | IVVB11.SA, GOLD11.SA, DIVO11.SA, HASH11.SA |
| **Watchlist** | VALE3.SA, PETR3.SA, BTC-USD |
| **Especulação** | CEAB3.SA, S1BS34.SA |

## ⚙️ Configuração Necessária

### 1️⃣ Gerar Senha de App do Gmail

1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione: **Email** e **Outro (smartphone)**
3. Digite: `GitHub Actions Monitor`
4. Copie a senha (16 caracteres)

### 2️⃣ Adicionar GitHub Secrets

No seu repositório → **Settings** → **Secrets and variables** → **Actions** → **New secret**

| Nome | Valor |
|------|-------|
| `EMAIL_SENDER` | seu.email@gmail.com |
| `EMAIL_PASSWORD` | pkhmooxtuopvnrcp |
| `EMAIL_RECIPIENT` | edgard.1706@gmail.com |

> ✅ **Pronto!** O sistema já comçará a rodar automaticamente.

## 🧪 Testar Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar análise uma vez
python monitor.py
```

## 📧 O que Você Recebe

- **Assunto**: `[ALERTA] Cruzamentos de Médias - 20/02/2026 19:15`
- **Conteúdo**: Tabela com todos os cruzamentos detectados nos últimos 14 dias
- **Link**: Acesso direto ao relatório completo

## 🔧 Personalização

Edite `monitor.py` para:
- Adicionar/remover ativos
- Mudar períodos de análise
- Alterar horários de envio de email

## 📝 Estrutura de Arquivos

```
.
├── monitor.py              # Script principal (atualizado a cada hora)
├── requirements.txt        # Dependências Python
├── relatorio_monitor.html  # Relatório gerado (atualizado)
└── data/
    └── current-analysis.json  # Dados em JSON

O workflow GitHub Actions está configurado para executar:

- **Horários**: 10h, 11h, 12h, 13h, 14h, 15h, 16h, 17h, 18h, 19h BRT
- **Envio de Email**: Apenas na execução das 19h ou posterior
- **Configuração**: Veja o arquivo [`.github/workflows/monitor.yml`](.github/workflows/monitor.yml) para detalhes do agendamento

> **Nota**: Se modificar os horários no README, lembre-se de atualizar também o arquivo de workflow.

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
