# NutriPro V2 - Arquitetura de Microserviços

## 🏗️ Estrutura da Arquitetura

```
nutripro-v2/
├── services/
│   ├── nutrition-service/     # Core: Pacientes, planos, alimentos (Python/FastAPI)
│   ├── auth-service/          # Autenticação e autorização (Go)
│   ├── ai-service/           # IA e Machine Learning (Python)
│   ├── payment-service/      # Pagamentos e NFe (Python/Node.js)
│   └── video-service/        # Videochamadas WebRTC (Node.js)
├── frontend/                 # React/Next.js + TypeScript
├── mobile/                   # React Native (futuro)
├── shared/                   # Tipos, configs e utilitários compartilhados
├── infrastructure/           # Docker, K8s, CI/CD
└── docs/                     # Documentação técnica
```

## 🚀 Tecnologias por Serviço

### Nutrition Service (Python/FastAPI)
- **Responsabilidade**: Gestão de pacientes, planos alimentares, alimentos, consultas
- **Stack**: FastAPI + SQLAlchemy + Pydantic + PostgreSQL
- **Migração**: Todo código atual Flask convertido

### Auth Service (Go)
- **Responsabilidade**: Autenticação, autorização, auditoria LGPD
- **Stack**: Gin + JWT + OAuth2 + PostgreSQL
- **Features**: 2FA, rate limiting, logs de auditoria

### AI Service (Python)
- **Responsabilidade**: Modelos ML, recomendações, análise de dados
- **Stack**: FastAPI + TensorFlow + OpenAI + scikit-learn
- **Features**: Prescrição assistida, análise de fotos, NLP

## 📋 Status da Migração

- [x] Estrutura base criada
- [ ] Nutrition Service (em andamento)
- [ ] Frontend React
- [ ] Auth Service
- [ ] AI Service
- [ ] Infraestrutura Docker

## 🏃‍♂️ Como Executar

```bash
# Development
docker-compose up -d

# Production
kubectl apply -f infrastructure/k8s/
```