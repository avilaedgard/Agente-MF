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
    "Carteira Ações": ["ITSA4.SA", "NEOE3.SA", "BBDC4.SA", "LREN3.SA", "RDOR3.SA", "GOAU4.SA", "KLBN4.SA", "EGIE3.SA", "FLRY3.SA", "RECV3.SA", "JHSF3.SA"],
    "Carteira ETF": ["IVVB11.SA", "DIVO11.SA", "GOLD11.SA", "HASH11.SA"],
    "Watchlist": ["VALE3.SA", "PETR3.SA", "BTC-USD", "GC=F", "SI=F"],
    "Especulação": []
}

def agora():
    return datetime.now(BRT)

def buscar_e_processar():
    """Busca dados e gera relatorio"""
    print("[INFO] Iniciando - " + agora().strftime('%d/%m/%Y %H:%M:%S BRT'))
    
    relatorio = {
        "timestamp": agora().isoformat(),
        "carteiras": {},
        "historico": {}
    }
    
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
                
                # Salvar últimos 365 dias para gráficos
                df_chart = df_close.tail(365).reset_index()
                if isinstance(df_chart.columns, pd.MultiIndex):
                    df_chart.columns = ['Date', 'Close']
                else:
                    df_chart.columns = ['Date', 'Close']
                
                sma17_chart = sma17.tail(365).reset_index()
                if isinstance(sma17_chart.columns, pd.MultiIndex):
                    sma17_chart.columns = ['Date', 'SMA17']
                else:
                    sma17_chart.columns = ['Date', 'SMA17']
                    
                sma72_chart = sma72.tail(365).reset_index()
                if isinstance(sma72_chart.columns, pd.MultiIndex):
                    sma72_chart.columns = ['Date', 'SMA72']
                else:
                    sma72_chart.columns = ['Date', 'SMA72']
                
                relatorio["historico"][ativo] = {
                    "datas": df_chart['Date'].dt.strftime('%Y-%m-%d').tolist(),
                    "precos": df_chart['Close'].round(2).tolist(),
                    "sma17": sma17_chart['SMA17'].round(2).tolist(),
                    "sma72": sma72_chart['SMA72'].round(2).tolist()
                }
                
                print("  [OK] " + ativo + ": " + sinal)
                
            except Exception as e:
                print("  [ERRO] " + ativo + ": " + str(e)[:80])
                continue
    
    return relatorio

def gerar_html_simples(relatorio):
    """Gera HTML com design profissional e gráficos interativos"""
    
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIGILANTE - Análise de Médias Móveis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-bottom: 4px solid #ffc107;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 600;
            letter-spacing: 1px;
        }
        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
            margin-bottom: 15px;
        }
        .header .info-row {
            display: flex;
            justify-content: center;
            gap: 40px;
            font-size: 0.95em;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .info-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .info-item label {
            font-weight: 600;
            opacity: 0.8;
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            font-size: 1.4em;
            font-weight: 600;
            border-left: 5px solid #ffc107;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 0.95em;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        thead {
            background: #f8f9fa;
            border-bottom: 2px solid #ddd;
        }
        th {
            padding: 18px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-right: 1px solid #eee;
            width: 14.28%;
        }
        th:last-child {
            border-right: none;
        }
        td {
            padding: 16px 18px;
            border-bottom: 1px solid #eee;
            border-right: 1px solid #eee;
            width: 14.28%;
        }
        td:last-child {
            border-right: none;
        }
        tbody tr:hover {
            background: #f0f8ff;
            transition: background 0.2s ease;
        }
        tbody tr:last-child td {
            border-bottom: none;
        }
        
        .ativo-link {
            color: #2a5298;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 2px dotted #2a5298;
            transition: 0.3s;
        }
        .ativo-link:hover {
            color: #764ba2;
            border-bottom-color: #764ba2;
        }
        
        .sinal {
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: 600;
            text-align: center;
            display: inline-block;
            min-width: 90px;
        }
        .compra {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .venda {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .neutro {
            background: #e2e3e5;
            color: #383d41;
            border: 1px solid #d6d8db;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }
        .footer p {
            margin: 5px 0;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .modal-content {
            background: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 12px;
            width: 90%;
            max-width: 1000px;
            box-shadow: 0 10px 50px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn {
            from {
                transform: translateY(-50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 2px solid #eee;
            padding-bottom: 15px;
        }
        .modal-header h2 {
            font-size: 1.5em;
            color: #333;
        }
        .close-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 8px 15px;
            font-size: 1em;
            border-radius: 6px;
            cursor: pointer;
            transition: 0.3s;
        }
        .close-btn:hover {
            background: #c82333;
        }
        .chart-container {
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }
        
        @media (max-width: 768px) {
            .header { padding: 25px; }
            .header h1 { font-size: 1.8em; }
            .header .info-row { gap: 20px; }
            .content { padding: 20px; }
            th, td { font-size: 0.85em; padding: 12px; width: auto; }
            .modal-content { width: 95%; margin: 20% auto; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>VIGILANTE</h1>
            <div class="subtitle">Análise de Médias Móveis - SMA17 vs SMA72</div>
            <div class="info-row">
                <div class="info-item">
                    <label>Atualizado em:</label>
                    <span>{TIMESTAMP}</span>
                </div>
                <div class="info-item">
                    <label>Próxima atualização:</label>
                    <span>Próxima hora cheia</span>
                </div>
            </div>
        </div>
        
        <div class="content">
"""
    
    for carteira, dados in relatorio.get("carteiras", {}).items():
        if not dados:
            continue
        
        html += '<div class="section">\n'
        html += '<h2>' + carteira + '</h2>\n'
        html += '<table>\n'
        html += '<thead><tr>'
        html += '<th>Ativo</th>'
        html += '<th>Fechamento</th>'
        html += '<th>SMA17</th>'
        html += '<th>SMA72</th>'
        html += '<th>Mín (5y)</th>'
        html += '<th>Máx (5y)</th>'
        html += '<th>Sinal</th>'
        html += '</tr></thead>\n'
        html += '<tbody>\n'
        
        for item in dados:
            cls = "compra" if "COMPRA" in item["Sinal"] else ("venda" if "VENDA" in item["Sinal"] else "neutro")
            ativo = item['Ativo']
            
            html += '<tr>'
            html += '<td><span class="ativo-link" onclick="abrirGrafico(\'' + ativo + '\')">' + ativo + '</span></td>'
            html += '<td>R$ ' + str(item['Fechamento']) + '</td>'
            html += '<td>' + str(item['SMA17']) + '</td>'
            html += '<td>' + str(item['SMA72']) + '</td>'
            html += '<td>R$ ' + str(item['Min (5y)']) + '</td>'
            html += '<td>R$ ' + str(item['Max (5y)']) + '</td>'
            html += '<td><span class="sinal ' + cls + '">' + item['Sinal'] + '</span></td>'
            html += '</tr>\n'
        
        html += '</tbody>\n'
        html += '</table>\n'
        html += '</div>\n'
    
    html += """
        </div>
        
        <div class="footer">
            <p><strong>Método:</strong> Análise técnica baseada em Médias Móveis Simples (SMA)</p>
            <p><strong>Sinal COMPRA:</strong> SMA17 acima de SMA72 | <strong>Sinal VENDA:</strong> SMA17 abaixo de SMA72</p>
            <p style="margin-top: 15px; color: #999; font-size: 0.85em;">Sistema automatizado - Atualização horária - Dados do Yahoo Finance</p>
        </div>
    </div>
    
    <div id="chartModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Gráfico</h2>
                <button class="close-btn" onclick="fecharGrafico()">Fechar</button>
            </div>
            <div class="chart-container">
                <canvas id="myChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        const historico = """ + json.dumps(relatorio.get("historico", {})) + """;
        
        function abrirGrafico(ativo) {
            if (!historico[ativo]) {
                alert('Dados não disponíveis para ' + ativo);
                return;
            }
            
            document.getElementById('modalTitle').textContent = 'Gráfico - ' + ativo;
            document.getElementById('chartModal').style.display = 'block';
            
            const dados = historico[ativo];
            const ctx = document.getElementById('myChart').getContext('2d');
            
            if (window.currentChart instanceof Chart) {
                window.currentChart.destroy();
            }
            
            window.currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dados.datas,
                    datasets: [
                        {
                            label: 'Preço de Fechamento',
                            data: dados.precos,
                            borderColor: '#2a5298',
                            backgroundColor: 'rgba(42, 82, 152, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3,
                            pointRadius: 2,
                            pointHoverRadius: 5
                        },
                        {
                            label: 'SMA17 (Curto Prazo)',
                            data: dados.sma17,
                            borderColor: '#ffc107',
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.3,
                            pointRadius: 1
                        },
                        {
                            label: 'SMA72 (Longo Prazo)',
                            data: dados.sma72,
                            borderColor: '#dc3545',
                            backgroundColor: 'transparent',
                            borderWidth: 2,
                            fill: false,
                            tension: 0.3,
                            pointRadius: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: { padding: 15, font: { size: 11 } }
                        },
                        title: {
                            display: true,
                            text: 'Análise de Preço e Médias Móveis - Últimos 365 dias'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            grid: { color: 'rgba(0, 0, 0, 0.05)' }
                        },
                        x: {
                            grid: { color: 'rgba(0, 0, 0, 0.05)' },
                            maxTicksLimit: 10
                        }
                    }
                }
            });
        }
        
        function fecharGrafico() {
            document.getElementById('chartModal').style.display = 'none';
        }
        
        window.onclick = function(event) {
            const modal = document.getElementById('chartModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""
    
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
