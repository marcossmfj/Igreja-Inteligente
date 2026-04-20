@echo off
title Central de Comando - SaaS Igreja Inteligente
color 0B

echo ========================================================
echo        BEM-VINDO AO SAAS IGREJA INTELIGENTE (LOCAL)
echo ========================================================
echo.

:: 1. Verificar se o Docker Desktop esta instalado e rodando
echo [1/5] Verificando se o motor do Docker esta ativo...
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo [AVISO] Docker Desktop nao esta rodando. Tentando abrir...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    echo [AGUARDE] O Docker esta carregando. Isso pode levar ate 1 minuto...
    :wait_docker
    timeout /t 5 /nobreak >nul
    docker info >nul 2>nul
    if %errorlevel% neq 0 (
        goto wait_docker
    )
    echo.
    echo [OK] Docker iniciado com sucesso!
) else (
    echo [OK] Docker ja esta rodando.
)

:: 2. Garantir pastas e arquivo .env
echo [2/5] Preparando pastas e arquivo .env...
mkdir -p assets/tenants >nul 2>nul
mkdir -p assets/cards >nul 2>nul
mkdir -p assets/birthdays >nul 2>nul
mkdir -p assets/documents >nul 2>nul

if not exist ".env" (
    echo [AVISO] Criando arquivo .env local...
    copy .env.example .env
)

:: 3. Subir a Infraestrutura
echo.
echo [3/5] Iniciando Containers via Docker Compose...
docker-compose up -d --build

:: Espera o banco e a API subirem
echo [AGUARDE] Aguardando inicializacao dos servicos (20s)...
timeout /t 20 /nobreak >nul

:: 4. Rodar o Setup de Usuarios e Linguajar
echo.
echo [4/5] Configurando Usuarios e Linguajar Padrao...
docker exec church_api python setup_users.py

:: 5. RODAR ROBO DE QA (TESTE COMPLETO)
echo.
echo [5/5] EXECUTANDO ROBO DE QA (VISITANTES, MEMBROS, CARGOS)...
echo Aguarde o robo de QA validar o sistema...
docker exec church_api pytest tests/test_full_workflow.py -s

echo.
echo ========================================================
echo    TUDO PRONTO! SISTEMA VERIFICADO E RODANDO.
echo ========================================================
echo MASTER: http://localhost:8000/dashboard/master.html
echo PASTOR: http://localhost:8000/dashboard/index.html
echo PROXY : http://localhost:81
echo ========================================================
echo.
pause
