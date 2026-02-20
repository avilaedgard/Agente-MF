#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VIGILANTE - Monitor Extremamente Simples
Apenas busca dados, calcula SMA17/SMA72 e gera HTML
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    import yfinance as yf
    import pandas as pd
except:
    print("[ERRO] Instale: pip install yfinance pandas")
    sys.exit(1)

# Configurações
BRT = timezone(timedelta(hours=-3))
CARTEIRAS = {
    "Ações": ["ITSA4.SA", "NEOE3.SA", "BBDC4.SA", "LREN3.SA", "RDOR3.SA"],
    "ETF": ["IVVB11.SA", "GOLD11.SA"],
    "Outros": ["VALE3.SA", "PETR3.SA", "BTC-USD"]
}

def agora():
    return datetime.now(BRT)

def buscar_e_processar():
    """Busca dados e gera relatorio"""
    print("[INFO] Iniciando - " + agora().strftime('%d/%m/%Y %H:%M:%S BRT'))
    
    relatorio = {"timestamp": agora().isoformat(), "carteiras": {}}
    
    for carteira, ativos in CARTEIRAS.items():
        print("[CARTEIRA] " + carteira)
        relatorio["carteiras"][carteira] = []
        
        for ativo in ativos:
            try:
                # Buscar dados (yfinance retorna MultiIndex para coluna Close)
                df = yf.download(ativo, period="5y", interval="1d", progress=False)
                
                if df is None or len(df) < 72:
                    print("  [SKIP] " + ativo + ": Dados insuficientes")
                    continue
                
                # Se tem MultiIndex, extrair a coluna correta
                if isinstance(df.columns, pd.MultiIndex):
                    # MultiIndex como ('Close', 'ITSA4.SA')
                    close_col = [col for col in df.columns if col[0] == 'Close'][0]
                    df_close = df[close_col].copy()
                else:
                    # Single index normal
                    df_close = df['Close'].copy()
                
                # Calcular SMA
                sma17 = df_close.rolling(17).mean()
                sma72 = df_close.rolling(72).mean()
                
                # Extrair ultimos valores
                close = float(df_close.iloc[-1])
                sma17_val = float(sma17.iloc[-1])
                sma72_val = float(sma72.iloc[-1])
                min5y = float(df_close.min())
                max5y = float(df_close.max())
                
                # Determinar sinal
                if sma17_val > sma72_val:
                    sinal = "COMPRA"
                elif sma17_val < sma72_val:
                    sinal = "VENDA"
                else:
                    sinal = "NEUTRO"
                
                relatorio["carteiras"][carteira].append({
                    "Ativo": ativo,
                    "Fechamento": round(close, 2),
                    "SMA17": round(sma17_val, 2),
                    "SMA72": round(sma72_val, 2),
                    "Min (5y)": round(min5y, 2),
                    "Max (5y)": round(max5y, 2),
                    "Sinal": sinal
                })
                
                print("  [OK] " + ativo + ": " + sinal)
                
            except Exception as e:
                print("  [ERRO] " + ativo + ": " + str(e)[:80])
                continue
    
    return relatorio

def gerar_html_simples(relatorio):
    """Gera HTML extremamente simples"""
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIGILANTE - Monitor de Medias Moveis</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial; background: #f0f0f0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        h1 { color: #333; margin-bottom: 5px; }
        .info { color: #666; font-size: 14px; margin-bottom: 30px; }
        h2 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px; margin-top: 25px; margin-bottom: 15px; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th { background: #f5f5f5; padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-weight: 600; }
        td { padding: 10px; border-bottom: 1px solid #eee; }
        tr:hover { background: #f9f9f9; }
        .compra { background: #d4edda; color: #155724; padding: 4px 8px; border-radius: 3px; }
        .venda { background: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 3px; }
        .neutro { background: #e2e3e5; color: #383d41; padding: 4px 8px; border-radius: 3px; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>VIGILANTE - Monitor de Medias Moveis</h1>
        <div class="info">SMA17 vs SMA72<br>Atualizado em: {TIMESTAMP}</div>
"""
    
    for carteira, dados in relatorio.get("carteiras", {}).items():
        if not dados:
            continue
        
        html += "<h2>" + carteira + "</h2><table><tr><th>Ativo</th><th>Fechamento</th><th>SMA17</th><th>SMA72</th><th>Min (5y)</th><th>Max (5y)</th><th>Sinal</th></tr>"
        
        for item in dados:
            cls = "compra" if "COMPRA" in item["Sinal"] else ("venda" if "VENDA" in item["Sinal"] else "neutro")
            html += "<tr><td><strong>" + item['Ativo'] + "</strong></td>"
            html += "<td>R$ " + str(item['Fechamento']) + "</td>"
            html += "<td>" + str(item['SMA17']) + "</td>"
            html += "<td>" + str(item['SMA72']) + "</td>"
            html += "<td>R$ " + str(item['Min (5y)']) + "</td>"
            html += "<td>R$ " + str(item['Max (5y)']) + "</td>"
            html += "<td><span class=\"" + cls + "\">" + item['Sinal'] + "</span></td></tr>"
        
        html += "</table>"
    
    html += "<div class=\"footer\"><p>Atualizado em: " + agora().strftime('%d/%m/%Y %H:%M:%S BRT') + "</p><p>Proxima atualizacao: proxima hora cheia</p></div></div></body></html>"
    
    return html.replace("{TIMESTAMP}", agora().strftime("%d/%m/%Y %H:%M:%S BRT"))

def main():
    try:
        # Processar dados
        relatorio = buscar_e_processar()
        
        # Salvar JSON
        os.makedirs("data", exist_ok=True)
        with open("data/current-analysis.json", "w", encoding="utf-8") as f:
            json.dump(relatorio, f, ensure_ascii=False, indent=2)
        print("[OK] Dados salvos em data/current-analysis.json")
        
        # Gerar HTML
        html = gerar_html_simples(relatorio)
        with open("relatorio_monitor.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("[OK] HTML gerado em relatorio_monitor.html")
        
        print("[SUCESSO] Finalizacao - " + agora().strftime('%d/%m/%Y %H:%M:%S BRT'))
        return 0
        
    except Exception as e:
        print("[ERRO FATAL]:", str(e))
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
