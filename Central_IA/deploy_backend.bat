@echo off
cd /d "%~dp0"
echo ===================================================
echo   ATUALIZANDO BACKEND (CENTRAL IA) NA VPS
echo ===================================================
echo.
echo [1/2] Enviando a pasta 'app' atualizada para a nuvem...
scp -r app root@184.107.88.20:/var/www/central_ai/
scp -r scripts root@184.107.88.20:/var/www/central_ai/
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao enviar arquivos.
    pause
    exit /b
)

echo.
echo [1.3/2] Executando migracao do banco de dados (colunas novas)...
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/python scripts/add_subuser_columns.py"
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/python scripts/fix_petshop_token.py"

echo.
echo [1.5/2] Atualizando Nginx e Systemd (WebSockets Fix)...
scp fix_ws.py root@184.107.88.20:/root/fix_ws.py
scp central_ai.service root@184.107.88.20:/etc/systemd/system/central_ai.service
ssh root@184.107.88.20 "chmod +x /root/fix_ws.py && /root/fix_ws.py"
echo ===================================================
echo   TUDO PRONTO! BACKEND ATUALIZADO COM SUCESSO!
echo ===================================================
pause


