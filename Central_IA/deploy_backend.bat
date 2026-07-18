@echo off
cd /d "%~dp0"
echo ===================================================
echo   ATUALIZANDO BACKEND (CENTRAL IA) NA VPS
echo ===================================================
echo.
echo [1/3] Enviando a pasta 'app' e o '.env' para a nuvem...
scp -r app root@184.107.88.20:/var/www/central_ai/
scp .env root@184.107.88.20:/var/www/central_ai/.env
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao enviar arquivos.
    pause
    exit /b
)

echo.
echo [2/3] Instalando novas bibliotecas (se houver)...
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/pip install -r requirements.txt"

echo.
echo [3/3] Reiniciando a Inteligência Artificial...
ssh root@184.107.88.20 "systemctl restart central_ai"

echo ===================================================
echo   TUDO PRONTO! BACKEND ATUALIZADO COM SUCESSO!
echo ===================================================
pause
