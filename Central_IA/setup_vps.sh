#!/bin/bash
set -e

echo "========================================="
echo " Preparando a VPS para a Central de IA "
echo "========================================="

echo "1. Atualizando pacotes..."
apt update && DEBIAN_FRONTEND=noninteractive apt upgrade -y

echo "2. Instalando python, git e postgresql..."
DEBIAN_FRONTEND=noninteractive apt install -y python3 python3-pip python3-venv git postgresql postgresql-contrib

echo "3. Iniciando e habilitando PostgreSQL..."
systemctl start postgresql || true
systemctl enable postgresql || true

echo "4. Criando banco de dados..."
sudo -u postgres psql -c "CREATE DATABASE central_agendamento_db;" || echo "Banco já existe ou ocorreu um erro não fatal."
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '134001';" || true

echo "5. Preparando pasta do projeto..."
mkdir -p /var/www/central_ai
cd /var/www/central_ai
python3 -m venv venv

echo "========================================="
echo " VPS Preparada com Sucesso!"
echo " A pasta /var/www/central_ai foi criada."
echo " O ambiente virtual (venv) está pronto."
echo " O banco de dados PostgreSQL está rodando."
echo "========================================="
