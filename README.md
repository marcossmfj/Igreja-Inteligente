# ⛪ Igreja Inteligente - Sistema SaaS Multi-tenant

Uma plataforma moderna e automatizada para gestão de igrejas, com foco em inteligência de escalas, automação via WhatsApp e cuidado pastoral orientado a dados.

---

## 🚀 Principais Funcionalidades

- **🏢 Multi-tenancy (SaaS):** Um único servidor gerencia múltiplas igrejas, cada uma com seus próprios dados e configurações isolados.
- **🤖 Escalas com IA:** O sistema sugere e gera escalas automaticamente, respeitando as folgas dos membros e suas funções específicas.
- **📱 Integração com WhatsApp:**
  - Envio automático de convites para escalas.
  - Confirmação ou recusa via chat (o sistema atualiza o banco sozinho).
  - Cards de aniversário personalizados gerados e enviados pelo robô.
  - Boas-vindas automática para novos visitantes.
- **📊 Painel do Pastor:** Dashboard com métricas de crescimento, taxas de conversão de visitantes e alertas de "cuidado pastoral" (membros que faltam frequentemente).
- **🔒 Segurança Industrial:** Implementação de JWT para autenticação, controle de acessos por roles (Master, Admin, Membro) e banco de dados isolado.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python (FastAPI), SQLAlchemy (PostgreSQL/SQLite).
- **Frontend:** Vue.js 3, TailwindCSS (Modern Interface).
- **Automação:** Evolution API (WhatsApp), APScheduler.
- **Infraestrutura:** Docker, Docker Compose, Linux/VPS Support.
- **QA:** Pytest com Playwright para testes de interface ponta a ponta.

---

## 📦 Como Rodar Localmente (Desenvolvimento)

Para rodar este sistema, você precisará do **Docker Desktop** e do **Python** instalados.

1. **Clonar o Repositório:**
   ```bash
   git clone https://github.com/marcossmfj/Igreja-Inteligente.git
   cd Igreja-Inteligente
   ```

2. **Inicializar o Ambiente:**
   Execute o script de automação para subir os containers e injetar dados de teste:
   ```cmd
   .\Iniciar_Sistema.bat
   ```

3. **Acessar os Portais:**
   - **Painel Master (SaaS):** `http://localhost:8000/dashboard/master.html`
   - **Portal do Pastor:** `http://localhost:8000/dashboard/index.html`

---

## 🔒 Segurança e Privacidade

Este projeto foi desenvolvido com uma arquitetura de separação de segredos. Arquivos sensíveis de configuração (como `.env`, scripts de VPS e manuais de produção) não estão incluídos neste repositório por razões de segurança.

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).

---

*Desenvolvido por [Marcos Rodrigues](https://github.com/marcossmfj)*
