#!/bin/bash

# ========================================
# VIGILANTE - Script de Inicialização
# ========================================

echo ""
echo "  ███████╗ ██████╗ ███╗   ███╗ ██████╗"
echo "  ██╔════╝██╔════╝ ████╗ ████║██╔═══██╗"
echo "  █████╗  ██║  ███╗██╔████╔██║██║   ██║"
echo "  ██╔══╝  ██║   ██║██║╚██╔╝██║██║   ██║"
echo "  ██║     ╚██████╔╝██║ ╚═╝ ██║╚██████╔╝"
echo "  ╚═╝      ╚═════╝ ╚═╝     ╚═╝ ╚═════╝"
echo ""
echo "  Análise Inteligente de Médias Móveis"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: Python 3 não encontrado!"
    echo "Certifique-se de que Python 3 está instalado"
    exit 1
fi

# Verificar dependências
echo "⏳ Verificando e instalando dependências..."
pip3 install -r requirements.txt > /dev/null 2>&1
pip3 install -r api/requirements-api.txt > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências!"
    echo "Tente executar manualmente: pip3 install -r requirements.txt"
    exit 1
fi

echo "✓ Dependências OK"

# Iniciar API
echo ""
echo "🚀 Iniciando servidor..."
echo ""
cd api
python3 app.py

