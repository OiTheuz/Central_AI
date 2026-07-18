@echo off
echo ==============================================
echo  Disparando mensagem para a Jessiely...
echo ==============================================
echo.
scp "C:\Users\MouTh\.gemini\antigravity-ide\brain\a775c2ad-84dd-41b2-9b5e-80c2262f13fe\scratch\solicitar_email_jessiely.py" root@184.107.88.20:/var/www/central_ai/solicitar_email_jessiely.py
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/python solicitar_email_jessiely.py"
echo.
echo Operacao concluida! Pressione qualquer tecla para fechar.
pause >nul
