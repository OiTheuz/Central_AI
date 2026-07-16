@echo off
cd /d "%~dp0"
echo Enviando script de correcao para a VPS...
scp scripts/fix_jessiely.py root@184.107.88.20:/var/www/central_ai/scripts/fix_jessiely.py
echo.
echo Executando script de correcao no Banco de Dados da VPS...
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/python scripts/fix_jessiely.py"
echo.
echo Correcao finalizada!
pause
