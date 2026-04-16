@echo off
title 🤖 Robô de Testes QA - SaaS Igreja Inteligente
color 0A

set LOG_FILE=privado\manuais\logs_qa.txt

echo ========================================================
echo        INICIANDO VARREDURA COMPLETA DO SISTEMA
echo ========================================================
echo.

:: Verificar se o container está rodando
docker ps --filter "name=church_api" --format "{{.Names}}" | findstr /i "church_api" >nul
if %errorlevel% neq 0 (
    echo [ERRO] O sistema nao parece estar rodando! 
    echo Por favor, execute 'Iniciar_Sistema.bat' primeiro.
    echo.
    pause
    exit /b
)

echo [%date% %time%] INICIANDO TESTE QA > %LOG_FILE%
echo. >> %LOG_FILE%
echo [1/2] Preparando ambiente de testes isolado...
echo [2/2] Executando robos de API e Interface (Playwright)...
echo.

:: Executa o pytest e salva a saída no arquivo de log E na tela
docker exec -e PYTHONPATH=/app -e DATABASE_URL=sqlite:///./test_church.db church_api pytest tests/test_central_qa.py -v >> %LOG_FILE% 2>&1

:: Exibir o resultado na tela para o usuário (lendo do log)
type %LOG_FILE%

echo.
echo. >> %LOG_FILE%
echo [%date% %time%] VARREDURA CONCLUIDA! >> %LOG_FILE%

echo.
echo ========================================================
echo    VARREDURA CONCLUIDA! LOG SALVO EM: %LOG_FILE%
echo ========================================================
echo.
pause
