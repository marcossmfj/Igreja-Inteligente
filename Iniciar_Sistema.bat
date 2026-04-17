@echo off
title Central de Comando - SaaS Igreja Inteligente
color 0B

echo ========================================================
echo        BEM-VINDO AO SAAS IGREJA INTELIGENTE (LOCAL)
echo ========================================================
echo.

:: 1. Verificar se o Docker Desktop esta instalado e rodando
echo [1/4] Verificando se o motor do Docker esta ativo...
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

:: 2. Garantir arquivo .env local se nao existir
if not exist ".env" (
    echo [AVISO] Criando arquivo .env local...
    copy .env.example .env
)

:: 3. Subir a Infraestrutura (Banco, API, Proxy, Backups)
echo.
echo [2/4] Iniciando Containers via Docker Compose...
docker-compose up -d --build

:: Espera o banco e a API subirem
echo [AGUARDE] Aguardando inicializacao dos servicos (20s)...
timeout /t 20 /nobreak >nul

:: 4. Rodar o Setup de Usuarios e Linguajar
echo.
echo [3/4] Configurando Usuarios e Linguajar Padrao...
docker exec -it church_api python setup_users.py

:: 5. Abrir os Portais de Acesso
echo.
echo [4/4] Abrindo Portais de Gestao no navegador...
timeout /t 2 /nobreak >nul

:: Abre o Painel Master (SaaS)
echo Abrindo Painel Master SaaS...
start "" "http://localhost:8000/dashboard/master.html"

:: Abre o Painel do Pastor (Dashboard)
echo Abrindo Portal do Pastor...
start "" "http://localhost:8000/dashboard/index.html"

echo.
echo ========================================================
echo    TUDO PRONTO! O SISTEMA ESTA RODANDO LOCALMENTE.
echo ========================================================
echo MASTER: http://localhost:8000/dashboard/master.html
echo PASTOR: http://localhost:8000/dashboard/index.html
echo PROXY : http://localhost:81
echo ========================================================
echo.
pause
