# 🚀 NutriPro - Resumo de Tecnologias

## 📌 Resposta Rápida

### **FRONT-END**
- **Versão Atual**: Jinja2 Templates + Bootstrap 5 + JavaScript Vanilla
- **Versão Nova**: Next.js 15 + React 19 + TypeScript + Tailwind CSS

### **BACK-END**  
- **Versão Atual**: Flask 3.1.1 (Python)
- **Versão Nova**: FastAPI (Python) + Go (microserviços)

### **BANCO DE DADOS**
- **Versão Atual**: SQLite 3
- **Versão Nova**: PostgreSQL (planejado)

---

## 🖥️ FRONT-END Detalhado

### Sistema Atual (Em Produção)

#### Tecnologias:
```
✅ Jinja2 - Template Engine (integrado ao Flask)
✅ Bootstrap 5.1.3 - Framework CSS
✅ Bootstrap Icons 1.8.1 - Ícones
✅ JavaScript Vanilla - Funcionalidades interativas
✅ Tom Select 2.2.2 - Autocomplete de alimentos
```

#### Arquivos JavaScript:
- `/static/js/plano_interativo.js` - Fluxo de prescrição
- `/static/js/distribuicao_macros.js` - Cálculos de macros

#### Características:
- Interface responsiva
- Design profissional
- Validação de formulários
- Autocomplete inteligente

---

### Nova Arquitetura (Em Desenvolvimento)

#### Tecnologias:
```
✅ Next.js 15.5.4 - Framework React
✅ React 19.1.0 - Biblioteca UI
✅ TypeScript 5 - Tipagem estática
✅ Tailwind CSS 4 - Framework CSS utility-first
✅ Turbopack - Build tool ultrarrápida
```

#### Localização:
- Diretório: `/frontend/`
- Tipo: SPA com SSR (Server-Side Rendering)

---

## ⚙️ BACK-END Detalhado

### Sistema Atual (Em Produção)

#### Framework:
```python
Flask 3.1.1 (Python 3.x)
Arquitetura: Monolítico MVC
```

#### Principais Bibliotecas:
```python
# Core
Flask 3.1.1              # Framework web
Flask-SQLAlchemy 3.1.1   # ORM
Flask-WTF 1.2.2          # Formulários
Flask-Migrate 4.1.0      # Migrações DB
Flask-Mail 0.10.0        # Emails

# Banco de Dados
SQLAlchemy 2.0.41        # ORM
Alembic 1.16.4           # Migrações

# Servidor
Waitress 3.0.2           # WSGI (produção)

# Utilidades
weasyprint 65.1          # Geração de PDF
pillow 11.2.1            # Imagens
python-dateutil 2.9.0    # Datas
```

#### APIs REST:
```
POST /api/calcular_calorias
POST /api/calcular_distribuicao
GET  /api/autocomplete_alimentos?q={query}
```

#### Funcionalidades:
1. ✅ CRUD de Pacientes
2. ✅ Planos Alimentares
3. ✅ Calculadora de Calorias (TMB)
4. ✅ Distribuição de Macros (automática/manual)
5. ✅ Sistema de Consultas
6. ✅ Banco de Alimentos (TACO - 597 itens)
7. ✅ Geração de PDFs
8. ✅ Autocomplete Inteligente

---

### Nova Arquitetura (Microserviços)

#### Serviços Planejados:

**1. Nutrition Service (Python/FastAPI)**
```python
Responsabilidade: Pacientes, planos, alimentos, consultas
Stack: FastAPI + SQLAlchemy + Pydantic + PostgreSQL
```

**2. Auth Service (Go)**
```go
Responsabilidade: Autenticação, autorização, auditoria LGPD
Stack: Gin + JWT + OAuth2 + PostgreSQL
Features: 2FA, rate limiting, logs de auditoria
```

**3. AI Service (Python)**
```python
Responsabilidade: IA, ML, recomendações
Stack: FastAPI + TensorFlow + OpenAI + scikit-learn
Features: Prescrição assistida, análise de fotos, NLP
```

**4. Payment Service (Python/Node.js)**
```
Responsabilidade: Pagamentos e NFe
```

**5. Video Service (Node.js)**
```
Responsabilidade: Videochamadas WebRTC
```

---

## 💾 BANCO DE DADOS Detalhado

### Sistema Atual

#### Tecnologia:
```
SGBD: SQLite 3
ORM: SQLAlchemy 2.0.41
Arquivo: instance/plataforma_nutri.db
```

#### Vantagens do SQLite:
✅ Banco embarcado (arquivo único)  
✅ Zero configuração  
✅ Portável (copiar .db = backup)  
✅ Rápido para pequeno/médio porte  
✅ Não requer servidor  
⚠️ Limitado em concorrência (ideal single-user)

#### Configuração:
```python
# Pode ser alterado via variável de ambiente
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'APP_DB_URI',
    'sqlite:///instance/plataforma_nutri.db'
)
```

#### Tabelas Principais:
```sql
paciente              # Dados do paciente
plano_alimentar       # Planos de dieta
refeicao              # Refeições do plano
item_refeicao         # Alimentos da refeição
alimento              # Banco de alimentos (TACO + custom)
consulta              # Agendamentos e histórico
```

#### Relacionamentos:
```
Paciente 1────N PlanoAlimentar
Paciente 1────N Consulta
PlanoAlimentar 1────N Refeicao
Refeicao 1────N ItemRefeicao
```

---

### Nova Arquitetura

#### Tecnologia:
```
SGBD: PostgreSQL
Estratégia: 1 banco por microserviço
Features: JSON nativo, ACID, escalável
```

#### Estrutura:
```
nutrition-db (PostgreSQL)
auth-db (PostgreSQL)
ai-db (PostgreSQL)
payment-db (PostgreSQL)
```

---

## 🏗️ ARQUITETURA

### Atual (Monolítica)

```
Cliente (Browser)
    ↓ HTTP
Servidor Waitress (WSGI)
    ↓
Flask 3.1.1
    ├─ Routes & Views (Jinja2)
    ├─ Business Logic
    ├─ Forms (WTForms)
    ├─ APIs REST
    └─ PDF Generation
    ↓
SQLAlchemy ORM
    ↓
SQLite Database
```

### Futura (Microserviços)

```
Frontend (Next.js + React)
    ↓ REST API
API Gateway
    ↓
┌─────┬─────┬─────┬─────┬─────┐
│Nutri│Auth │ AI  │Pay  │Video│
└──┬──┴──┬──┴──┬──┴──┬──┴──┬──┘
   │     │     │     │     │
   ▼     ▼     ▼     ▼     ▼
  PG    PG    PG    PG    PG
(PostgreSQL isolados)
```

---

## 📦 DISTRIBUIÇÃO

### Desktop App (Atual)
```
Ferramenta: PyInstaller 6.14.1
Plataforma: Windows
Formato: NutriPro.exe (executável standalone)
Inclui:
  - Python runtime
  - SQLite database
  - Templates e assets
  - Tabela TACO (597 alimentos)
```

---

## 🎯 COMPARAÇÃO DIRETA

| Aspecto | Versão Atual | Versão Futura |
|---------|--------------|---------------|
| **Frontend** | Jinja2 + Bootstrap + JS | Next.js + React + TypeScript |
| **UI Framework** | Bootstrap 5 | Tailwind CSS 4 |
| **Backend** | Flask (Python) | FastAPI + Go (microserviços) |
| **Banco de Dados** | SQLite | PostgreSQL |
| **Autenticação** | ❌ Não implementada | ✅ JWT + OAuth2 + 2FA |
| **Arquitetura** | Monolítica | Microserviços |
| **Escalabilidade** | Vertical (limitada) | Horizontal (cloud-ready) |
| **Deploy** | Executável Windows | Docker + Kubernetes |
| **IA/ML** | ❌ Não implementada | ✅ TensorFlow + OpenAI |

---

## 📊 DADOS

### Banco de Alimentos
```
Fonte: Tabela TACO (oficial)
Quantidade: 597 alimentos brasileiros
Informações: kcal, carboidratos, proteínas, gorduras (por 100g)
Customização: Adicionar alimentos próprios
```

---

## 🔐 SEGURANÇA

### Atual
```
✅ CSRF Protection (WTForms)
✅ Validação server-side
✅ Email validation
⚠️ Sem sistema de autenticação
```

### Futura
```
✅ JWT Tokens
✅ OAuth2
✅ 2FA (autenticação de dois fatores)
✅ Rate limiting
✅ Auditoria LGPD
✅ Criptografia de dados sensíveis
```

---

## 📝 CONCLUSÃO FINAL

### ✅ Stack Atual (Produção)
**Ideal para**: Aplicação desktop, uso individual/pequenas clínicas

```
Front: Jinja2 + Bootstrap 5 + JavaScript
Back:  Flask 3.1.1 (Python)
DB:    SQLite 3
```

### 🚀 Stack Futura (Em Desenvolvimento)
**Ideal para**: Aplicação web escalável, multi-tenant, cloud

```
Front: Next.js + React + TypeScript
Back:  FastAPI + Go (microserviços)
DB:    PostgreSQL
```

---

**📅 Data**: 2025-10-06  
**👨‍💻 Sistema**: NutriPro - Plataforma de Prescrição Nutricional  
**📍 Repositório**: https://github.com/Chel0626/nutripro-plataforma
