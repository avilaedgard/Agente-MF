#!/usr/bin/env python3
"""
Script para atualizar o monitor a cada hora durante o horário de trading (10-19h BRT)
Executa localmente e faz um push para disparar o workflow do GitHub Actions
"""

import os
import time
import subprocess
from datetime import datetime, timezone, timedelta

def agora_brt():
    """Retorna hora atual em BRT"""
    tz_brt = timezone(timedelta(hours=-3))
    return datetime.now(tz_brt)

def atualizar_timestamp():
    """Atualiza um arquivo timestamp para disparar o push"""
    timestamp_file = os.path.join(os.path.dirname(__file__), '.timestamp')
    with open(timestamp_file, 'w') as f:
        f.write(agora_brt().isoformat())

def fazer_push():
    """Faz um commit e push para disparar o workflow"""
    try:
        repo_dir = os.path.dirname(__file__)
        os.chdir(repo_dir)
        
        # Atualizar arquivo timestamp
        atualizar_timestamp()
        
        # Git add, commit e push
        subprocess.run(['git', 'add', '.timestamp'], check=True, capture_output=True)
        subprocess.run([
            'git', 'commit', 
            '-m', f'chore: atualizar monitor em {agora_brt().strftime("%H:%M BRT")}'
        ], check=True, capture_output=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True)
        
        print(f"✅ Push realizado às {agora_brt().strftime('%H:%M:%S BRT')}")
        return True
    except Exception as e:
        print(f"❌ Erro no push: {e}")
        return False

def main():
    """Loop principal - executa a cada hora entre 10h-19h BRT"""
    print("🚀 Monitor de automação iniciado")
    print(f"Horário inicial: {agora_brt().strftime('%H:%M:%S BRT')}")
    print("⏰ Executará a cada hora entre 10:00-19:00 BRT\n")
    
    ultima_execucao = None
    
    while True:
        agora = agora_brt()
        hora_atual = agora.hour
        data_atual = agora.date()
        
        # Executar se estiver entre 10h e 19h BRT e ainda não executou hoje nessa hora
        if (10 <= hora_atual <= 19) and ultima_execucao != (data_atual, hora_atual):
            print(f"\n[{agora.strftime('%H:%M:%S')}] Disparando workflow...")
            if fazer_push():
                ultima_execucao = (data_atual, hora_atual)
                print(f"Próxima execução em ~1 hora")
        
        # Aguardar 1 minuto antes de verificar novamente
        time.sleep(60)

if __name__ == "__main__":
    main()
