@echo off
scp check_remote.py root@184.107.88.20:/var/www/central_ai/
ssh root@184.107.88.20 "cd /var/www/central_ai && venv/bin/python check_remote.py"
pause
