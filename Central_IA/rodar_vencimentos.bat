@echo off
echo ==============================================
echo Iniciando verificacao de vencimentos do Asaas
echo ==============================================

cd /d "%~dp0\.."
.venv\Scripts\python.exe scripts\check_vencimentos.py

echo.
echo ==============================================
echo Finalizado.
echo ==============================================
pause
