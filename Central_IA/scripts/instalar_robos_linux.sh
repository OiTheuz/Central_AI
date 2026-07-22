#!/bin/bash

echo "=========================================================="
echo " CONFIGURANDO AGENDADOR AUTOMATICO (LINUX/VPS)"
echo "=========================================================="

# Descobre automaticamente a pasta real do projeto na VPS
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Procura o arquivo python no ambiente virtual do linux (venv/bin/python)
PYTHON_EXEC="$PROJECT_DIR/venv/bin/python"

if [ ! -f "$PYTHON_EXEC" ]; then
    # Caso o ambiente virtual tenha outro nome ou não exista, usa o python3 global
    PYTHON_EXEC=$(which python3)
fi

echo "Pasta detectada: $PROJECT_DIR"
echo "Python que sera usado: $PYTHON_EXEC"
echo ""

# Cria os comandos que o Linux vai entender
CRON_JOB_1="0 8 * * * cd \"$PROJECT_DIR\" && \"$PYTHON_EXEC\" scripts/check_vencimentos.py >> \"$PROJECT_DIR/cron_vencimentos.log\" 2>&1"
CRON_JOB_2="5 8 * * * cd \"$PROJECT_DIR\" && \"$PYTHON_EXEC\" scripts/check_fim_trial.py >> \"$PROJECT_DIR/cron_trial.log\" 2>&1"

# Adiciona os robos no Crontab de forma silenciosa e limpa (sem sobrescrever os antigos se você tiver outros)
(crontab -l 2>/dev/null | grep -v "scripts/check_vencimentos.py" | grep -v "scripts/check_fim_trial.py"; echo "$CRON_JOB_1"; echo "$CRON_JOB_2") | crontab -

echo "=========================================================="
echo "✅ Tudo pronto! Os robos foram instalados com sucesso."
echo "-> Vencimento (10 dias): Todos os dias as 08:00 AM."
echo "-> Fim do Trial (7 dias): Todos os dias as 08:05 AM."
echo "=========================================================="
