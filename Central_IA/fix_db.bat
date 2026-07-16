@echo off
echo ===================================================
echo CORRIGINDO BANCO DE DADOS NA PRODUCAO E DESTRAVANDO CHAT
echo ===================================================
echo [1/2] Enviando script para a nuvem...
scp reset_remote.py root@184.107.88.20:/var/www/central_ai/

echo [2/2] Executando reset na nuvem...
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/python reset_remote.py && systemctl restart central_ai"
echo.
echo ===================================================
echo FEITO! TABELAS CRIADAS E CHAT DESTRAVADO!
echo ===================================================
pause
