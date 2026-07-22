@echo off
echo ==============================================
echo Iniciando verificacao de FIM DE TRIAL
echo ==============================================

cd /d "%~dp0\.."
.venv\Scripts\python.exe scripts\check_fim_trial.py

echo.
echo ==============================================
echo Finalizado.
echo ==============================================
pause
