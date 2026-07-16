@echo off
cd /d "%~dp0"
echo Enviando script de configuracao do Token Global para a VPS...
scp scripts/set_global_test_token.py root@184.107.88.20:/var/www/central_ai/scripts/set_global_test_token.py
echo.
echo Atualizando o Token Global no servidor...
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/python scripts/set_global_test_token.py && systemctl restart central_ai"
echo.
echo Configuracao finalizada!
pause
