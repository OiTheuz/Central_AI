@echo off
cd /d "%~dp0"
color 0B
echo ===================================================
echo ATUALIZANDO BANCO DE DADOS DA VPS (Lembretes)
echo ===================================================
echo Enviando script de migracao para a VPS...
scp "scripts\migrar_lembrete_pre.py" root@184.107.88.20:/var/www/central_ai/scripts/migrar_lembrete_pre.py

echo.
echo Executando migracao no banco de dados da nuvem...
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/python scripts/migrar_lembrete_pre.py > migracao_log.txt 2>&1 ; systemctl restart central_ai"

echo.
color 0A
echo ===================================================
echo BANCO DE DADOS ATUALIZADO COM SUCESSO!
echo ===================================================
pause
