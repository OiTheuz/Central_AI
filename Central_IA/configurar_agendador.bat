@echo off
echo =======================================================
echo CONFIGURANDO OS ROBOS DIARIOS NO AGENDADOR DO WINDOWS
echo =======================================================

:: Pega o caminho absoluto do diretório atual
set "DIR=%~dp0"

echo.
echo [1/2] Agendando Lembrete de Vencimento (10 Dias) para todo dia as 08:00 AM...
schtasks /create /tn "OpenChatz_Lembrete_10Dias" /tr "\"%DIR%rodar_vencimentos.bat\"" /sc daily /st 08:00 /f

echo.
echo [2/2] Agendando Verificacao de Fim de Trial para todo dia as 08:05 AM...
schtasks /create /tn "OpenChatz_Fim_Trial" /tr "\"%DIR%rodar_fim_trial.bat\"" /sc daily /st 08:05 /f

echo.
echo =======================================================
echo Concluido! Os robos vao rodar sozinhos todos os dias.
echo =======================================================
pause
