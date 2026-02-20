#!/usr/bin/env python3
"""
Script de teste para diagnosticar problemas com secrets e email
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

print("=" * 60)
print("🔍 TESTE DE CONFIGURAÇÃO - VIGILANTE")
print("=" * 60)

# Verificar secrets
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "").strip()
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "").strip()
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "").strip()

print("\n📋 SECRETS CONFIGURADOS:")
print(f"  EMAIL_SENDER: {'✅ Sim' if EMAIL_SENDER else '❌ NÃO CONFIGURADO'} ({EMAIL_SENDER[:20]}***)")
print(f"  EMAIL_PASSWORD: {'✅ Sim' if EMAIL_PASSWORD else '❌ NÃO CONFIGURADO'} (***)")
print(f"  EMAIL_RECIPIENT: {'✅ Sim' if EMAIL_RECIPIENT else '❌ NÃO CONFIGURADO'} ({EMAIL_RECIPIENT})")

if not (EMAIL_SENDER and EMAIL_PASSWORD and EMAIL_RECIPIENT):
    print("\n❌ Faltam secrets! Configure em: Settings → Secrets and variables → Actions")
    exit(1)

# Testar conexão SMTP
print("\n📧 TESTANDO CONEXÃO SMTP:")
try:
    print("  Conectando a smtp.gmail.com:587...")
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    print("  ✅ Conexão bem-sucedida")
    
    print("  Iniciando TLS...")
    server.starttls()
    print("  ✅ TLS ativado")
    
    print(f"  Fazendo login como {EMAIL_SENDER}...")
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    print("  ✅ Login bem-sucedido!")
    
    server.quit()
    
    print("\n🎉 TUDO OK! Os secrets estão configurados corretamente.")
    print("\n✅ Próximo passo: Execute o workflow real no GitHub Actions")
    
except smtplib.SMTPAuthenticationError:
    print("  ❌ ERRO DE AUTENTICAÇÃO!")
    print("  • EMAIL_SENDER ou EMAIL_PASSWORD está INCORRETO")
    print("  • Verifique se a senha tem 16 caracteres (sem espaços)")
    print("  • Verifique em: https://myaccount.google.com/apppasswords")
except smtplib.SMTPException as e:
    print(f"  ❌ ERRO DE SMTP: {str(e)}")
except Exception as e:
    print(f"  ❌ ERRO: {str(e)}")
    exit(1)
