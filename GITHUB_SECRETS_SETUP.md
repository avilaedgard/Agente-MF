# ⚙️ Configuração de GitHub Secrets

Siga **exatamente** estes passos para configurar o sistema de alertas por email.

## 🔐 Passo 1: Gerar Senha de App do Gmail

1. Acesse: **https://myaccount.google.com/apppasswords**
2. Você será pedido para confirmar sua identidade (2FA)
3. **Selecione aplicativo:** Email
4. **Selecione dispositivo:** Outro (nome personalizado)
5. **Digite o nome:** `GitHub Actions Monitor`
6. **Clique em Gerar**

Google vai exibir uma senha com 16 caracteres espaçados:
```
p k h m o o x t u o p v n r c p  
```

**Copie APENAS os caracteres, sem os espaços:**
```
pkhmooxtuopvnrcp
```

---

## 📝 Passo 2: Adicionar GitHub Secrets

1. Vá para seu repositório no GitHub
2. Clique em **Settings** (engrenagem no topo)
3. Na barra esquerda, clique em **Secrets and variables** → **Actions**
4. Clique em **New repository secret** (botão verde)

### Secret 1: EMAIL_SENDER
- **Name:** `EMAIL_SENDER`
- **Secret:** `edgard.1706@gmail.com`
- **→ Clique em Add secret**

### Secret 2: EMAIL_PASSWORD
- **Name:** `EMAIL_PASSWORD`
- **Secret:** `pkhmooxtuopvnrcp` (sem espaços!)
- **→ Clique em Add secret**

### Secret 3: EMAIL_RECIPIENT
- **Name:** `EMAIL_RECIPIENT`
- **Secret:** `edgard.1706@gmail.com`
- **→ Clique em Add secret**

---

## ✅ Pronto!

Agora o sistema está 100% configurado e vai:

✅ Rodar **automaticamente a cada hora** (10h-19h BRT)  
✅ Atualizar o relatório HTML  
✅ Enviar **email com alertas diários** após 19:00 BRT  

### 🌐 Acesse o Relatório Atualizado:
https://avilaedgard.github.io/Agente-MF/relatorio_monitor.html

---

## 🧪 Para Testar (Opcional)

Se quiser **testar o email imediatamente**, vá até:

1. Seu repositório no GitHub
2. **Actions** (aba no topo)
3. **Monitor - Atualizar HTML e Enviar Alertas**
4. **Run workflow** (botão ao lado)
5. Selecione **Run workflow**

Você receberá um email em segundos!

---

## ⚠️ Se Não Receber o Email

1. **Verifique** a pasta de Spam/Lixo
2. **Confirme** que os secrets foram digitados **EXATAMENTE CERTOS**
3. **Verifique** em https://myaccount.google.com/apppasswords se a senha ainda está lá
4. Se expirou, gere uma nova senha (repita Passo 1)

---

## 📋 Estrutura Final do Projeto

```
Agente-MF/
├── .github/
│   └── workflows/
│       └── monitor.yml          # ⚙️ Workflow que roda cada hora
├── data/
│   └── current-analysis.json    # 📊 Dados atualizados
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── monitor.py                   # 🚀 Script principal (simples e direto)
├── requirements.txt             # 📦 Apenas 3 dependências
└── README.md
```

Todo o resto foi **deletado** e a estrutura agora é simples, rápida e confiável! 🎉
