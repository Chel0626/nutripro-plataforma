#!/bin/bash

echo "🚀 Iniciando NutriPro V2..."

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
fi

# Fazer build dos serviços
echo "🔨 Fazendo build dos serviços..."
docker-compose build

# Iniciar os serviços
echo "🚀 Iniciando serviços..."
docker-compose up -d postgres redis

# Aguardar postgres estar pronto
echo "⏳ Aguardando PostgreSQL..."
until docker-compose exec postgres pg_isready -U nutripro -d nutripro_nutrition; do
    sleep 2
done

# Iniciar serviços da aplicação
echo "🚀 Iniciando aplicação..."
docker-compose up -d

echo "✅ NutriPro V2 iniciado com sucesso!"
echo ""
echo "🌐 Acesse a aplicação:"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8001/docs"
echo "   API: http://localhost:8001/api/v1"
echo ""
echo "📊 Para verificar logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para parar a aplicação:"
echo "   docker-compose down"