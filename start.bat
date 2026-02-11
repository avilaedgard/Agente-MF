@echo off
REM ========================================
REM VIGILANTE - Script de Inicialização
REM ========================================

echo.
echo  ███████╗ ██████╗ ███╗   ███╗ ██████╗
echo  ██╔════╝██╔════╝ ████╗ ████║██╔═══██╗
echo  █████╗  ██║  ███╗██╔████╔██║██║   ██║
echo  ██╔══╝  ██║   ██║██║╚██╔╝██║██║   ██║
echo  ██║     ╚██████╔╝██║ ╚═╝ ██║╚██████╔╝
echo  ╚═╝      ╚═════╝ ╚═╝     ╚═╝ ╚═════╝
echo.
echo  Análise Inteligente de Médias Móveis
echo.

REM Verificar se pip está instalado
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erro: Python pip não encontrado!
    echo Certifique-se de que Python está instalado e no PATH
    pause
    exit /b 1
)

REM Verificar dependências
echo ⏳ Verificando dependências...
pip install -r requirements.txt >nul 2>&1
pip install -r api/requirements-api.txt >nul 2>&1

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências!
    echo Tente executar manualmente: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✓ Dependências OK

REM Iniciar API
echo.
echo 🚀 Iniciando servidor...
echo.
cd api
python app.py

pause
