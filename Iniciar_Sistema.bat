@echo off
title Central de Comando - SaaS Igreja Inteligente
color 0B

echo ========================================================
echo        BEM-VINDO AO SAAS IGREJA INTELIGENTE
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

:: 2. Gerar o Template Visual (caso nao exista)
echo.
echo [2/4] Verificando assets visuais...
if not exist "assets\template_escala.png" (
    python privado\scripts\generate_template.py
    echo [OK] Template gerado!
) else (
    echo [OK] Template visual ja existe.
)

:: 3. Subir a Infraestrutura (Postgres, WhatsApp, API)
echo.
echo [3/4] Iniciando Servidores (Banco, WhatsApp e API)...
docker-compose up -d --build

:: Espera o banco e a API subirem
timeout /t 10 /nobreak >nul

:: Popula o banco com as novas inteligencias (Templates, Membros e Rodizio)
echo [EXTRA] Injetando Dados de Inteligencia Pastoral...
docker exec church_api python privado/scripts/seed_test_data.py

:: 4. Abrir os Portais de Acesso
echo.
echo [4/4] Abrindo Portais de Gestao no navegador...
timeout /t 5 /nobreak >nul

:: Abre o Painel Master (SaaS)
echo Abrindo Painel Master SaaS...
start "" "http://localhost:8000/dashboard/master.html"

:: Abre o Painel do Pastor (Dashboard)
echo Abrindo Portal do Pastor...
start "" "http://localhost:8000/dashboard/index.html"

echo.
echo ========================================================
echo    TUDO PRONTO! O SISTEMA ESTA RODANDO.
echo ========================================================
echo MASTER: http://localhost:8000/dashboard/master.html (admin/admin)
echo PASTOR: http://localhost:8000/dashboard/index.html (pastor1@test.com/123456)
echo.
pause
