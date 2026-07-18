@echo off
echo ==============================================
echo  Buscando Conversa da Jessiely na VPS...
echo ==============================================
echo.
scp "C:\Users\MouTh\.gemini\antigravity-ide\brain\a775c2ad-84dd-41b2-9b5e-80c2262f13fe\scratch\ver_conversa.py" root@184.107.88.20:/var/www/central_ai/ver_conversa.py
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/python ver_conversa.py"
echo.
echo Operacao concluida! Pressione qualquer tecla para fechar.
pause >nul
