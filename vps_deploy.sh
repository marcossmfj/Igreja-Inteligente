#!/bin/bash
# Script de deploy rápido para a VPS Google Cloud (35.224.87.100)

echo "🚀 Iniciando deploy na VPS..."

# 1. Garantir que o Docker e Docker Compose estão instalados
if ! command -v docker &> /dev/null
then
    echo "Docker não encontrado. Por favor, instale o Docker primeiro."
    exit
fi

# 2. Criar pastas de volumes se não existirem
mkdir -p assets/tenants
mkdir -p assets/cards
mkdir -p assets/birthdays

# 3. Copiar .env.example para .env se não existir
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️ Arquivo .env criado a partir do exemplo. Por favor, edite-o com suas senhas!"
fi

# 4. Derrubar containers antigos (se existirem) e subir novos
docker-compose down
docker-compose up --build -d

echo "✅ Sistema Rodando em: http://35.224.87.100:8000"
echo "✅ WhatsApp API em: http://35.224.87.100:8080"
echo "Use 'docker logs church_api -f' para acompanhar os logs."
