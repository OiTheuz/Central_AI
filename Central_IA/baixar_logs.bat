@echo off
cd /d "%~dp0"
echo Baixando logs da VPS... (digite a senha se pedir)
ssh root@184.107.88.20 "journalctl -u central_ai.service -n 100 --no-pager" > vps_logs.txt
echo Baixando log da migracao...
scp root@184.107.88.20:/var/www/central_ai/migracao_log.txt migracao_log.txt
echo.
echo Logs baixados com sucesso em vps_logs.txt e migracao_log.txt!
pause
