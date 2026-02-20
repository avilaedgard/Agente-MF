#!/usr/bin/env python3
"""
Vigilante - Monitor de Médias Móveis (SMA17 × SMA72)
Atualiza relatório HTML a cada hora e envia alertas por email diariamente.
"""

import os
import sys
import json
import time
import smtplib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import yfinance as yf
    import pandas as pd
except ImportError as e:
    print(f"❌ Erro ao importar dependências: {e}")
    print("Instale com: pip install yfinance pandas requests")
    sys.exit(1)

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

# Fuso horário do Brasil (BRT = GMT-3)
BRT = timezone(timedelta(hours=-3))

# Carteiras para monitorar
CARTEIRAS = {
    "Carteira Ações": ["ITSA4.SA", "NEOE3.SA", "BBDC4.SA", "LREN3.SA", "RDOR3.SA", "GOAU4.SA", "KLBN4.SA", "EGIE3.SA", "RECV3.SA", "JHSF3.SA"],
    "Carteira ETF": ["IVVB11.SA", "GOLD11.SA", "DIVO11.SA", "HASH11.SA"],
    "Watchlist": ["VALE3.SA", "PETR3.SA", "BTC-USD"],
    "Especulação": ["CEAB3.SA", "S1BS34.SA"]
}

# Email (com fallback para valores padrão vazios)
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "").strip()
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "").strip()
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "").strip()
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Caminhos
CAMINHO_HTML = "relatorio_monitor.html"
CAMINHO_DATA = "data/current-analysis.json"

# Debug: mostrar status de configuração
if os.getenv("DEBUG") == "1":
    print(f"[DEBUG] EMAIL_SENDER configurado: {'✅' if EMAIL_SENDER else '❌'}")
    print(f"[DEBUG] EMAIL_PASSWORD configurado: {'✅' if EMAIL_PASSWORD else '❌'}")
    print(f"[DEBUG] EMAIL_RECIPIENT configurado: {'✅' if EMAIL_RECIPIENT else '❌'}")

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def agora_brt():
    """Retorna datetime atual em BRT (Brasília)"""
    return datetime.now(BRT)

def buscar_dados(ticker, periodo="5y"):
    """Busca dados históricos de um ativo via Yahoo Finance"""
    try:
        df = yf.download(ticker, period=periodo, interval="1d", progress=False)
        if df is not None and len(df) > 0:
            return df
    except Exception as e:
        print(f"  ⚠️  Erro ao buscar {ticker}: {str(e)}")
    return None

def calcular_medias(df):
    """Calcula SMA17 e SMA72"""
    if df is None or len(df) < 72:
        return None
    
    df = df.copy()
    df['SMA17'] = df['Close'].rolling(window=17).mean()
    df['SMA72'] = df['Close'].rolling(window=72).mean()
    
    return df

def detectar_cruzamentos(df, ativo, carteira):
    """Detecta cruzamentos de SMA17 × SMA72 nos últimos 14 dias"""
    if df is None or len(df) < 2:
        return []
    
    sinais = []
    data_limite = agora_brt().date() - timedelta(days=14)
    
    # Iterar pelos últimos dias
    for i in range(len(df) - 1, 1, -1):
        data_candle = df.index[i].date()
        
        if data_candle < data_limite:
            break
        
        sma17_anterior = df['SMA17'].iloc[i - 1]
        sma72_anterior = df['SMA72'].iloc[i - 1]
        sma17_atual = df['SMA17'].iloc[i]
        sma72_atual = df['SMA72'].iloc[i]
        
        # Validar dados
        if pd.isna([sma17_anterior, sma72_anterior, sma17_atual, sma72_atual]).any():
            continue
        
        preco = float(df['Close'].iloc[i])
        
        # Cruzamento de COMPRA (SMA17 cruza acima de SMA72)
        if sma17_anterior <= sma72_anterior and sma17_atual > sma72_atual:
            sinais.append({
                "Carteira": carteira,
                "Ativo": ativo,
                "Sinal": "🟢 COMPRA",
                "Preco": round(preco, 2),
                "Data": data_candle.strftime('%d/%m/%Y'),
                "SMA17": round(float(sma17_atual), 2),
                "SMA72": round(float(sma72_atual), 2),
            })
        
        # Cruzamento de VENDA (SMA17 cruza abaixo de SMA72)
        elif sma17_anterior >= sma72_anterior and sma17_atual < sma72_atual:
            sinais.append({
                "Carteira": carteira,
                "Ativo": ativo,
                "Sinal": "🔴 VENDA",
                "Preco": round(preco, 2),
                "Data": data_candle.strftime('%d/%m/%Y'),
                "SMA17": round(float(sma17_atual), 2),
                "SMA72": round(float(sma72_atual), 2),
            })
    
    return sinais

def enviar_email_alerta(sinais_finais):
    """Envia alerta por email com os cruzamentos detectados"""
    
    if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECIPIENT:
        print("  ⚠️  Credenciais de email não configuradas!")
        return False
    
    if not sinais_finais:
        print("  ℹ️  Nenhum sinal para enviar por email")
        return False
    
    try:
        # Preparar email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = f"🔔 [ALERTA] Cruzamentos de Médias - {agora_brt().strftime('%d/%m/%Y %H:%M')}"
        
        # Montar tabela de sinais
        corpo_html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 8px; max-width: 800px; margin: 0 auto; }
                h2 { color: #333; border-bottom: 3px solid #0366d6; padding-bottom: 10px; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th { background: #0366d6; color: white; padding: 12px; text-align: left; }
                td { padding: 10px; border-bottom: 1px solid #ddd; }
                tr:hover { background: #f9f9f9; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }
                .link { color: #0366d6; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🔔 Relatório de Cruzamentos de Médias Móveis</h2>
                <p><strong>Data/Hora:</strong> {DATA_HORA}</p>
                <p><strong>Sinais detectados nos últimos 14 dias:</strong> {TOTAL}</p>
                
                <table>
                    <tr>
                        <th>Ativo</th>
                        <th>Carteira</th>
                        <th>Sinal</th>
                        <th>Preço</th>
                        <th>Data</th>
                        <th>SMA17</th>
                        <th>SMA72</th>
                    </tr>
        """
        
        corpo_html = corpo_html.replace("{DATA_HORA}", agora_brt().strftime('%d/%m/%Y %H:%M:%S'))
        corpo_html = corpo_html.replace("{TOTAL}", str(len(sinais_finais)))
        
        for item in sinais_finais:
            corpo_html += f"""
                    <tr>
                        <td><strong>{item['Ativo']}</strong></td>
                        <td>{item['Carteira']}</td>
                        <td><strong>{item['Sinal']}</strong></td>
                        <td>R$ {item['Preco']}</td>
                        <td>{item['Data']}</td>
                        <td>{item['SMA17']}</td>
                        <td>{item['SMA72']}</td>
                    </tr>
            """
        
        corpo_html += """
                </table>
                
                <div class="footer">
                    <p>📊 <a href="https://avilaedgard.github.io/Agente-MF/relatorio_monitor.html" class="link">Ver relatório completo</a></p>
                    <p>Este é um email automático do sistema <strong>Vigilante</strong>.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(corpo_html, 'html'))
        
        # Enviar email
        try:
            print(f"  📧 Conectando ao SMTP ({SMTP_SERVER}:{SMTP_PORT})...")
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                print(f"  🔐 Iniciando TLS...")
                server.starttls()
                print(f"  👤 Fazendo login como {EMAIL_SENDER}...")
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                print(f"  📤 Enviando mensagem...")
                server.send_message(msg)
                print(f"  ✅ Email enviado com sucesso para {EMAIL_RECIPIENT}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"  ❌ ERRO DE AUTENTICAÇÃO: Verifique EMAIL_SENDER e EMAIL_PASSWORD")
            print(f"     Erro: {str(e)}")
            return False
        except smtplib.SMTPException as e:
            print(f"  ❌ ERRO DE SMTP: {str(e)}")
            return False
        except Exception as e:
            print(f"  ❌ ERRO ao enviar email: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

# ============================================================================
# GERAÇÃO DE HTML
# ============================================================================

def gerar_html(relatorios_por_carteira):
    """Gera HTML com o relatório de médias móveis"""
    
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vigilante - Monitor de Médias Móveis</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 50px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 32px;
            margin-bottom: 5px;
        }
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        .timestamp {
            display: block;
            font-size: 12px;
            margin-top: 10px;
            opacity: 0.8;
        }
        .content {
            padding: 40px;
        }
        .carteira-section {
            margin-bottom: 40px;
        }
        .carteira-title {
            font-size: 20px;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th {
            background: #f5f5f5;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #ddd;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        tr:hover {
            background: #f9f9f9;
        }
        .compra {
            background: #d4edda;
            color: #155724;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
        }
        .venda {
            background: #f8d7da;
            color: #721c24;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
        }
        .neutro {
            background: #e2e3e5;
            color: #383d41;
            padding: 6px 12px;
            border-radius: 4px;
        }
        .footer {
            background: #f5f5f5;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card strong {
            font-size: 24px;
            display: block;
            margin-top: 10px;
        }
        @media (max-width: 768px) {
            .header { padding: 20px; }
            .header h1 { font-size: 24px; }
            .content { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 VIGILANTE</h1>
            <p>Monitor de Cruzamentos de Médias Móveis (SMA17 × SMA72)</p>
            <span class="timestamp">Atualizado em {TIMESTAMP}</span>
        </div>
        
        <div class="content">
            <div class="stats">
                <div class="stat-card">
                    <div>Total de Carteiras</div>
                    <strong>{TOTAL_CARTEIRAS}</strong>
                </div>
                <div class="stat-card">
                    <div>Total de Ativos</div>
                    <strong>{TOTAL_ATIVOS}</strong>
                </div>
                <div class="stat-card">
                    <div>Sinais COMPRA</div>
                    <strong>{TOTAL_COMPRA}</strong>
                </div>
                <div class="stat-card">
                    <div>Sinais VENDA</div>
                    <strong>{TOTAL_VENDA}</strong>
                </div>
            </div>
    """
    
    # Calcular estatísticas
    total_carteiras = len(relatorios_por_carteira)
    total_ativos = sum(len(df) if not df.empty else 0 for df in relatorios_por_carteira.values())
    total_compra = 0
    total_venda = 0
    
    # Gerar tabelas por carteira
    for carteira, df in relatorios_por_carteira.items():
        if df.empty:
            continue
        
        html += f'<div class="carteira-section">'
        html += f'<h2 class="carteira-title">{carteira}</h2>'
        html += '<table>'
        html += '<tr>'
        html += '<th>Ativo</th>'
        html += '<th>Abertura</th>'
        html += '<th>Fechamento</th>'
        html += '<th>Sinal</th>'
        html += '<th>SMA17</th>'
        html += '<th>SMA72</th>'
        html += '<th>Mínimo (5y)</th>'
        html += '<th>Máximo (5y)</th>'
        html += '</tr>'
        
        for _, row in df.iterrows():
            sinal = row['Sinal']
            sinal_class = 'compra' if 'COMPRA' in str(sinal) else ('venda' if 'VENDA' in str(sinal) else 'neutro')
            
            if 'COMPRA' in str(sinal):
                total_compra += 1
            elif 'VENDA' in str(sinal):
                total_venda += 1
            
            html += f'<tr>'
            html += f'<td><strong>{row["Ativo"]}</strong></td>'
            html += f'<td>R$ {row["Abertura"]:.2f}</td>'
            html += f'<td>R$ {row["Fechamento"]:.2f}</td>'
            html += f'<td><span class="{sinal_class}">{sinal}</span></td>'
            html += f'<td>{row["SMA17"]:.2f}</td>'
            html += f'<td>{row["SMA72"]:.2f}</td>'
            html += f'<td>R$ {row["Minimo (5y)"]:.2f}</td>'
            html += f'<td>R$ {row["Maximo (5y)"]:.2f}</td>'
            html += f'</tr>'
        
        html += '</table>'
        html += '</div>'
    
    html += '</div>'
    html += f'<div class="footer">'
    html += f'<p>Atualizado em {agora_brt().strftime("%d/%m/%Y às %H:%M:%S")} BRT</p>'
    html += f'<p>🤖 Sistema automatizado • Próxima atualização em aproximadamente 1 hora</p>'
    html += f'</div>'
    html += '</body>'
    html += '</html>'
    
    # Substituir placeholders
    html = html.replace("{TIMESTAMP}", agora_brt().strftime("%d/%m/%Y às %H:%M:%S BRT"))
    html = html.replace("{TOTAL_CARTEIRAS}", str(total_carteiras))
    html = html.replace("{TOTAL_ATIVOS}", str(total_ativos))
    html = html.replace("{TOTAL_COMPRA}", str(total_compra))
    html = html.replace("{TOTAL_VENDA}", str(total_venda))
    
    return html

# ============================================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================================

def processar_analise():
    """Executa a análise completa de uma vez"""
    
    print(f"\n{'='*60}")
    print(f"  🚀 INICIANDO ANÁLISE - {agora_brt().strftime('%d/%m/%Y %H:%M:%S BRT')}")
    print(f"{'='*60}\n")
    
    relatorios_por_carteira = {}
    sinais_finais = []
    
    # Processar cada carteira
    for carteira, ativos in CARTEIRAS.items():
        print(f"📂 Carteira: {carteira}")
        relatorios_por_carteira[carteira] = []
        
        for ativo in ativos:
            # Buscar dados
            df = buscar_dados(ativo)
            if df is None:
                print(f"  ❌ {ativo}: Dados não disponíveis")
                continue
            
            # Calcular médias
            df = calcular_medias(df)
            if df is None:
                print(f"  ❌ {ativo}: Não há dados suficientes")
                continue
            
            # Extrair últimos valores
            ultimo_fechamento = float(df['Close'].iloc[-1])
            primeira_abertura = float(df['Open'].iloc[-1])
            sma17_ultima = float(df['SMA17'].iloc[-1])
            sma72_ultima = float(df['SMA72'].iloc[-1])
            minimo_5y = float(df['Close'].min())
            maximo_5y = float(df['Close'].max())
            
            # Determinar sinal atual
            if sma17_ultima > sma72_ultima:
                sinal = "🟢 COMPRA"
            elif sma17_ultima < sma72_ultima:
                sinal = "🔴 VENDA"
            else:
                sinal = "⚪ Neutro"
            
            # Adicionar ao relatório
            relatorios_por_carteira[carteira].append({
                "Ativo": ativo,
                "Abertura": primeira_abertura,
                "Fechamento": ultimo_fechamento,
                "Sinal": sinal,
                "SMA17": sma17_ultima,
                "SMA72": sma72_ultima,
                "Minimo (5y)": minimo_5y,
                "Maximo (5y)": maximo_5y,
            })
            
            # Detectar cruzamentos
            cruzamentos = detectar_cruzamentos(df, ativo, carteira)
            sinais_finais.extend(cruzamentos)
            
            print(f"  ✅ {ativo}: {sinal}")
        
        # Converter para DataFrame
        if relatorios_por_carteira[carteira]:
            relatorios_por_carteira[carteira] = pd.DataFrame(relatorios_por_carteira[carteira])
        else:
            relatorios_por_carteira[carteira] = pd.DataFrame()
    
    # Gerar HTML
    print("\n📝 Gerando HTML...")
    html = gerar_html(relatorios_por_carteira)
    with open(CAMINHO_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ HTML atualizado: {CAMINHO_HTML}")
    
    # Salvar dados em JSON
    print("💾 Salvando dados...")
    os.makedirs("data", exist_ok=True)
    data_para_salvar = {
        "timestamp": agora_brt().isoformat(),
        "sinais": sinais_finais,
        "relatorios": {k: v.to_dict('records') for k, v in relatorios_por_carteira.items()}
    }
    with open(CAMINHO_DATA, "w", encoding="utf-8") as f:
        json.dump(data_para_salvar, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Dados salvos: {CAMINHO_DATA}")
    
    # Alertas
    if sinais_finais:
        print(f"\n🔔 CRUZAMENTOS DETECTADOS: {len(sinais_finais)}")
        for sinal in sinais_finais:
            print(f"  {sinal['Ativo']} ({sinal['Carteira']}): {sinal['Sinal']} em {sinal['Data']}")
        
        # Enviar email se for após 19:00 BRT
        agora = agora_brt()
        test_mode = os.getenv("TEST_EMAIL") == "1"
        
        if test_mode or agora.hour >= 19:
            print("\n📧 Enviando email de alerta...")
            enviar_email_alerta(sinais_finais)
        else:
            print(f"\n⏰ Email será enviado após 19:00 BRT (atual: {agora.strftime('%H:%M')})")
    else:
        print("\n✅ Nenhum cruzamento detectado nos últimos 14 dias")
    
    print(f"\n{'='*60}")
    print(f"  ✅ ANÁLISE CONCLUÍDA")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    processar_analise()
