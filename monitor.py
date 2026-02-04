import os
import time
import json
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import requests

try:
    from win10toast import ToastNotifier
except Exception:
    ToastNotifier = None

# Alpha Vantage API key (substitua pela sua chave)
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "EX6OIZP8MT79GC9N")

# Mapeamento de commodities para Alpha Vantage
COMMODITY_SYMBOLS = {
    "GC=F": "GLD",  # Ouro
    "SI=F": "SLV",  # Prata
}

def fetch_commodity_data(symbol, period="5y"):
    """Busca dados de commodities - não mais necessário, YFinance trata direto"""
    return None


def fetch_data(ativo):
    """Tenta buscar dados do Yahoo Finance"""
    # Remapear GOLD e SILVER para os ETFs GLD e SLV
    symbol_map = {
        "GOLD": "GLD",  # SPDR Gold Trust ETF
        "SILVER": "SLV"  # iShares Silver Trust ETF
    }
    
    # Usar o mapa se necessário
    ticker = symbol_map.get(ativo, ativo)
    
    try:
        # Yahoo Finance para ações/ETFs
        df = yf.download(ticker, period="5y", interval="1d", progress=False)
        if df is not None and len(df) > 0:
            return df
    except:
        pass
    
    return None
    
    # Se nada funcionou, retorna None
    return None

# Configurações
CARTEIRAS = {
    "Carteira Ações": ["ITSA4.SA", "NEOE3.SA", "BBDC4.SA", "LREN3.SA", "RDOR3.SA", "GOAU4.SA", "KLBN4.SA", "EGIE3.SA", "RECV3.SA", "JHSF3.SA"],
    "Carteira ETF": ["IVVB11.SA", "GOLD11.SA", "DIVO11.SA", "HASH11.SA"],
    "Watchlist": ["VALE3.SA", "PETR3.SA", "BTC-USD", "GOLD", "SILVER"],  # GOLD->GLD, SILVER->SLV (ETFs via YFinance)
    "Especulação": ["CEAB3.SA", "S1BS34.SA"]
}

toaster = ToastNotifier() if ToastNotifier else None
HORARIO_EXECUCAO = "18:30"
CAMINHO_HTML = "relatorio_monitor.html"

# Fuso horário do Brasil (GMT-3)
BRT = timezone(timedelta(hours=-3))

def agora_brt():
    """Retorna datetime atual no fuso horário de Brasília (BRT/GMT-3)"""
    return datetime.now(BRT)

def gerar_html(relatorios_por_carteira, charts_data):
    titulo = f"Relatório de Médias Móveis - {agora_brt().strftime('%d/%m/%Y %H:%M')}"
    html_tabelas = ""
    
    for carteira, df_relatorio in relatorios_por_carteira.items():
        html_tabelas += f"<h3>{carteira}</h3>\n"
        if not df_relatorio.empty:
            # Criar HTML customizado para a tabela
            html_tabelas += "<table>\n<thead>\n<tr>"
            html_tabelas += "<th>Ativo</th><th>Abertura</th><th>Fechamento</th><th>Sinal</th>"
            html_tabelas += "<th>SMA17</th><th>SMA72</th><th>Distancia</th><th>Ultimo Cruzamento</th>"
            html_tabelas += "<th>Minimo (5y)</th><th>Maximo (5y)</th>"
            html_tabelas += "</tr>\n</thead>\n<tbody>\n"
            
            for _, row in df_relatorio.iterrows():
                sinal_class = "compra" if "COMPRA" in str(row['Sinal']) else "venda" if "VENDA" in str(row['Sinal']) else "neutro"
                tooltip = "COMPRA: SMA17 esta acima de SMA72 (tendencia de alta)" if "COMPRA" in str(row['Sinal']) else \
                          "VENDA: SMA17 esta abaixo de SMA72 (tendencia de baixa)" if "VENDA" in str(row['Sinal']) else \
                          "NEUTRO: Medias estao no mesmo nivel"
                
                html_tabelas += f"<tr>"
                html_tabelas += f"<td><button class='asset-link' onclick=\"openChart('{row['Ativo']}')\">{row['Ativo']}</button></td>"
                html_tabelas += f"<td>R$ {row['Abertura']:.2f}</td>"
                html_tabelas += f"<td>R$ {row['Fechamento']:.2f}</td>"
                html_tabelas += f"<td title='{tooltip}' class='{sinal_class}'>{row['Sinal']}</td>"
                html_tabelas += f"<td>{row['SMA17']:.2f}</td>"
                html_tabelas += f"<td>{row['SMA72']:.2f}</td>"
                html_tabelas += f"<td>{row['Distancia']:.2f}</td>"
                html_tabelas += f"<td>{row['Ultimo Cruzamento']}</td>"
                html_tabelas += f"<td>R$ {row['Minimo (5y)']:.2f}</td>"
                html_tabelas += f"<td>R$ {row['Maximo (5y)']:.2f}</td>"
                html_tabelas += f"</tr>\n"
            
            html_tabelas += "</tbody>\n</table>\n"
        else:
            html_tabelas += f"<p style='text-align: center; color: #999;'>Nenhum dado disponível nesta carteira.</p>\n"
        html_tabelas += "<br>"
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatorio de Medias Moveis</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            padding: 30px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        h2 {{ 
            margin-bottom: 30px;
            color: #2c3e50;
            text-align: center;
            font-size: 28px;
            border-bottom: 4px solid #0366d6;
            padding-bottom: 15px;
        }}
        
        h3 {{
            margin-top: 30px;
            margin-bottom: 15px;
            color: #fff;
            background: linear-gradient(135deg, #0366d6, #0549a0);
            padding: 12px 20px;
            border-radius: 5px;
            font-size: 18px;
        }}
        
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            margin-bottom: 25px;
            background-color: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border-radius: 5px;
            overflow: hidden;
        }}
        
        thead {{
            background: #2c3e50;
        }}
        
        th {{
            color: white;
            padding: 14px;
            text-align: center;
            font-weight: 600;
            border-right: 1px solid #ecf0f1;
            font-size: 13px;
        }}
        
        th:last-child {{
            border-right: none;
        }}
        
        td {{
            padding: 12px 14px;
            text-align: center;
            border-right: 1px solid #ecf0f1;
            font-size: 14px;
        }}
        
        td:last-child {{
            border-right: none;
        }}
        
        tbody tr {{
            border-bottom: 1px solid #ecf0f1;
            transition: background-color 0.3s ease;
        }}
        
        tbody tr:hover {{
            background-color: #f8f9fa;
        }}
        
        tbody tr:last-child {{
            border-bottom: none;
        }}
        
        .compra {{
            background-color: #d4edda;
            color: #155724;
            font-weight: bold;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: help;
        }}
        
        .venda {{
            background-color: #f8d7da;
            color: #721c24;
            font-weight: bold;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: help;
        }}
        
        .neutro {{
            background-color: #e2e3e5;
            color: #383d41;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: help;
        }}
        
        td[title] {{
            position: relative;
        }}
        
        strong {{
            color: #0366d6;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #7f8c8d;
            font-size: 12px;
        }}
        .asset-link {{
            background: none;
            border: none;
            color: #0366d6;
            font-weight: 700;
            cursor: pointer;
            text-decoration: underline;
        }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.75);
        }}
        .modal-content {{
            background-color: #0d1117;
            margin: 5% auto;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            max-width: 1100px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }}
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #c9d1d9;
            margin-bottom: 10px;
        }}
        .modal-close {{
            color: #c9d1d9;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
            border: none;
            background: transparent;
        }}
        #chart {{
            width: 100%;
            height: 520px;
        }}
    </style>
    <script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
</head>
<body>
    <div class="container">
        <h2>{titulo}</h2>
        {html_tabelas if html_tabelas.strip() else '<p style="text-align: center; color: #7f8c8d;">Nenhum dado disponivel no momento.</p>'}
        <div class="footer">
            <p>Atualizado automaticamente todos os dias as 18:30 BRT</p>
            <p>SMA17: Media Movel de 17 periodos | SMA50: Media Movel de 50 periodos</p>
        </div>
    </div>
    <div id="chartModal" class="modal" onclick="closeChart(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h3 id="chartTitle">Grafico</h3>
                <button class="modal-close" onclick="closeChart()">&times;</button>
            </div>
            <div id="chart"></div>
        </div>
    </div>
    <script>
        const chartsData = {json.dumps(charts_data, ensure_ascii=False)};

        function openChart(ativo) {{
            const data = chartsData[ativo];
            if (!data) return;

            document.getElementById('chartTitle').textContent = `TradingView Style - ${'{'}ativo{'}'}`;
            document.getElementById('chartModal').style.display = 'block';

            const closeTrace = {{
                x: data.dates,
                y: data.close,
                type: 'scatter',
                mode: 'lines',
                name: 'Preço',
                line: {{ color: '#2dd4bf', width: 2 }}
            }};
            const sma17Trace = {{
                x: data.dates,
                y: data.sma17,
                type: 'scatter',
                mode: 'lines',
                name: 'SMA17',
                line: {{ color: '#f59e0b', width: 1.5 }}
            }};
            const sma72Trace = {{
                x: data.dates,
                y: data.sma72,
                type: 'scatter',
                mode: 'lines',
                name: 'SMA72',
                line: {{ color: '#ef4444', width: 1.5 }}
            }};

            const layout = {{
                paper_bgcolor: '#0d1117',
                plot_bgcolor: '#0d1117',
                font: {{ color: '#c9d1d9' }},
                xaxis: {{
                    showgrid: true,
                    gridcolor: '#1f2937',
                    rangeslider: {{ visible: false }}
                }},
                yaxis: {{
                    showgrid: true,
                    gridcolor: '#1f2937'
                }},
                legend: {{ orientation: 'h', y: -0.2 }},
                margin: {{ t: 30, r: 20, b: 60, l: 50 }}
            }};

            Plotly.newPlot('chart', [closeTrace, sma17Trace, sma72Trace], layout, {{ responsive: true }});
        }}

        function closeChart(event) {{
            document.getElementById('chartModal').style.display = 'none';
            Plotly.purge('chart');
        }}
    </script>
</body>
</html>"""
    return html


def processar_diario():
    print(f"\n=== Iniciando Varredura de Fechamento: {agora_brt().strftime('%d/%m/%Y')} ===\n")
    relatorios_por_carteira = {carteira: [] for carteira in CARTEIRAS}
    charts_data = {}
    sinais_finais = []

    def _series(col_name, data_frame):
        series = data_frame[col_name]
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]
        return series

    for carteira, ativos in CARTEIRAS.items():
        print(f"\n[*] Processando {carteira}...")
        for ativo in ativos:
            try:
                # Pega dados diários usando função com fallback
                df = fetch_data(ativo)
                
                if df is None or len(df) < 72:
                    print(f"  [AVISO] {ativo}: Dados insuficientes")
                    continue

                # Médias
                df['SMA17'] = df['Close'].rolling(window=17).mean()
                df['SMA72'] = df['Close'].rolling(window=72).mean()
                
                # Encontrar o último cruzamento
                df['Cruzamento'] = (df['SMA17'] > df['SMA72']).astype(int).diff()
                cruzamentos = df[df['Cruzamento'] != 0]
                
                if len(cruzamentos) > 0:
                    ultima_data_cruzamento = cruzamentos.index[-1].strftime('%d/%m/%Y')
                    data_ultimo_cruzamento = cruzamentos.index[-1]
                else:
                    ultima_data_cruzamento = "Sem dados"
                    data_ultimo_cruzamento = df.index[-1]
                
                # Pegar dados desde 1 ano antes do último cruzamento
                from datetime import timedelta
                data_inicio = data_ultimo_cruzamento - timedelta(days=365)
                df_chart = df[df.index >= data_inicio].copy()

                # Últimos 2 dias para detectar o cruzamento no fechamento
                sma17_penultima = df['SMA17'].iloc[-2]
                sma72_penultima = df['SMA72'].iloc[-2]
                sma17_ultima = df['SMA17'].iloc[-1]
                sma72_ultima = df['SMA72'].iloc[-1]
                fechamento_ultimo = df['Close'].iloc[-1]
                abertura_ultima = df['Open'].iloc[-1]
                menor_preco = df['Low'].min()
                maior_preco = df['High'].max()
                
                # Converter para float se necessário
                if hasattr(abertura_ultima, 'item'):
                    abertura_ultima = abertura_ultima.item()
                if hasattr(fechamento_ultimo, 'item'):
                    fechamento_ultimo = fechamento_ultimo.item()
                if hasattr(sma17_ultima, 'item'):
                    sma17_ultima = sma17_ultima.item()
                if hasattr(sma72_ultima, 'item'):
                    sma72_ultima = sma72_ultima.item()
                if hasattr(sma17_penultima, 'item'):
                    sma17_penultima = sma17_penultima.item()
                if hasattr(sma72_penultima, 'item'):
                    sma72_penultima = sma72_penultima.item()
                if hasattr(menor_preco, 'item'):
                    menor_preco = menor_preco.item()
                if hasattr(maior_preco, 'item'):
                    maior_preco = maior_preco.item()

                if pd.isna([sma17_penultima, sma72_penultima, sma17_ultima, sma72_ultima]).any():
                    continue

                # Lógica baseada na posição das médias
                if sma17_ultima > sma72_ultima:
                    status = "COMPRA"
                elif sma17_ultima < sma72_ultima:
                    status = "VENDA"
                else:
                    status = "Neutro"
                
                # Detectar cruzamentos para alertas especiais
                cruzamento = False
                if sma17_penultima <= sma72_penultima and sma17_ultima > sma72_ultima:
                    cruzamento = True
                    sinais_finais.append({"Carteira": carteira, "Ativo": ativo, "Sinal": "COMPRA (Cruzamento)", "Preco": round(fechamento_ultimo, 2)})
                elif sma17_penultima >= sma72_penultima and sma17_ultima < sma72_ultima:
                    cruzamento = True
                    sinais_finais.append({"Carteira": carteira, "Ativo": ativo, "Sinal": "VENDA (Cruzamento)", "Preco": round(fechamento_ultimo, 2)})

                relatorios_por_carteira[carteira].append({
                    "Ativo": ativo,
                    "Abertura": round(float(abertura_ultima), 2),
                    "Fechamento": round(float(fechamento_ultimo), 2),
                    "Sinal": status,
                    "SMA17": round(float(sma17_ultima), 2),
                    "SMA72": round(float(sma72_ultima), 2),
                    "Distancia": round(abs(float(sma17_ultima) - float(sma72_ultima)), 2),
                    "Ultimo Cruzamento": ultima_data_cruzamento,
                    "Minimo (5y)": round(float(menor_preco), 2),
                    "Maximo (5y)": round(float(maior_preco), 2)
                })
                # Guardar dados para o grafico (ultimo 180 dias)
                # Guardar dados para o grafico
                df_chart = df[df.index >= data_inicio].copy()
                close_series = _series('Close', df_chart)
                sma17_series = _series('SMA17', df_chart)
                sma72_series = _series('SMA72', df_chart)
                charts_data[ativo] = {
                    "dates": [d.strftime('%Y-%m-%d') for d in df_chart.index],
                    "close": [float(v) if not pd.isna(v) else None for v in close_series.tolist()],
                    "sma17": [float(v) if not pd.isna(v) else None for v in sma17_series.tolist()],
                    "sma72": [float(v) if not pd.isna(v) else None for v in sma72_series.tolist()]
                }
                print(f"  [OK] {ativo}: {status}")
                
            except Exception as e:
                print(f"  [ERRO] {ativo}: {str(e)}")
                continue

    # --- RESULTADOS ---
    # Converter para DataFrames
    relatorios_df = {}
    for carteira, dados in relatorios_por_carteira.items():
        if dados:
            relatorios_df[carteira] = pd.DataFrame(dados)
        else:
            relatorios_df[carteira] = pd.DataFrame()
    
    # Gerar HTML
    html = gerar_html(relatorios_df, charts_data)
    with open(CAMINHO_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n[OK] HTML atualizado: {CAMINHO_HTML}")

    if sinais_finais:
        print("\n[ALERTA] ATIVOS QUE CRUZARAM A MEDIA HOJE:")
        df_sinais = pd.DataFrame(sinais_finais)
        print(df_sinais.to_string(index=False))
        
        # Gera o alerta visual no Windows
        mensagem = "\n".join([f"{item['Ativo']} ({item['Carteira']}): {item['Sinal']}" for item in sinais_finais])
        if toaster:
            toaster.show_toast("Alerta de Medias Moveis", 
                               mensagem,
                               duration=10)
    else:
        print("\n[OK] Nenhum cruzamento de media detectado nos ativos selecionados hoje.")


def loop_diario():
    ultima_execucao = None
    while True:
        agora = agora_brt()
        horario_atual = agora.strftime("%H:%M")
        data_atual = agora.date()

        if horario_atual == HORARIO_EXECUCAO and ultima_execucao != data_atual:
            processar_diario()
            ultima_execucao = data_atual

        time.sleep(30)

if __name__ == "__main__":
    if os.getenv("RUN_ONCE") == "1":
        processar_diario()
    else:
        loop_diario()