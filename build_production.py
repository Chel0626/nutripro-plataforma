#!/usr/bin/env python3
"""
Script de Build para Produção
Desenvolvido para NutriPro - Sistema de Gestão Nutricional

Este script prepara a aplicação para deploy em produção.
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    try:
        import flask
        import firebase_admin
        import google.auth
        import dotenv
        print("✅ Dependências principais verificadas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        return False

def create_production_env():
    """Cria arquivo .env para produção"""
    print("⚙️ Criando configuração de produção...")
    
    env_prod_content = """# .env.production - Variáveis para produção
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=CHANGE-THIS-IN-PRODUCTION-TO-SECURE-KEY

# Database Configuration
DATABASE_URL=sqlite:///nutripro.db
USE_FIREBASE=true

# Google Calendar API Configuration
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI=https://your-domain.com/oauth2callback

# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_CREDENTIALS={"type":"service_account",...}

# Email Configuration (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
"""
    
    with open('.env.production', 'w') as f:
        f.write(env_prod_content)
    
    print("✅ Arquivo .env.production criado")

def create_requirements_production():
    """Cria requirements.txt otimizado para produção"""
    print("📦 Criando requirements para produção...")
    
    # Requirements mínimas para produção
    prod_requirements = [
        "Flask>=3.0.0",
        "Flask-SQLAlchemy>=3.1.0",
        "Flask-WTF>=1.2.0",
        "WTForms>=3.1.0",
        "python-dotenv>=1.0.0",
        "firebase-admin>=6.2.0",
        "google-auth>=2.23.0",
        "google-auth-oauthlib>=1.1.0",
        "google-auth-httplib2>=0.1.1",
        "google-api-python-client>=2.100.0",
        "gunicorn>=21.2.0",  # Servidor WSGI para produção
        "psycopg2-binary>=2.9.7",  # Para PostgreSQL se necessário
    ]
    
    with open('requirements.production.txt', 'w') as f:
        for req in prod_requirements:
            f.write(f"{req}\n")
    
    print("✅ requirements.production.txt criado")

def create_dockerfile():
    """Cria Dockerfile para containerização"""
    print("🐳 Criando Dockerfile...")
    
    dockerfile_content = """# Dockerfile para NutriPro
FROM python:3.12-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements.production.txt .
RUN pip install --no-cache-dir -r requirements.production.txt

# Copia código da aplicação
COPY . .

# Cria diretório para dados
RUN mkdir -p /app/data

# Expõe porta
EXPOSE 5000

# Comando para iniciar aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Dockerfile criado")

def create_docker_compose():
    """Cria docker-compose.yml para desenvolvimento local"""
    print("🐳 Criando docker-compose.yml...")
    
    docker_compose_content = """version: '3.8'

services:
  nutripro:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./.env.production:/app/.env
    restart: unless-stopped
    
  # Opcional: adicione PostgreSQL se necessário
  # postgres:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: nutripro
  #     POSTGRES_USER: nutripro
  #     POSTGRES_PASSWORD: secure_password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

# volumes:
#   postgres_data:
"""
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose_content)
    
    print("✅ docker-compose.yml criado")

def create_vercel_config():
    """Cria configuração para deploy no Vercel"""
    print("▲ Criando configuração Vercel...")
    
    vercel_json = """{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  }
}"""
    
    with open('vercel.json', 'w') as f:
        f.write(vercel_json)
    
    print("✅ vercel.json criado")

def create_deploy_guide():
    """Cria guia de deploy"""
    print("📚 Criando guia de deploy...")
    
    guide_content = """# 🚀 Guia de Deploy - NutriPro

## Opções de Deploy

### 1. Vercel (Recomendado)
```bash
# Instalar Vercel CLI
npm i -g vercel

# Fazer deploy
vercel

# Configurar variáveis de ambiente no dashboard Vercel
```

### 2. Railway
```bash
# Conectar ao Railway
railway login
railway link

# Deploy
railway up
```

### 3. Heroku
```bash
# Criar app
heroku create nutripro-app

# Configurar variáveis
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
# ... outras variáveis

# Deploy
git push heroku main
```

### 4. Docker
```bash
# Build da imagem
docker build -t nutripro .

# Executar container
docker run -d -p 5000:5000 --env-file .env.production nutripro

# Ou usar docker-compose
docker-compose up -d
```

## Configurações Necessárias

### Variáveis de Ambiente
- Copie `.env.production` e configure:
  - `SECRET_KEY`: Chave secreta única
  - `GOOGLE_CLIENT_ID`: Do Google Cloud Console
  - `GOOGLE_CLIENT_SECRET`: Do Google Cloud Console
  - `FIREBASE_CREDENTIALS`: JSON do Firebase
  - `GOOGLE_REDIRECT_URI`: URL do seu domínio

### Firebase
- Atualize regras de segurança para produção
- Configure domínio autorizado

### Google Calendar
- Adicione domínio de produção nas URLs autorizadas

## Checklist de Deploy
- [ ] Configurar variáveis de ambiente
- [ ] Atualizar URLs de redirect
- [ ] Configurar regras Firebase para produção
- [ ] Testar funcionalidades principais
- [ ] Configurar monitoramento (opcional)

## Suporte
Em caso de problemas, verifique:
1. Logs da aplicação
2. Configuração das variáveis
3. Conectividade com Firebase
4. URLs de redirect do Google
"""
    
    with open('DEPLOY_GUIDE.md', 'w') as f:
        f.write(guide_content)
    
    print("✅ DEPLOY_GUIDE.md criado")

def run_tests():
    """Executa testes básicos"""
    print("🧪 Executando testes...")
    
    try:
        # Teste de importação
        from app import app
        with app.app_context():
            print("✅ App inicializa corretamente")
        
        # Teste Firebase
        from database_service import database_service
        info = database_service.get_database_info()
        print(f"✅ Database service: {info['mode']}")
        
        return True
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")
        return False

def main():
    """Função principal do build"""
    print("🏗️ INICIANDO BUILD DE PRODUÇÃO")
    print("=" * 50)
    
    start_time = datetime.now()
    
    # Verificações
    if not check_dependencies():
        print("❌ Build falhou: dependências faltando")
        return False
    
    # Criação de arquivos
    create_production_env()
    create_requirements_production()
    create_dockerfile()
    create_docker_compose()
    create_vercel_config()
    create_deploy_guide()
    
    # Testes
    if not run_tests():
        print("⚠️ Build concluído com avisos")
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n🎉 BUILD CONCLUÍDO!")
    print(f"⏱️ Tempo: {duration.total_seconds():.1f}s")
    print("\n📁 Arquivos criados:")
    print("  - .env.production")
    print("  - requirements.production.txt")
    print("  - Dockerfile")
    print("  - docker-compose.yml")
    print("  - vercel.json")
    print("  - DEPLOY_GUIDE.md")
    print("\n📖 Próximos passos:")
    print("  1. Leia DEPLOY_GUIDE.md")
    print("  2. Configure .env.production")
    print("  3. Escolha plataforma de deploy")
    print("  4. Siga as instruções no guia")
    
    return True

if __name__ == "__main__":
    main()