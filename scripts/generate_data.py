"""
Script para gerar JSONs com análise atual e backtest
Para ser executado pelo GitHub Actions
"""
import json
import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from monitor import (
    fetch_data, agora_brt, analisar_com_gemini, CARTEIRAS, BRT
)
from api.backtest_engine import executar_backtest

def gerar_analise_atual():
    """Gera análise atual e salva em JSON"""
    print("[ANÁLISE] Iniciando geração de análise atual...")
    
    relatorio = {
        "timestamp": agora_brt().isoformat(),
        "carteiras": {}
    }
    
    sinais = []
    
    for carteira, ativos in CARTEIRAS.items():
        relatorio["carteiras"][carteira] = []
        print(f"  Processando {carteira}...")
        
        for ativo in ativos:
            try:
                df = fetch_data(ativo)
                
                if df is None or len(df) < 72:
                    continue
                
                df['SMA17'] = df['Close'].rolling(window=17).mean()
                df['SMA72'] = df['Close'].rolling(window=72).mean()
                
                # Dados atuais
                sma17 = float(df['SMA17'].iloc[-1])
                sma72 = float(df['SMA72'].iloc[-1])
                preco = float(df['Close'].iloc[-1])
                abertura = float(df['Open'].iloc[-1])
                minimo = float(df['Low'].min())
                maximo = float(df['High'].max())
                
                # Determinar sinal
                if sma17 > sma72:
                    sinal = "COMPRA"
                elif sma17 < sma72:
                    sinal = "VENDA"
                else:
                    sinal = "NEUTRO"
                
                # Encontrar último cruzamento
                df['Cruzamento'] = (df['SMA17'] > df['SMA72']).astype(int).diff()
                cruzamentos = df[df['Cruzamento'] != 0]
                
                if len(cruzamentos) > 0:
                    ultima_data_cruzamento = cruzamentos.index[-1].strftime('%d/%m/%Y')
                else:
                    ultima_data_cruzamento = "Sem dados"
                
                item = {
                    "ativo": ativo,
                    "preco": round(preco, 2),
                    "abertura": round(abertura, 2),
                    "sinal": sinal,
                    "sma17": round(sma17, 2),
                    "sma72": round(sma72, 2),
                    "distancia": round(abs(sma17 - sma72), 2),
                    "ultimo_cruzamento": ultima_data_cruzamento,
                    "minimo_5y": round(minimo, 2),
                    "maximo_5y": round(maximo, 2)
                }
                
                relatorio["carteiras"][carteira].append(item)
                
                # Detector de cruzamento nos últimos 14 dias
                data_limite = agora_brt().date() - timedelta(days=14)
                for i in range(len(df)-1, 1, -1):
                    data_candle = df.index[i].date()
                    if data_candle < data_limite:
                        break
                    
                    sma17_ant = df['SMA17'].iloc[i-1]
                    sma72_ant = df['SMA72'].iloc[i-1]
                    sma17_atu = df['SMA17'].iloc[i]
                    sma72_atu = df['SMA72'].iloc[i]
                    
                    try:
                        if sma17_ant <= sma72_ant and sma17_atu > sma72_atu:
                            sinais.append({
                                "carteira": carteira,
                                "ativo": ativo,
                                "sinal": "COMPRA",
                                "preco": round(preco, 2),
                                "data": df.index[i].strftime('%d/%m/%Y'),
                                "sma17": round(sma17, 2),
                                "sma72": round(sma72, 2),
                                "distancia": round(abs(sma17 - sma72), 2)
                            })
                        elif sma17_ant >= sma72_ant and sma17_atu < sma72_atu:
                            sinais.append({
                                "carteira": carteira,
                                "ativo": ativo,
                                "sinal": "VENDA",
                                "preco": round(preco, 2),
                                "data": df.index[i].strftime('%d/%m/%Y'),
                                "sma17": round(sma17, 2),
                                "sma72": round(sma72, 2),
                                "distancia": round(abs(sma17 - sma72), 2)
                            })
                    except:
                        pass
            
            except Exception as e:
                print(f"  [ERRO] {ativo}: {str(e)}")
                continue
    
    relatorio["sinais_recentes"] = sinais
    
    # Análise com Gemini se houver sinais
    if sinais:
        try:
            print("  Analisando com Gemini...")
            relatorio["analise_gemini"] = analisar_com_gemini(sinais)
        except Exception as e:
            print(f"  [WARN] Gemini erro: {e}")
    
    # Salvar em JSON
    os.makedirs('data', exist_ok=True)
    with open('data/current-analysis.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Análise salva em data/current-analysis.json")
    return relatorio


def gerar_backtest():
    """Gera backtest e salva em JSON"""
    print("[BACKTEST] Iniciando geração de backtest...")
    
    try:
        resultado = executar_backtest(anos=15)
        
        os.makedirs('data', exist_ok=True)
        with open('data/backtest.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Backtest salvo em data/backtest.json")
        return resultado
    
    except Exception as e:
        print(f"[ERRO] Backtest falhou: {e}")
        # Salvar erro
        erro = {
            "status": "erro",
            "mensagem": str(e),
            "timestamp": agora_brt().isoformat()
        }
        with open('data/backtest.json', 'w', encoding='utf-8') as f:
            json.dump(erro, f, indent=2, ensure_ascii=False)
        return None


if __name__ == "__main__":
    # Aceitar argumentos de linha de comando
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--analysis', action='store_true', help='Gerar análise atual')
    parser.add_argument('--backtest', action='store_true', help='Gerar backtest')
    parser.add_argument('--all', action='store_true', help='Gerar tudo')
    
    args = parser.parse_args()
    
    if args.all or args.analysis:
        gerar_analise_atual()
    
    if args.all or args.backtest:
        gerar_backtest()
    
    if not (args.all or args.analysis or args.backtest):
        # Por padrão, gerar análise
        gerar_analise_atual()
