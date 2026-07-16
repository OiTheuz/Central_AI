@echo off
cd /d "%~dp0"
echo ===================================================
echo PREPARANDO O NOVO SERVIDOR (184.107.88.20)
echo ===================================================
echo.
echo [1/2] Enviando scripts de setup para a nova VPS...
scp setup_vps.sh setup_nginx.sh central_api.conf central_ai.service fix_ws.py root@184.107.88.20:/root/
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao enviar arquivos.
    pause
    exit /b
)

echo.
echo [2/2] Executando scripts de configuracao na VPS...
ssh root@184.107.88.20 "chmod +x /root/setup_vps.sh /root/setup_nginx.sh && /root/setup_vps.sh && /root/setup_nginx.sh"

echo.
echo ===================================================
echo   VPS PREPARADA COM SUCESSO!
echo ===================================================
echo Agora voce pode rodar o deploy_backend.bat normalmente!
pause
