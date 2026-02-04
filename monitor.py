import os
import time
import yfinance as yf
import pandas as pd
from datetime import datetime

try:
    from win10toast import ToastNotifier
except Exception:
    ToastNotifier = None

# Configurações
CARTEIRAS = {
    "Carteira Ações": ["ITSA4.SA", "NEOE3.SA", "BBDC4.SA", "LREN3.SA", "RDOR3.SA", "GOAU4.SA", "KLBN4.SA", "EGIE3.SA", "RECV3.SA", "JHSF3.SA"],
    "Carteira ETF": ["IVVB11.SA", "GOLD11.SA", "DIVO11.SA", "HASH11.SA"],
    "Watchlist": ["VALE3.SA", "PETR3.SA", "BTC-USD", "GC=F", "SI=F"],
    "Especulação": ["CEAB3.SA", "S1BS34.SA"]
}

toaster = ToastNotifier() if ToastNotifier else None
HORARIO_EXECUCAO = "18:30"
CAMINHO_HTML = "relatorio_monitor.html"

def gerar_html(relatorios_por_carteira):
    titulo = f"Relatório de Médias Móveis - {datetime.now().strftime('%d/%m/%Y')}"
    html_tabelas = ""
    
    for carteira, df_relatorio in relatorios_por_carteira.items():
        if not df_relatorio.empty:
            tabela = df_relatorio.to_html(index=False, border=0, justify="center", classes="tabela-carteira")
            html_tabelas += f"<h3>{carteira}</h3>\n{tabela}\n<br>"
    
    html = f"""
    <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    padding: 20px; 
                    background-color: #f9f9f9;
                }}
                h2 {{ 
                    margin-bottom: 20px;
                    color: #333;
                    border-bottom: 3px solid #0366d6;
                    padding-bottom: 10px;
                }}
                h3 {{
                    margin-top: 25px;
                    color: #555;
                    background-color: #e8f0f7;
                    padding: 10px;
                    border-radius: 5px;
                }}
                table {{ 
                    border-collapse: collapse; 
                    width: 100%; 
                    margin-bottom: 15px;
                    background-color: white;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    border-radius: 5px;
                    overflow: hidden;
                }}
                th, td {{ 
                    border: 1px solid #ddd; 
                    padding: 12px; 
                    text-align: center;
                }}
                th {{ 
                    background: #0366d6;
                    color: white;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{
                    background-color: #f5f5f5;
                }}
                tr:hover {{
                    background-color: #fffacd;
                }}
                .compra {{
                    background-color: #90EE90;
                    font-weight: bold;
                }}
                .venda {{
                    background-color: #FFB6C6;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <h2>{titulo}</h2>
            {html_tabelas if html_tabelas else '<p>Nenhum dado disponível no momento.</p>'}
        </body>
    </html>
    """
    return html


def processar_diario():
    print(f"\n=== Iniciando Varredura de Fechamento: {datetime.now().strftime('%d/%m/%Y')} ===\n")
    relatorios_por_carteira = {carteira: [] for carteira in CARTEIRAS}
    sinais_finais = []

    for carteira, ativos in CARTEIRAS.items():
        print(f"\n📊 Processando {carteira}...")
        for ativo in ativos:
            try:
                # Pega dados diários (1d)
                df = yf.download(ativo, period="5y", interval="1d", progress=False)
                
                if len(df) < 72:
                    print(f"  ⚠️  {ativo}: Dados insuficientes")
                    continue

                # Médias
                df['SMA17'] = df['Close'].rolling(window=17).mean()
                df['SMA72'] = df['Close'].rolling(window=72).mean()

                # Últimos 2 dias para detectar o cruzamento no fechamento
                sma17_penultima = df['SMA17'].iloc[-2]
                sma72_penultima = df['SMA72'].iloc[-2]
                sma17_ultima = df['SMA17'].iloc[-1]
                sma72_ultima = df['SMA72'].iloc[-1]
                fechamento_ultimo = df['Close'].iloc[-1]
                abertura_ultima = df['Open'].iloc[-1]
                menor_preco = df['Low'].min()
                maior_preco = df['High'].max()

                if pd.isna([sma17_penultima, sma72_penultima, sma17_ultima, sma72_ultima]).any():
                    continue

                status = "Neutro"
                # Cruzamento de Alta
                if sma17_penultima <= sma72_penultima and sma17_ultima > sma72_ultima:
                    status = "🔼 COMPRA"
                    sinais_finais.append({"Carteira": carteira, "Ativo": ativo, "Sinal": status, "Preço": round(fechamento_ultimo, 2)})
                    
                # Cruzamento de Baixa
                elif sma17_penultima >= sma72_penultima and sma17_ultima < sma72_ultima:
                    status = "🔽 VENDA"
                    sinais_finais.append({"Carteira": carteira, "Ativo": ativo, "Sinal": status, "Preço": round(fechamento_ultimo, 2)})

                relatorios_por_carteira[carteira].append({
                    "Ativo": ativo,
                    "Abertura": round(abertura_ultima, 2),
                    "Fechamento": round(fechamento_ultimo, 2),
                    "Sinal": status,
                    "Menor (5y)": round(menor_preco, 2),
                    "Maior (5y)": round(maior_preco, 2)
                })
                print(f"  ✅ {ativo}: {status}")
                
            except Exception as e:
                print(f"  ❌ {ativo}: Erro ao processar - {str(e)}")
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
    html = gerar_html(relatorios_df)
    with open(CAMINHO_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n✅ HTML atualizado: {CAMINHO_HTML}")

    if sinais_finais:
        print("\n🎯 ATIVOS QUE CRUZARAM A MÉDIA HOJE:")
        df_sinais = pd.DataFrame(sinais_finais)
        print(df_sinais.to_string(index=False))
        
        # Gera o alerta visual no Windows
        mensagem = "\n".join([f"{item['Ativo']} ({item['Carteira']}): {item['Sinal']}" for item in sinais_finais])
        if toaster:
            toaster.show_toast("🚨 Alerta de Médias Móveis", 
                               mensagem,
                               duration=10)
    else:
        print("\n✅ Nenhum cruzamento de média detectado nos ativos selecionados hoje.")


def loop_diario():
    ultima_execucao = None
    while True:
        agora = datetime.now()
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