import os
import subprocess

NGINX_CONF = "/etc/nginx/sites-available/central_api"
DOMAIN = "api.openchatz.com.br"
EMAIL = "contato@openchatz.com.br"

def setup_nginx():
    print(f"Configurando Nginx para o domínio {DOMAIN}...")
    
    if not os.path.exists(NGINX_CONF):
        print(f"Erro: Arquivo {NGINX_CONF} não encontrado.")
        return

    with open(NGINX_CONF, "r") as f:
        content = f.read()

    # Atualiza o server_name se necessário
    if "server_name" in content:
        # Substitui a linha do server_name atual
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith("server_name"):
                lines[i] = f"    server_name {DOMAIN};"
        new_content = '\n'.join(lines)
    else:
        new_content = content.replace("listen 80;", f"listen 80;\n    server_name {DOMAIN};")

    with open(NGINX_CONF, "w") as f:
        f.write(new_content)
    
    print("Arquivo Nginx atualizado com sucesso.")

    print("Reiniciando Nginx...")
    subprocess.run(["systemctl", "reload", "nginx"], check=True)

    print(f"Gerando Certificado SSL (HTTPS) para {DOMAIN} usando Certbot...")
    # Executa o certbot
    certbot_cmd = [
        "certbot", "--nginx", 
        "-d", DOMAIN, 
        "--non-interactive", 
        "--agree-tos", 
        "-m", EMAIL,
        "--redirect"
    ]
    try:
        subprocess.run(certbot_cmd, check=True)
        print("Certificado SSL gerado com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao gerar SSL: {e}")
        print("Tente rodar manualmente: certbot --nginx -d api.openchatz.com.br")

if __name__ == "__main__":
    setup_nginx()
