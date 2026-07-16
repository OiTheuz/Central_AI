@echo off
cd /d "%~dp0"
echo ===================================================
echo     COPIANDO BANCO DE DADOS (DADOS DOS USUARIOS)
echo ===================================================
echo.
echo [1/3] Acessando a VPS ANTIGA (Hostinger) para salvar os dados...
echo Se pedir senha, digite a senha da HOSTINGER!
ssh root@187.77.42.116 "sudo -u postgres pg_dump central_agendamento_db -c > /root/backup_central_ai.sql"
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao gerar o backup na VPS antiga.
    pause
    exit /b
)

echo.
echo [2/3] Baixando os dados para o seu computador...
scp root@187.77.42.116:/root/backup_central_ai.sql backup_central_ai.sql
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao baixar o arquivo.
    pause
    exit /b
)

echo.
echo [3/3] Enviando e Restaurando na VPS NOVA (Integrator)...
echo Se pedir senha, digite a senha da VPS NOVA!
scp backup_central_ai.sql root@184.107.88.20:/root/backup_central_ai.sql
ssh root@184.107.88.20 "sudo -u postgres psql central_agendamento_db < /root/backup_central_ai.sql"
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao restaurar na VPS nova.
    pause
    exit /b
)

echo.
color 0A
echo ===================================================
echo BANCO DE DADOS MIGRADO COM SUCESSO!
echo ===================================================
echo Agora todos os seus usuarios, lojas e senhas estao na VPS nova!
pause
