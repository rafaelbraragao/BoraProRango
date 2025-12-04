@echo off
call venv\Scripts\activate.bat

echo.
echo ================================
echo   INICIAR APLICATIVO FLASK
echo ================================
echo.
echo Escolha o ambiente:
echo [1] Desenvolvimento
echo [2] Produção
echo [3] Testes
set /p opcao=Digite o número do ambiente: 

if "%opcao%"=="1" (
    set FLASK_ENV=development
) else if "%opcao%"=="2" (
    set FLASK_ENV=production
) else if "%opcao%"=="3" (
    set FLASK_ENV=testing
) else (
    echo Ambiente inválido.
    pause
    exit /b
)

set FLASK_APP=app.py
echo.
echo Iniciando com ambiente: %FLASK_ENV%
python -m flask run