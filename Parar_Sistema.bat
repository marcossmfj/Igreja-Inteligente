@echo off
title Parando o SaaS Igreja Inteligente...
color 0C

echo ========================================================
echo        PARANDO O SISTEMA SAAS
echo ========================================================
echo.
echo Desligando o Banco de Dados, API e WhatsApp...
echo.

docker-compose down

echo.
echo ========================================================
echo    SISTEMA DESLIGADO COM SUCESSO!
echo ========================================================
echo.
pause
