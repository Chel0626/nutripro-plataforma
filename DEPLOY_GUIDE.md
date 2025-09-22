# 🚀 Guia de Deploy - NutriPro

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
