@echo off
cd /d "%~dp0"
echo ===================================================
echo   FINALIZANDO A MIGRACAO (ENV E DEPENDENCIAS)
echo ===================================================
echo.
echo [1/2] Enviando arquivo .env e requirements.txt...
scp .env requirements.txt root@184.107.88.20:/var/www/central_ai/
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao enviar .env e requirements.txt.
    pause
    exit /b
)

echo.
echo [2/2] Instalando dependencias do Python na VPS...
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/pip install -r requirements.txt && systemctl daemon-reload && systemctl restart central_ai"

echo.
echo ===================================================
echo   TUDO PRONTO DO LADO DO CODIGO E BANCO!
echo ===================================================
echo AVISO IMPORTANTE:
echo 1. Atualize o apontamento do DNS do dominio lautz.tech
echo    para apontar para o novo IP: 184.107.88.20
echo 2. Apos o DNS ser atualizado (pode levar alguns minutos),
echo    rode o Certbot no terminal da VPS para ativar o HTTPS:
echo    certbot --nginx -d lautz.tech -d www.lautz.tech
echo.
pause
