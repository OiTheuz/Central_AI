@echo off
cd /d "%~dp0"
color 0B
echo ===================================================
echo CONFIGURANDO ROTINAS DE LEMBRETES AUTOMATICOS NA VPS
echo ===================================================
echo Enviando scripts para a VPS...
scp "scripts\check_lembretes_pre.py" root@184.107.88.20:/var/www/central_ai/scripts/check_lembretes_pre.py
scp "scripts\check_lembretes_petshop.py" root@184.107.88.20:/var/www/central_ai/scripts/check_lembretes_petshop.py

echo.
echo Adicionando tarefas no Cron da VPS...
ssh root@184.107.88.20 "(crontab -l 2>/dev/null | grep -v check_lembretes ; echo '*/5 * * * * cd /var/www/central_ai && /var/www/central_ai/venv/bin/python scripts/check_lembretes_pre.py >> /var/log/lembretes_pre.log 2>&1' ; echo '0 * * * * cd /var/www/central_ai && /var/www/central_ai/venv/bin/python scripts/check_lembretes_petshop.py >> /var/log/lembretes_pos.log 2>&1') | crontab -"

echo.
color 0A
echo ===================================================
echo LEMBRETES CONFIGURADOS COM SUCESSO!
echo O robo vai verificar e enviar os lembretes a cada 5 min.
echo ===================================================
pause
