# 📊 Análise Completa de Tecnologias do Sistema NutriPro

## 🎯 Resumo Executivo

O **NutriPro** é uma plataforma de prescrição nutricional que utiliza uma arquitetura híbrida, combinando uma aplicação monolítica principal (Flask) com uma arquitetura de microserviços em desenvolvimento (nutripro-v2).

---

## 🖥️ FRONT-END

### **Versão Atual (Produção)**

#### **Stack Principal**
- **Templates Engine**: Jinja2 (integrado com Flask)
- **Framework CSS**: Bootstrap 5.1.3
- **Ícones**: Bootstrap Icons 1.8.1
- **JavaScript Vanilla**: Para funcionalidades interativas
- **Biblioteca de Autocomplete**: Tom Select 2.2.2
  - Usado para seleção de alimentos com busca
  - Interface moderna com suporte a Bootstrap 5

#### **Recursos do Front-End**
```html
<!-- Estrutura típica dos templates -->
Base.html
├── Bootstrap 5.1.3 (CSS Framework)
├── Bootstrap Icons (Ícones)
├── Tom Select (Autocomplete/Select)
└── JavaScript customizado (plano_interativo.js, distribuicao_macros.js)
```

#### **Arquivos JavaScript Principais**
1. **`/static/js/plano_interativo.js`**
   - Gerencia o fluxo interativo de prescrição
   - Calculadora de calorias
   - Distribuição de macronutrientes
   - Autocomplete de alimentos
   
2. **`/static/js/distribuicao_macros.js`**
   - Cálculos de distribuição de macros
   - Ajustes manuais e automáticos
   - Validações de porcentagens

#### **Características**
- ✅ Interface responsiva com Bootstrap
- ✅ Design limpo e profissional
- ✅ Experiência de usuário fluida
- ✅ Suporte a formulários dinâmicos
- ✅ Validação client-side e server-side

---

### **Nova Arquitetura (Em Desenvolvimento)**

#### **Stack Moderna**
```json
{
  "framework": "Next.js 15.5.4",
  "linguagem": "TypeScript 5",
  "biblioteca_ui": "React 19.1.0",
  "estilização": "Tailwind CSS 4",
  "build_tool": "Turbopack (Next.js)"
}
```

#### **Localização**
- **Diretório**: `/frontend/`
- **Tipo**: Single Page Application (SPA) com Server-Side Rendering (SSR)

#### **Recursos Avançados**
- ✅ TypeScript para type safety
- ✅ Tailwind CSS para estilização utility-first
- ✅ React 19 com hooks modernos
- ✅ Next.js 15 com App Router
- ✅ Turbopack para builds ultrarrápidos
- ✅ ESLint para qualidade de código

#### **Estrutura do Projeto Frontend**
```
frontend/
├── src/
│   ├── app/          # App Router (Next.js)
│   └── components/   # Componentes React reutilizáveis
├── public/           # Assets estáticos
├── package.json
└── tsconfig.json
```

---

## ⚙️ BACK-END

### **Versão Atual (Produção)**

#### **Framework e Linguagem**
- **Framework**: Flask 3.1.1 (Python)
- **Linguagem**: Python 3.x
- **Arquitetura**: Monolítico com padrão MVC

#### **Bibliotecas e Dependências Principais**

##### **Core Framework**
```python
Flask==3.1.1              # Web framework
Flask-SQLAlchemy==3.1.1   # ORM para banco de dados
Flask-WTF==1.2.2          # Formulários com validação
Flask-Migrate==4.1.0      # Migrações de banco de dados
Flask-Mail==0.10.0        # Sistema de e-mail
```

##### **Banco de Dados e ORM**
```python
SQLAlchemy==2.0.41        # ORM principal
Alembic==1.16.4          # Ferramenta de migração
```

##### **Validação e Formulários**
```python
WTForms==3.2.1           # Criação e validação de forms
email_validator==2.2.0   # Validação de emails
```

##### **Servidor de Produção**
```python
Waitress==3.0.2          # WSGI server (Windows-friendly)
```

##### **Geração de PDFs**
```python
weasyprint==65.1         # Conversão HTML → PDF
pillow==11.2.1           # Processamento de imagens
```

##### **Utilitários**
```python
python-dateutil==2.9.0   # Manipulação de datas
python-slugify==8.0.4    # Geração de slugs
python-dotenv==1.1.0     # Variáveis de ambiente
```

#### **Estrutura do Backend**
```
Backend (Flask)
├── app.py                # Aplicação principal
├── run.py               # Script de inicialização
├── models.py            # Modelos do banco (vazio, definidos em app.py)
├── forms.py             # Formulários WTForms (vazio, definidos em app.py)
├── calculadoras.py      # Lógica de cálculos nutricionais
├── taco_data.py         # Dados da tabela TACO (597 alimentos)
└── import_taco.py       # Script de importação de alimentos
```

#### **APIs REST Disponíveis**
```python
# APIs de Cálculo
POST /api/calcular_calorias
POST /api/calcular_distribuicao

# API de Autocomplete
GET /api/autocomplete_alimentos?q={query}
```

#### **Funcionalidades Backend**
1. **Gestão de Pacientes** (CRUD completo)
2. **Planos Alimentares** (criação, edição, visualização)
3. **Calculadora de Calorias** (TMB + fator de atividade)
4. **Distribuição de Macronutrientes** (automática e manual)
5. **Sistema de Consultas** (agendamento e histórico)
6. **Banco de Alimentos** (TACO + alimentos customizados)
7. **Geração de PDFs** (exportação de planos)
8. **Autocomplete Inteligente** (busca de alimentos)

---

### **Nova Arquitetura (Microserviços - Em Desenvolvimento)**

#### **Nutrition Service** (Python/FastAPI)
```python
{
  "framework": "FastAPI",
  "orm": "SQLAlchemy",
  "validacao": "Pydantic",
  "responsabilidade": [
    "Gestão de pacientes",
    "Planos alimentares",
    "Alimentos e consultas"
  ]
}
```

#### **Auth Service** (Go)
```go
{
  "framework": "Gin",
  "autenticacao": "JWT + OAuth2",
  "features": [
    "2FA",
    "Rate limiting",
    "Logs de auditoria LGPD"
  ]
}
```

#### **AI Service** (Python)
```python
{
  "framework": "FastAPI",
  "ml_libs": ["TensorFlow", "OpenAI", "scikit-learn"],
  "features": [
    "Prescrição assistida por IA",
    "Análise de fotos de alimentos",
    "Processamento de linguagem natural (NLP)"
  ]
}
```

#### **Payment Service** (Python/Node.js)
- Gestão de pagamentos
- Emissão de Notas Fiscais Eletrônicas (NFe)

#### **Video Service** (Node.js)
- Videochamadas com WebRTC
- Teleconsultas em tempo real

---

## 💾 BANCO DE DADOS

### **Versão Atual (Produção)**

#### **Tecnologia**
- **SGBD**: SQLite 3
- **ORM**: SQLAlchemy 2.0.41
- **Localização padrão**: `instance/plataforma_nutri.db`

#### **Configuração**
```python
# Configuração em app.py
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'APP_DB_URI', 
    f'sqlite:///{default_db_path}'
)
```

#### **Características do SQLite**
- ✅ Banco de dados embarcado (arquivo único)
- ✅ Zero configuração (ideal para distribuição desktop)
- ✅ Portável (copia o arquivo .db = backup completo)
- ✅ Rápido para aplicações de pequeno a médio porte
- ✅ Não requer servidor de banco de dados
- ⚠️ Limitações em concorrência (adequado para uso single-user)

#### **Suporte Futuro**
O sistema foi projetado para facilmente migrar para PostgreSQL ou MySQL através da variável de ambiente `APP_DB_URI`:
```bash
# Exemplo de migração para PostgreSQL
export APP_DB_URI="postgresql://user:pass@localhost/nutripro"
```

---

### **Schema do Banco de Dados**

#### **Tabelas Principais**

##### **1. Paciente**
```sql
CREATE TABLE paciente (
    id INTEGER PRIMARY KEY,
    nome_completo VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    data_nascimento DATE,
    peso FLOAT,
    altura_cm INTEGER,
    sexo VARCHAR(20),
    observacoes TEXT,
    data_cadastro DATETIME NOT NULL
);
```

##### **2. PlanoAlimentar**
```sql
CREATE TABLE plano_alimentar (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    nome_plano VARCHAR(150) NOT NULL,
    objetivo_calorico_final INTEGER,
    orientacoes_diabetes TEXT,
    orientacoes_nutricao TEXT,
    data_criacao DATETIME NOT NULL
);
```

##### **3. Refeicao**
```sql
CREATE TABLE refeicao (
    id INTEGER PRIMARY KEY,
    plano_id INTEGER NOT NULL REFERENCES plano_alimentar(id),
    nome_refeicao VARCHAR(100) NOT NULL,
    meta_carboidratos_g FLOAT,
    meta_proteinas_g FLOAT,
    meta_gorduras_g FLOAT
);
```

##### **4. ItemRefeicao**
```sql
CREATE TABLE item_refeicao (
    id INTEGER PRIMARY KEY,
    refeicao_id INTEGER NOT NULL REFERENCES refeicao(id),
    nome_alimento VARCHAR(200) NOT NULL,
    marca_alimento VARCHAR(150),
    quantidade_g FLOAT NOT NULL,
    medida_caseira VARCHAR(100),
    substituicoes TEXT,
    carboidratos_g FLOAT NOT NULL,
    proteinas_g FLOAT NOT NULL,
    gorduras_g FLOAT NOT NULL,
    kcal INTEGER NOT NULL
);
```

##### **5. Alimento**
```sql
CREATE TABLE alimento (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    marca VARCHAR(150),
    kcal_100g FLOAT NOT NULL,
    carboidratos_100g FLOAT NOT NULL,
    proteinas_100g FLOAT NOT NULL,
    gorduras_100g FLOAT NOT NULL,
    origem VARCHAR(50) DEFAULT 'manual'
);
CREATE INDEX idx_alimento_nome ON alimento(nome);
```

##### **6. Consulta**
```sql
CREATE TABLE consulta (
    id INTEGER PRIMARY KEY,
    data_hora DATETIME NOT NULL,
    tipo_consulta VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'Agendada',
    observacoes_nutri TEXT,
    link_videochamada VARCHAR(255),
    data_criacao DATETIME NOT NULL,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id)
);
```

#### **Relacionamentos**
```
Paciente 1──────N PlanoAlimentar
Paciente 1──────N Consulta
PlanoAlimentar 1──────N Refeicao
Refeicao 1──────N ItemRefeicao
```

---

### **Nova Arquitetura (Microserviços)**

#### **SGBD Planejado**
- **PostgreSQL** (principal)
  - Um banco por serviço (isolamento de dados)
  - Suporte a JSON nativo
  - Melhor para escalabilidade
  - ACID compliant

#### **Estrutura**
```
Microserviços
├── nutrition-db (PostgreSQL)
├── auth-db (PostgreSQL)
├── ai-db (PostgreSQL)
└── payment-db (PostgreSQL)
```

---

## 🏗️ ARQUITETURA GERAL

### **Versão Atual**

```
┌─────────────────────────────────────────┐
│         CLIENTE (Navegador)             │
│  HTML + Bootstrap + JavaScript          │
└─────────────┬───────────────────────────┘
              │ HTTP/HTTPS
┌─────────────▼───────────────────────────┐
│      SERVIDOR (Waitress WSGI)           │
│                                          │
│  ┌────────────────────────────────┐    │
│  │      Flask 3.1.1 (Python)      │    │
│  │                                 │    │
│  │  ├─ Routes & Views (Jinja2)    │    │
│  │  ├─ Business Logic             │    │
│  │  ├─ Forms (WTForms)            │    │
│  │  ├─ APIs REST                  │    │
│  │  └─ PDF Generation             │    │
│  └──────────┬─────────────────────┘    │
│             │                            │
│  ┌──────────▼─────────────────────┐    │
│  │  SQLAlchemy ORM                │    │
│  └──────────┬─────────────────────┘    │
└─────────────┼───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│     SQLite Database                     │
│  (instance/plataforma_nutri.db)         │
└─────────────────────────────────────────┘
```

---

### **Nova Arquitetura (Microserviços)**

```
┌──────────────────────────────────────────────────┐
│         FRONTEND (Next.js + React)               │
│         TypeScript + Tailwind CSS                │
└────────┬─────────────────────────────────────────┘
         │ REST API / GraphQL
         ▼
┌──────────────────────────────────────────────────┐
│              API Gateway                         │
└───┬────┬────┬────┬────┬───────────────────────────┘
    │    │    │    │    │
    ▼    ▼    ▼    ▼    ▼
┌────┐ ┌───┐ ┌──┐ ┌────┐ ┌─────┐
│Nutr│ │Auth│ │AI│ │Pay │ │Video│
│ion │ │    │ │  │ │ment│ │     │
└─┬──┘ └─┬─┘ └┬─┘ └──┬─┘ └──┬──┘
  │      │    │      │      │
  ▼      ▼    ▼      ▼      ▼
┌──┐   ┌──┐ ┌──┐  ┌──┐   ┌──┐
│PG│   │PG│ │PG│  │PG│   │PG│
└──┘   └──┘ └──┘  └──┘   └──┘
PostgreSQL Databases (isolados)
```

---

## 📦 DISTRIBUIÇÃO E DEPLOYMENT

### **Desktop Application**
- **Empacotamento**: PyInstaller 6.14.1
- **Plataforma**: Windows (executável standalone)
- **Recursos incluídos**: 
  - Python runtime embarcado
  - Banco de dados SQLite
  - Templates e assets
  - Tabela TACO (597 alimentos)

### **Configurações de Build**
```python
# NutriPro.spec (PyInstaller)
- Modo: windowed (sem console)
- Ícone: icone.ico
- Dados incluídos: templates/, static/, taco_data.py
- Nome: NutriPro.exe
```

---

## 🔒 SEGURANÇA

### **Versão Atual**
- ✅ WTForms com proteção CSRF
- ✅ Validação server-side
- ✅ Secret key configurável
- ✅ Email validation
- ⚠️ Sem autenticação/autorização implementada

### **Nova Arquitetura**
- ✅ JWT tokens
- ✅ OAuth2
- ✅ Autenticação de dois fatores (2FA)
- ✅ Rate limiting
- ✅ Logs de auditoria (compliance LGPD)
- ✅ Criptografia de dados sensíveis

---

## 📊 DADOS E INTEGRAÇÕES

### **Banco de Alimentos**
- **Fonte**: Tabela TACO (Tabela Brasileira de Composição de Alimentos)
- **Quantidade**: 597 alimentos pré-cadastrados
- **Campos**: Nome, kcal, carboidratos, proteínas, gorduras (por 100g)
- **Customização**: Usuário pode adicionar alimentos próprios

### **Integrações Planejadas**
- 🔄 Firebase (autenticação e storage)
- 🔄 APIs de IA (OpenAI para prescrições assistidas)
- 🔄 Gateway de pagamento
- 🔄 Sistema de NFe

---

## 🎓 PADRÕES E BOAS PRÁTICAS

### **Backend**
- ✅ Padrão MVC (Model-View-Controller)
- ✅ ORM para abstração de banco de dados
- ✅ Migrações de banco versionadas (Alembic)
- ✅ Separação de concerns (calculadoras.py, forms.py)
- ✅ Logging estruturado
- ✅ Variáveis de ambiente para configuração

### **Frontend**
- ✅ Progressive Enhancement
- ✅ Responsividade mobile-first (Bootstrap)
- ✅ Validação client-side + server-side
- ✅ UX fluida com feedback ao usuário
- ✅ TypeScript para type safety (novo frontend)

---

## 📈 ESCALABILIDADE

### **Limitações Atuais**
- SQLite: Adequado para 1-10 usuários simultâneos
- Monólito: Escalabilidade vertical limitada
- Sem cache implementado

### **Melhorias Planejadas**
- PostgreSQL: Milhares de conexões simultâneas
- Microserviços: Escalabilidade horizontal
- Redis: Cache de sessões e queries frequentes
- CDN: Assets estáticos
- Docker/Kubernetes: Orquestração de containers

---

## 🔧 FERRAMENTAS DE DESENVOLVIMENTO

### **Backend**
```bash
Python 3.x
Flask CLI
Alembic (migrações)
PyInstaller (builds)
Waitress (servidor WSGI)
```

### **Frontend Moderno**
```bash
Node.js + npm
Next.js CLI
TypeScript Compiler
ESLint (linting)
Turbopack (bundling)
```

### **Controle de Versão**
- Git
- GitHub (repositório remoto)

---

## 📝 CONCLUSÃO

O **NutriPro** utiliza uma stack sólida e moderna, combinando:

### **✅ Pontos Fortes**
1. **Backend robusto** com Flask e SQLAlchemy
2. **Frontend responsivo** com Bootstrap
3. **Banco de dados simples** e portável (SQLite)
4. **Fácil distribuição** como executável Windows
5. **Base de alimentos completa** (TACO)
6. **Arquitetura evolutiva** (migração para microserviços em andamento)

### **🔄 Em Desenvolvimento**
1. Frontend moderno com Next.js + TypeScript
2. Arquitetura de microserviços
3. Autenticação e autorização robustas
4. Features de IA para prescrições assistidas
5. Teleconsultas com WebRTC

### **🎯 Stack Resumida**

| Camada | Tecnologia Atual | Tecnologia Futura |
|--------|------------------|-------------------|
| **Frontend** | Jinja2 + Bootstrap 5 + JS | Next.js + React + TypeScript |
| **Backend** | Flask 3.1.1 (Python) | FastAPI + Go (microserviços) |
| **Banco de Dados** | SQLite 3 | PostgreSQL |
| **ORM** | SQLAlchemy 2.0.41 | SQLAlchemy + Pydantic |
| **Servidor** | Waitress (WSGI) | Uvicorn/Gunicorn |
| **Autenticação** | Não implementada | JWT + OAuth2 + 2FA |
| **Deploy** | PyInstaller (exe) | Docker + Kubernetes |

---

**Data da Análise**: 2025-10-06  
**Versão do Sistema**: 1.0 (Monolito) + 2.0 (Microserviços - em desenvolvimento)
