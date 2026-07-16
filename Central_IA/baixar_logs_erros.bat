@echo off
cd /d "%~dp0"
echo Baixando logs da VPS filtrados (última 1 hora)...
ssh root@184.107.88.20 "journalctl -u central_ai.service --since '1 hour ago' --no-pager | grep -E 'webhook|ERROR|WARNING|Exception|Traceback'" > vps_webhook_logs.txt
echo.
echo Logs salvos em vps_webhook_logs.txt!
pause
