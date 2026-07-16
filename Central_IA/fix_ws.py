#!/usr/bin/env python3
import os
import subprocess

print("Configuring WebSockets for all Nginx sites...")
conf_dir = "/etc/nginx/sites-available"

for filename in os.listdir(conf_dir):
    filepath = os.path.join(conf_dir, filename)
    if not os.path.isfile(filepath):
        continue
        
    with open(filepath, 'r') as f:
        content = f.read()
        
    if "proxy_pass" in content:
        print(f"Updating Nginx conf: {filepath}")
        if "proxy_set_header Upgrade" in content:
            print(f"WebSocket já configurado em {filepath}")
            continue
            
        # Find the first proxy_pass line and insert headers after it
        lines = content.split('\n')
        new_lines = []
        injected = False
        for line in lines:
            new_lines.append(line)
            if "proxy_pass" in line and not injected:
                new_lines.append('        # Websocket support')
                new_lines.append('        proxy_set_header Upgrade $http_upgrade;')
                new_lines.append('        proxy_set_header Connection "upgrade";')
                injected = True
                
        with open(filepath, 'w') as f:
            f.write('\n'.join(new_lines))
        print(f"WebSocket configurado em {filepath}")

print("Reloading Nginx and Central AI...")
subprocess.run(["systemctl", "daemon-reload"], check=True)
subprocess.run(["systemctl", "restart", "nginx"], check=True)
subprocess.run(["systemctl", "restart", "central_ai"], check=True)
print("Correções aplicadas com sucesso!")
