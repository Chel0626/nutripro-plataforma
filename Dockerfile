# Dockerfile para NutriPro
FROM python:3.12-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
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
