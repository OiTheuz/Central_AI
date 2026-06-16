#!/bin/bash
set -e

echo "========================================="
echo " Instalando e Configurando o Nginx "
echo "========================================="

echo "1. Instalando pacotes..."
DEBIAN_FRONTEND=noninteractive apt install -y nginx certbot python3-certbot-nginx

echo "2. Movendo arquivo de configuracao..."
mv /root/central_api.conf /etc/nginx/sites-available/central_api

echo "3. Criando link simbolico e limpando default..."
ln -sf /etc/nginx/sites-available/central_api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "4. Testando a sintaxe do Nginx..."
nginx -t

echo "5. Reiniciando o Nginx..."
systemctl restart nginx

echo "========================================="
echo " Proxy Reverso configurado com sucesso!"
echo " A API agora esta acessivel na porta 80."
echo " O proximo passo e rodar o Certbot."
echo "========================================="
