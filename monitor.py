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
ATIVOS = ["PETR4.SA", "VALE3.SA", "IVVB11.SA", "HGLG11.SA", "BBDC4.SA", "ITUB4.SA"]
toaster = ToastNotifier() if ToastNotifier else None
HORARIO_EXECUCAO = "18:30"
CAMINHO_HTML = "relatorio_monitor.html"

def gerar_html(df_relatorio):
        titulo = f"Relatório de Médias Móveis - {datetime.now().strftime('%d/%m/%Y')}"
        tabela = df_relatorio.to_html(index=False, border=0, justify="center")
        html = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 16px; }}
                    h2 {{ margin-bottom: 12px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                    th {{ background: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h2>{titulo}</h2>
                {tabela}
            </body>
        </html>
        """
        return html


def processar_diario():
    print(f"\n=== Iniciando Varredura de Fechamento: {datetime.now().strftime('%d/%m/%Y')} ===\n")
    relatorio_final = []
    relatorio_completo = []

    for ativo in ATIVOS:
        # Pega dados diários (1d)
        df = yf.download(ativo, period="5y", interval="1d", progress=False)
        
        if len(df) < 72: continue

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
            status = "COMPRA (Cruzamento de Alta)"
            relatorio_final.append({"Ativo": ativo, "Sinal": status, "Preço": round(fechamento_ultimo, 2)})
            
        # Cruzamento de Baixa
        elif sma17_penultima >= sma72_penultima and sma17_ultima < sma72_ultima:
            status = "VENDA (Cruzamento de Baixa)"
            relatorio_final.append({"Ativo": ativo, "Sinal": status, "Preço": round(fechamento_ultimo, 2)})

        relatorio_completo.append({
            "Ativo": ativo,
            "Abertura": round(abertura_ultima, 2),
            "Fechamento": round(fechamento_ultimo, 2),
            "Sinal": status,
            "Menor (5y)": round(menor_preco, 2),
            "Maior (5y)": round(maior_preco, 2)
        })

    # --- RESULTADOS ---
    if relatorio_completo:
        df_relatorio = pd.DataFrame(relatorio_completo)
        html = gerar_html(df_relatorio)
        with open(CAMINHO_HTML, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ HTML atualizado: {CAMINHO_HTML}")

    if relatorio_final:
        print("🎯 ATIVOS QUE CRUZARAM A MÉDIA HOJE:")
        df_final = pd.DataFrame(relatorio_final)
        print(df_final.to_string(index=False)) # Mostra a lista bonitinha no terminal
        
        # Gera o alerta visual no Windows
        mensagem = "\n".join([f"{item['Ativo']}: {item['Sinal']}" for item in relatorio_final])
        if toaster:
            toaster.show_toast("Alerta de Médias Móveis", 
                               mensagem,
                               duration=10)
    else:
        print("Nenhum cruzamento de média detectado nos ativos selecionados hoje.")


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