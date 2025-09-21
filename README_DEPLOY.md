# 🥗 NutriPro - Plataforma de Nutrição Completa

## 🚀 Deploy Rápido

### Opção 1: Railway (Recomendado - Gratuito)

1. **Preparar repositório GitHub**:
   ```bash
   git add .
   git commit -m "Preparar aplicação para deploy"
   git push origin main
   ```

2. **Fazer deploy no Railway**:
   - Acesse [railway.app](https://railway.app)
   - Conecte sua conta GitHub
   - Clique em "New Project" → "Deploy from GitHub repo"
   - Selecione o repositório `nutripro-plataforma`
   - Railway detectará automaticamente que é uma aplicação Flask
   - Configure as variáveis de ambiente:
     - `SECRET_KEY`: uma chave secreta forte
     - `FLASK_ENV`: `production`

3. **Pronto!** Sua aplicação estará online em alguns minutos.

### Opção 2: Render (Alternativa Gratuita)

1. Acesse [render.com](https://render.com)
2. Conecte GitHub e selecione o repositório
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Environment**: Python 3
4. Adicione variáveis de ambiente:
   - `SECRET_KEY`: chave secreta
   - `FLASK_ENV`: `production`

### Opção 3: Heroku

1. Instale Heroku CLI
2. Execute:
   ```bash
   heroku create nutripro-app
   heroku config:set SECRET_KEY="sua-chave-secreta"
   heroku config:set FLASK_ENV="production"
   git push heroku main
   ```

## 🔧 Configuração Local

1. **Clone e configure**:
   ```bash
   git clone <repo-url>
   cd nutripro-plataforma
   pip install -r requirements.txt
   ```

2. **Configure variáveis**:
   ```bash
   cp .env.example .env
   # Edite .env com suas configurações
   ```

3. **Execute**:
   ```bash
   python app.py
   ```

## 📋 Funcionalidades

- ✅ **Gestão de Pacientes**: Cadastro completo com dados pessoais e objetivos
- ✅ **Cálculo de Calorias**: Baseado em fórmulas científicas (Harris-Benedict, Mifflin-St Jeor)
- ✅ **Distribuição de Macros**: Carboidratos, proteínas e gorduras por refeição
- ✅ **Banco de Alimentos TACO**: Mais de 3000 alimentos brasileiros
- ✅ **Planos Alimentares**: Geração automática com PDF profissional
- ✅ **Google Calendar**: Sincronização com Calendly para agendamentos
- ✅ **Consultas**: Gestão completa de atendimentos
- ✅ **Responsivo**: Interface adaptada para mobile e desktop

## 🔗 Integrações

### Google Calendar
- Sincronização automática com Calendly
- Associação inteligente de pacientes
- Gestão de consultas online

### Banco de Dados
- SQLite (desenvolvimento)
- PostgreSQL (produção)
- Migrations automáticas

## 📱 Acesso

Após o deploy, sua aplicação estará disponível 24/7 online e você poderá:
- Acessar de qualquer dispositivo
- Compartilhar com pacientes
- Trabalhar de forma colaborativa
- Ter backup automático na nuvem

## 🆘 Suporte

Problemas com deploy? Entre em contato!