@echo off
echo ===================================================
echo APAGANDO LOJAS DE TESTE NO SERVIDOR DE PRODUCAO
echo ===================================================
echo.
echo [1/2] Enviando script para a nuvem...
scp C:\Users\MouTh\.gemini\antigravity-ide\brain\a775c2ad-84dd-41b2-9b5e-80c2262f13fe\scratch\delete_remote.py root@184.107.88.20:/var/www/central_ai/delete_remote.py
echo.
echo [2/2] Executando delecao na nuvem...
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/python delete_remote.py"
echo.
echo ===================================================
echo DELECAO CONCLUIDA COM SUCESSO!
echo ===================================================
pause
