import os
import json
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# Importar a lógica do monitor existente
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from monitor import (
    fetch_data, agora_brt, analisar_com_gemini, CARTEIRAS, BRT,
    _dias_desde, _fundamentos_ativo, _formatar_marketcap, 
    _montar_links_noticias
)
from backtest_engine import executar_backtest

load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Cache para dados de backtest (rodada 1x/semana)
backtest_cache = {
    "data": None,
    "timestamp": None,
    "executing": False
}

# Fuso horário do Brasil
BRT_TZ = timezone(timedelta(hours=-3))

def obter_analise_atual():
    """Retorna análise de médias móveis atual"""
    relatorio = {
        "timestamp": agora_brt().isoformat(),
        "carteiras": {}
    }
    
    sinais = []
    
    for carteira, ativos in CARTEIRAS.items():
        relatorio["carteiras"][carteira] = []
        
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
                    
                    if pd.isna([sma17_ant, sma72_ant, sma17_atu, sma72_atu]).any():
                        continue
                    
                    # COMPRA (SMA17 cruza acima)
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
                    # VENDA (SMA17 cruza abaixo)
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
            
            except Exception as e:
                print(f"[ERRO] {ativo}: {str(e)}")
                continue
    
    relatorio["sinais_recentes"] = sinais
    
    # Análise com Gemini se houver sinais
    if sinais:
        relatorio["analise_gemini"] = analisar_com_gemini(sinais)
    
    return relatorio


def executar_backtest_async():
    """Executa backtest em thread separada"""
    print("[BACKTEST] Iniciando backtest de 15 anos...")
    backtest_cache["executing"] = True
    
    try:
        resultado = executar_backtest()
        backtest_cache["data"] = resultado
        backtest_cache["timestamp"] = agora_brt().isoformat()
        print("[BACKTEST] Completado com sucesso!")
    except Exception as e:
        print(f"[ERRO BACKTEST] {str(e)}")
        backtest_cache["data"] = {
            "status": "erro",
            "mensagem": str(e)
        }
    finally:
        backtest_cache["executing"] = False


def agendar_backtest():
    """Agenda execução de backtest 1x por semana (domingo 03:00 BRT)"""
    scheduler = BackgroundScheduler(timezone='America/Sao_Paulo')
    scheduler.add_job(
        executar_backtest_async,
        trigger='cron',
        day_of_week='sun',
        hour=3,
        minute=0,
        id='backtest_semanal'
    )
    scheduler.start()
    print("[SCHEDULER] Backtest agendado para todo domingo às 03:00 BRT")


# === ROTAS API ===

@app.route('/api/current-analysis', methods=['GET'])
def api_analise_atual():
    """Retorna análise de médias móveis atual"""
    return jsonify(obter_analise_atual())


@app.route('/api/backtest', methods=['GET'])
def api_backtest():
    """Retorna resultados do backtest (cached, 1x/semana)"""
    if backtest_cache["executing"]:
        return jsonify({
            "status": "processando",
            "mensagem": "Backtest em execução..."
        }), 202
    
    if backtest_cache["data"] is None:
        # Executar backtest pela primeira vez
        executar_backtest_async()
        return jsonify({
            "status": "processando",
            "mensagem": "Gerando backtest de 15 anos..."
        }), 202
    
    return jsonify({
        "status": "sucesso",
        "timestamp": backtest_cache["timestamp"],
        "dados": backtest_cache["data"]
    })


@app.route('/api/backtest/forcar', methods=['POST'])
def api_backtest_forcar():
    """Força execução imediata do backtest (admin only)"""
    if backtest_cache["executing"]:
        return jsonify({
            "status": "erro",
            "mensagem": "Backtest já está em execução"
        }), 409
    
    # Executar em thread separada
    thread = threading.Thread(target=executar_backtest_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "status": "iniciado",
        "mensagem": "Backtest iniciado. Pode levar alguns minutos..."
    }), 202


@app.route('/api/news/<symbol>', methods=['GET'])
def api_noticias(symbol):
    """Retorna notícias de um ativo específico"""
    try:
        # Usando a função existente do monitor
        links = _montar_links_noticias([{
            "Ativo": symbol,
            "Carteira": "",
            "Data": "",
            "Sinal": ""
        }])
        
        return jsonify({
            "status": "sucesso",
            "ativo": symbol,
            "noticias": links
        })
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500


# === SERVIR FRONTEND ===

@app.route('/', methods=['GET'])
def servir_frontend():
    """Serve o arquivo index.html do frontend"""
    return send_from_directory('../frontend', 'index.html')


@app.route('/<path:filename>', methods=['GET'])
def servir_arquivo(filename):
    """Serve arquivos estáticos do frontend"""
    return send_from_directory('../frontend', filename)


if __name__ == '__main__':
    # Agendar backtest semanal
    agendar_backtest()
    
    # Executar backtest inicial
    print("[INIT] Executando backtest inicial...")
    executar_backtest_async()
    
    # Iniciar servidor Flask
    print("[SERVER] Iniciando em http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
