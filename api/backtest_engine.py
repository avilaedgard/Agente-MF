"""
Engine de Backtest - Análise histórica de 15 anos
Estratégia: Compra no cruzamento SMA17 acima de SMA72, nunca vende
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from monitor import CARTEIRAS, fetch_data, agora_brt

BRT = timezone(timedelta(hours=-3))

def calcular_retorno(preco_entrada, preco_saida):
    """Calcula retorno percentual"""
    if preco_entrada == 0:
        return 0
    return ((preco_saida - preco_entrada) / preco_entrada) * 100


def analisar_ativo_backtest(ativo, anos=15):
    """Analisa um ativo com estratégia SMA17/SMA72 por N anos"""
    try:
        # Buscar dados de N anos
        df = yf.download(ativo, period=f"{anos}y", interval="1d", progress=False)
        
        if df is None or len(df) < 72:
            return None
        
        # Garantir que é Series
        if isinstance(df['Close'], pd.DataFrame):
            df['Close'] = df['Close'].iloc[:, 0]
        
        df['SMA17'] = df['Close'].rolling(window=17).mean()
        df['SMA72'] = df['Close'].rolling(window=72).mean()
        
        # Encontrar cruzamentos (sinal de entrada)
        df['Sinal'] = 0
        df.loc[df['SMA17'] > df['SMA72'], 'Sinal'] = 1  # Compra
        df.loc[df['SMA17'] <= df['SMA72'], 'Sinal'] = 0  # Venda
        df['Posicao'] = df['Sinal'].diff()  # 1 = entrada, -1 = saída, 0 = sem mudança
        
        # Encontrar pontos de entrada (cruzamento de baixa para cima)
        entradas = df[df['Posicao'] == 1].copy()
        
        if len(entradas) == 0:
            return {
                "ativo": ativo,
                "total_entradas": 0,
                "rentabilidade_total": 0,
                "retorno_buy_hold": round(calcular_retorno(
                    df['Close'].iloc[0],
                    df['Close'].iloc[-1]
                ), 2),
                "operacoes": []
            }
        
        operacoes = []
        rentabilidade_total = 0
        
        for idx, (data_entrada, row_entrada) in enumerate(entradas.iterrows()):
            preco_entrada = row_entrada['Close']
            
            # Saída: usar o preço no final do período analisado
            preco_saida = df['Close'].iloc[-1]
            
            retorno = calcular_retorno(preco_entrada, preco_saida)
            rentabilidade_total += retorno
            
            operacoes.append({
                "num": idx + 1,
                "data_entrada": data_entrada.strftime('%Y-%m-%d'),
                "preco_entrada": round(preco_entrada, 2),
                "preco_saida": round(preco_saida, 2),
                "retorno_percent": round(retorno, 2),
                "dias": (df.index[-1] - data_entrada).days
            })
        
        # Retorno buy & hold (compra e segura)
        retorno_buy_hold = calcular_retorno(df['Close'].iloc[0], df['Close'].iloc[-1])
        
        # Calcular estatísticas
        retornos = [op['retorno_percent'] for op in operacoes]
        operacoes_positivas = len([r for r in retornos if r > 0])
        operacoes_negativas = len([r for r in retornos if r < 0])
        taxa_acerto = (operacoes_positivas / len(retornos) * 100) if retornos else 0
        
        return {
            "ativo": ativo,
            "periodo_anos": anos,
            "data_inicio": df.index[0].strftime('%Y-%m-%d'),
            "data_fim": df.index[-1].strftime('%Y-%m-%d'),
            "total_entradas": len(operacoes),
            "operacoes_positivas": operacoes_positivas,
            "operacoes_negativas": operacoes_negativas,
            "taxa_acerto_percent": round(taxa_acerto, 2),
            "rentabilidade_estrategia": round(sum(retornos), 2),
            "retorno_medio_por_operacao": round(sum(retornos) / len(retornos), 2) if retornos else 0,
            "maior_ganho": round(max(retornos), 2) if retornos else 0,
            "maior_perda": round(min(retornos), 2) if retornos else 0,
            "retorno_buy_hold": round(retorno_buy_hold, 2),
            "preco_inicial": round(df['Close'].iloc[0], 2),
            "preco_final": round(df['Close'].iloc[-1], 2),
            "operacoes": operacoes[:50]  # Limitar a 50 primeiras operações
        }
    
    except Exception as e:
        print(f"[ERRO BACKTEST] {ativo}: {str(e)}")
        return None


def executar_backtest(anos=15):
    """Executa backtest para todos os ativos de todas as carteiras"""
    print(f"\n[BACKTEST] Iniciando análise de {anos} anos...")
    
    resultado = {
        "timestamp": agora_brt().isoformat(),
        "periodo_anos": anos,
        "status": "completo",
        "resumo": {
            "total_ativos": 0,
            "ativos_analisados": 0,
            "rentabilidade_media": 0,
            "taxa_acerto_media": 0
        },
        "carteiras": {}
    }
    
    total_ativos = sum(len(ativos) for ativos in CARTEIRAS.values())
    ativos_analisados = 0
    rentabilidades = []
    taxas_acerto = []
    
    for carteira, ativos in CARTEIRAS.items():
        print(f"\n[BACKTEST] {carteira}...")
        resultado["carteiras"][carteira] = []
        
        for ativo in ativos:
            print(f"  Analisando {ativo}...", end=" ", flush=True)
            
            analise = analisar_ativo_backtest(ativo, anos=anos)
            
            if analise:
                resultado["carteiras"][carteira].append(analise)
                ativos_analisados += 1
                rentabilidades.append(analise["rentabilidade_estrategia"])
                taxas_acerto.append(analise["taxa_acerto_percent"])
                print(f"OK ({analise['retorno_buy_hold']:+.2f}%)")
            else:
                print("FALHOU")
    
    # Calcular resumo
    resultado["resumo"]["total_ativos"] = total_ativos
    resultado["resumo"]["ativos_analisados"] = ativos_analisados
    resultado["resumo"]["rentabilidade_media"] = round(
        sum(rentabilidades) / len(rentabilidades), 2
    ) if rentabilidades else 0
    resultado["resumo"]["taxa_acerto_media"] = round(
        sum(taxas_acerto) / len(taxas_acerto), 2
    ) if taxas_acerto else 0
    
    print(f"\n[BACKTEST] Concluído! {ativos_analisados}/{total_ativos} ativos analisados")
    print(f"[BACKTEST] Rentabilidade média: {resultado['resumo']['rentabilidade_media']:.2f}%")
    print(f"[BACKTEST] Taxa de acerto média: {resultado['resumo']['taxa_acerto_media']:.2f}%")
    
    return resultado


if __name__ == "__main__":
    resultado = executar_backtest(anos=15)
    import json
    print(json.dumps(resultado, indent=2))
