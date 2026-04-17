# 🗺️ Guia de Acesso - SaaS Igreja Inteligente

Este documento contém todos os links e credenciais para os ambientes de Produção (VPS) e Desenvolvimento (Local).

---

## 🚀 AMBIENTE DE PRODUÇÃO (VPS Google Cloud)
**IP do Servidor:** `35.224.87.100`

### ⛪ 1. Portal do Pastor (Dashboard Igreja)
*   **Link:** [http://35.224.87.100:8000/dashboard/index.html](http://35.224.87.100:8000/dashboard/index.html)
*   **Login:** `pastor@igreja.com.br`
*   **Senha:** `pastor123`

### 🏢 2. Painel Master (Administrador SaaS)
*   **Link:** [http://35.224.87.100:8000/dashboard/master.html](http://35.224.87.100:8000/dashboard/master.html)
*   **Login:** `admin@igreja.com.br`
*   **Senha:** `admin123`

### 🌐 3. Gerenciador de Domínios (Proxy Manager)
*   **Link:** [http://35.224.87.100:81](http://35.224.87.100:81)
*   **Login:** `admin@example.com`
*   **Senha Inicial:** `changeme`

### 🤖 4. WhatsApp API (Evolution Manager)
*   **Link:** [http://35.224.87.100:8080/manager](http://35.224.87.100:8080/manager)
*   **Global API Key:** `sua-apikey-global-12345`

---

## 💻 AMBIENTE LOCAL (Seu Computador)
**Atenção:** Certifique-se que o Docker Desktop está aberto.

### 🔗 Links Locais:
*   **Sistema:** [http://localhost:8000](http://localhost:8000)
*   **Proxy Manager:** [http://localhost:81](http://localhost:81)
*   **WhatsApp API:** [http://localhost:8080/manager](http://localhost:8080/manager)

### 🔑 Credenciais Locais:
*   As mesmas de produção, caso rode o script de setup localmente.

---

## 🛠️ COMANDOS ÚTEIS NA VPS (SSH)

*   **Atualizar Sistema:** `cd ~/Igreja-Inteligente && git pull origin main && sudo ./vps_deploy.sh`
*   **Ver Logs:** `sudo docker logs church_api -f`
*   **Reiniciar tudo:** `sudo docker-compose restart`
*   **Reset de Senhas/Setup:** `sudo docker exec -it church_api python setup_users.py`
