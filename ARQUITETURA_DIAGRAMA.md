# 🏗️ Diagrama de Arquitetura - NutriPro

## 📊 ARQUITETURA ATUAL (Monolítica - Em Produção)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                     CAMADA DE APRESENTAÇÃO                  ┃
┃  ┌────────────────────────────────────────────────────┐   ┃
┃  │         BROWSER (Cliente Web)                      │   ┃
┃  │                                                      │   ┃
┃  │  HTML5 + CSS3 (Bootstrap 5.1.3)                    │   ┃
┃  │  JavaScript (Vanilla + Tom Select 2.2.2)           │   ┃
┃  │  Bootstrap Icons 1.8.1                             │   ┃
┃  │                                                      │   ┃
┃  │  Templates Jinja2:                                 │   ┃
┃  │  • base.html                                       │   ┃
┃  │  • plano_formulario.html                           │   ┃
┃  │  • distribuicao_macros.html                        │   ┃
┃  │  • paciente_detalhe.html                           │   ┃
┃  └─────────────────┬──────────────────────────────────┘   ┃
┗━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                      │
                      │ HTTP/HTTPS
                      │ (Requests/Responses)
                      ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    CAMADA DE APLICAÇÃO                      ┃
┃  ┌────────────────────────────────────────────────────┐   ┃
┃  │        Waitress WSGI Server (3.0.2)                │   ┃
┃  │        Porta: 5000                                 │   ┃
┃  │        Host: 127.0.0.1                             │   ┃
┃  └─────────────────┬──────────────────────────────────┘   ┃
┃                    │                                        ┃
┃  ┌─────────────────▼──────────────────────────────────┐   ┃
┃  │              Flask Application 3.1.1               │   ┃
┃  │                    (Python)                        │   ┃
┃  │                                                      │   ┃
┃  │  ┌─────────────────────────────────────────────┐  │   ┃
┃  │  │          ROTAS & CONTROLLERS               │  │   ┃
┃  │  │                                              │  │   ┃
┃  │  │  • / (home)                                 │  │   ┃
┃  │  │  • /pacientes                               │  │   ┃
┃  │  │  • /planos                                  │  │   ┃
┃  │  │  • /consultas                               │  │   ┃
┃  │  │  • /ferramentas/calculadora_calorias       │  │   ┃
┃  │  │  • /ferramentas/distribuicao_macros        │  │   ┃
┃  │  │  • /api/calcular_calorias                  │  │   ┃
┃  │  │  • /api/calcular_distribuicao              │  │   ┃
┃  │  │  • /api/autocomplete_alimentos             │  │   ┃
┃  │  └─────────────────────────────────────────────┘  │   ┃
┃  │                                                      │   ┃
┃  │  ┌─────────────────────────────────────────────┐  │   ┃
┃  │  │          LÓGICA DE NEGÓCIO                 │  │   ┃
┃  │  │                                              │  │   ┃
┃  │  │  • calculadoras.py                          │  │   ┃
┃  │  │    - calcular_necessidade_calorica()       │  │   ┃
┃  │  │    - distribuir_macros_nas_refeicoes()     │  │   ┃
┃  │  │    - calcular_macros_por_porcentagem()     │  │   ┃
┃  │  │                                              │  │   ┃
┃  │  │  • forms.py (WTForms)                       │  │   ┃
┃  │  │    - PacienteForm                           │  │   ┃
┃  │  │    - ConsultaForm                           │  │   ┃
┃  │  │    - DistribuicaoMacrosForm                 │  │   ┃
┃  │  │                                              │  │   ┃
┃  │  │  • taco_data.py                             │  │   ┃
┃  │  │    - DADOS_TACO (597 alimentos)            │  │   ┃
┃  │  └─────────────────────────────────────────────┘  │   ┃
┃  │                                                      │   ┃
┃  │  ┌─────────────────────────────────────────────┐  │   ┃
┃  │  │          EXTENSÕES FLASK                   │  │   ┃
┃  │  │                                              │  │   ┃
┃  │  │  • Flask-SQLAlchemy (ORM)                  │  │   ┃
┃  │  │  • Flask-WTF (Formulários)                 │  │   ┃
┃  │  │  • Flask-Migrate (Migrações DB)            │  │   ┃
┃  │  │  • Flask-Mail (Emails)                     │  │   ┃
┃  │  │  • WeasyPrint (PDFs)                       │  │   ┃
┃  │  └─────────────────────────────────────────────┘  │   ┃
┃  └─────────────────┬──────────────────────────────────┘   ┃
┗━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                      │
                      │ SQLAlchemy ORM
                      ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    CAMADA DE DADOS                          ┃
┃  ┌────────────────────────────────────────────────────┐   ┃
┃  │           SQLAlchemy 2.0.41 (ORM)                  │   ┃
┃  │                                                      │   ┃
┃  │  Modelos:                                          │   ┃
┃  │  • Paciente                                        │   ┃
┃  │  • PlanoAlimentar                                  │   ┃
┃  │  • Refeicao                                        │   ┃
┃  │  • ItemRefeicao                                    │   ┃
┃  │  • Alimento                                        │   ┃
┃  │  • Consulta                                        │   ┃
┃  └─────────────────┬──────────────────────────────────┘   ┃
┃                    │                                        ┃
┃  ┌─────────────────▼──────────────────────────────────┐   ┃
┃  │              SQLite 3 Database                     │   ┃
┃  │                                                      │   ┃
┃  │  Arquivo: instance/plataforma_nutri.db             │   ┃
┃  │                                                      │   ┃
┃  │  Tabelas:                                          │   ┃
┃  │  ├─ paciente                                       │   ┃
┃  │  ├─ plano_alimentar                                │   ┃
┃  │  ├─ refeicao                                       │   ┃
┃  │  ├─ item_refeicao                                  │   ┃
┃  │  ├─ alimento                                       │   ┃
┃  │  └─ consulta                                       │   ┃
┃  │                                                      │   ┃
┃  │  Características:                                  │   ┃
┃  │  ✓ Embarcado (arquivo único)                      │   ┃
┃  │  ✓ Zero configuração                              │   ┃
┃  │  ✓ Portável                                       │   ┃
┃  │  ✓ ACID compliant                                 │   ┃
┃  └────────────────────────────────────────────────────┘   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🚀 ARQUITETURA FUTURA (Microserviços - Em Desenvolvimento)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                        CAMADA DE APRESENTAÇÃO                         ┃
┃  ┌──────────────────────────────────────────────────────────────┐   ┃
┃  │              Next.js 15 + React 19 (TypeScript)              │   ┃
┃  │                                                                │   ┃
┃  │  • SSR (Server-Side Rendering)                               │   ┃
┃  │  • CSR (Client-Side Rendering)                               │   ┃
┃  │  • Tailwind CSS 4                                            │   ┃
┃  │  • Turbopack (Build Tool)                                    │   ┃
┃  │                                                                │   ┃
┃  │  Diretório: /frontend/                                       │   ┃
┃  └────────────────────────┬─────────────────────────────────────┘   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                             │
                             │ REST API / GraphQL
                             │ JSON over HTTPS
                             ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                         API GATEWAY                                  ┃
┃  ┌──────────────────────────────────────────────────────────────┐   ┃
┃  │  • Roteamento de requisições                                 │   ┃
┃  │  • Load Balancing                                            │   ┃
┃  │  • Rate Limiting                                             │   ┃
┃  │  • Authentication/Authorization                              │   ┃
┃  │  • API Versioning                                            │   ┃
┃  └──────┬───────┬───────┬───────┬───────┬──────────────────────┘   ┃
┗━━━━━━━━━┿━━━━━━━┿━━━━━━━┿━━━━━━━┿━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━┛
           │       │       │       │       │
           ▼       ▼       ▼       ▼       ▼
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                      CAMADA DE MICROSERVIÇOS                         ┃
┃                                                                        ┃
┃  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               ┃
┃  │   NUTRITION  │  │     AUTH     │  │      AI      │               ┃
┃  │   SERVICE    │  │   SERVICE    │  │   SERVICE    │               ┃
┃  ├──────────────┤  ├──────────────┤  ├──────────────┤               ┃
┃  │ FastAPI      │  │ Go (Gin)     │  │ FastAPI      │               ┃
┃  │ SQLAlchemy   │  │ JWT/OAuth2   │  │ TensorFlow   │               ┃
┃  │ Pydantic     │  │ 2FA          │  │ OpenAI       │               ┃
┃  │              │  │ Rate Limit   │  │ scikit-learn │               ┃
┃  │ Endpoints:   │  │              │  │              │               ┃
┃  │ • Pacientes  │  │ Endpoints:   │  │ Endpoints:   │               ┃
┃  │ • Planos     │  │ • /login     │  │ • /predict   │               ┃
┃  │ • Alimentos  │  │ • /register  │  │ • /analyze   │               ┃
┃  │ • Consultas  │  │ • /verify    │  │ • /suggest   │               ┃
┃  │ • Cálculos   │  │ • /audit     │  │ • /nlp       │               ┃
┃  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               ┃
┃         │                 │                 │                        ┃
┃         ▼                 ▼                 ▼                        ┃
┃  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               ┃
┃  │ PostgreSQL   │  │ PostgreSQL   │  │ PostgreSQL   │               ┃
┃  │ nutrition_db │  │  auth_db     │  │   ai_db      │               ┃
┃  └──────────────┘  └──────────────┘  └──────────────┘               ┃
┃                                                                        ┃
┃  ┌──────────────┐  ┌──────────────┐                                  ┃
┃  │   PAYMENT    │  │    VIDEO     │                                  ┃
┃  │   SERVICE    │  │   SERVICE    │                                  ┃
┃  ├──────────────┤  ├──────────────┤                                  ┃
┃  │ Python/Node  │  │ Node.js      │                                  ┃
┃  │ Stripe API   │  │ WebRTC       │                                  ┃
┃  │ NFe          │  │ Socket.io    │                                  ┃
┃  │              │  │              │                                  ┃
┃  │ Endpoints:   │  │ Endpoints:   │                                  ┃
┃  │ • /checkout  │  │ • /call      │                                  ┃
┃  │ • /invoice   │  │ • /room      │                                  ┃
┃  │ • /webhook   │  │ • /stream    │                                  ┃
┃  └──────┬───────┘  └──────┬───────┘                                  ┃
┃         │                 │                                           ┃
┃         ▼                 ▼                                           ┃
┃  ┌──────────────┐  ┌──────────────┐                                  ┃
┃  │ PostgreSQL   │  │ PostgreSQL   │                                  ┃
┃  │ payment_db   │  │  video_db    │                                  ┃
┃  └──────────────┘  └──────────────┘                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 📊 FLUXO DE DADOS - Arquitetura Atual

```
┌─────────────────────────────────────────────────────────────┐
│                   FLUXO: Nova Prescrição                    │
└─────────────────────────────────────────────────────────────┘

1. USUÁRIO ACESSA /planos/novo/<paciente_id>
   │
   ▼
2. FLASK RENDERIZA plano_formulario.html (Jinja2)
   │
   ▼
3. JAVASCRIPT CARREGA:
   ├─ plano_interativo.js
   └─ Inicializa Tom Select para autocomplete
   │
   ▼
4. USUÁRIO PREENCHE DADOS DO PACIENTE
   │
   ▼
5. CLICK "Calcular Calorias" → POST /api/calcular_calorias
   │
   ├─ Backend: calcular_necessidade_calorica()
   │   └─ Retorna: { kcal_manutencao, kcal_objetivo }
   │
   └─ Frontend: Exibe resultado e preenche campo
   │
   ▼
6. USUÁRIO DEFINE DISTRIBUIÇÃO DE MACROS
   ├─ Porcentagens: Carboidratos, Proteínas, Gorduras
   ├─ Número de refeições grandes/pequenas
   └─ Click "Calcular Distribuição"
   │
   ▼
7. POST /api/calcular_distribuicao
   │
   ├─ Backend: calcular_macros_por_porcentagem()
   ├─ Backend: distribuir_macros_nas_refeicoes()
   │   └─ Retorna: { distribuicao por refeição }
   │
   └─ Frontend: Renderiza tabela de distribuição
   │
   ▼
8. USUÁRIO AJUSTA VALORES MANUALMENTE
   ├─ Toggle redistribuição automática
   └─ Click "Finalizar e Prosseguir"
   │
   ▼
9. FRONTEND RENDERIZA REFEIÇÕES DETALHADAS
   │
   ▼
10. USUÁRIO ADICIONA ALIMENTOS (para cada refeição)
    │
    ├─ Digita no campo → GET /api/autocomplete_alimentos?q=arroz
    │   │
    │   ├─ Backend busca em: DADOS_TACO + Alimento table
    │   └─ Retorna: [{ id, nome, marca, macros }]
    │
    ├─ Seleciona alimento do autocomplete
    ├─ Define quantidade
    └─ JavaScript calcula macros automaticamente
    │
    ▼
11. USUÁRIO FINALIZA PLANO
    │
    └─ Click "Salvar Plano" → POST /salvar_plano
        │
        ├─ Backend constrói objeto PlanoAlimentar
        ├─ Cria Refeicoes e ItemRefeicao
        ├─ db.session.add() + db.session.commit()
        ├─ Gera PDF com WeasyPrint
        ├─ Salva JSON em /data/paciente_X/
        │
        └─ Redirect: /planos/<plano_id>
```

---

## 🔄 RELACIONAMENTOS DO BANCO DE DADOS

```
┌─────────────────────┐
│      Paciente       │
│ ─────────────────── │
│ • id (PK)           │
│ • nome_completo     │
│ • email (UNIQUE)    │
│ • telefone          │
│ • data_nascimento   │
│ • peso              │
│ • altura_cm         │
│ • sexo              │
│ • observacoes       │
└──────┬──────────┬───┘
       │          │
       │ 1        │ 1
       │          │
       │ N        │ N
       ▼          ▼
┌─────────────┐ ┌─────────────┐
│PlanoAlimentar│ │   Consulta  │
│─────────────│ │─────────────│
│• id (PK)    │ │• id (PK)    │
│• paciente_id│ │• paciente_id│
│  (FK)       │ │  (FK)       │
│• nome_plano │ │• data_hora  │
│• objetivo_  │ │• tipo       │
│  calorico   │ │• status     │
│• orientacoes│ │• observacoes│
└──────┬──────┘ └─────────────┘
       │
       │ 1
       │
       │ N
       ▼
┌─────────────┐
│  Refeicao   │
│─────────────│
│• id (PK)    │
│• plano_id   │
│  (FK)       │
│• nome       │
│  _refeicao  │
│• meta_carb  │
│• meta_prot  │
│• meta_gord  │
└──────┬──────┘
       │
       │ 1
       │
       │ N
       ▼
┌─────────────┐
│ItemRefeicao │
│─────────────│
│• id (PK)    │
│• refeicao_id│
│  (FK)       │
│• nome       │
│  _alimento  │
│• marca      │
│• quantidade │
│  _g         │
│• medida     │
│  _caseira   │
│• carboidr.  │
│• proteinas  │
│• gorduras   │
│• kcal       │
└─────────────┘

┌─────────────┐
│  Alimento   │  (Tabela independente)
│─────────────│
│• id (PK)    │
│• nome       │
│• marca      │
│• kcal_100g  │
│• carb_100g  │
│• prot_100g  │
│• gord_100g  │
│• origem     │  ('TACO' ou 'manual')
└─────────────┘
```

---

## 📦 DEPLOYMENT - Executável Windows

```
┌─────────────────────────────────────────────────┐
│         PyInstaller Build Process               │
└─────────────────────────────────────────────────┘

app.py + dependencies
    │
    │ PyInstaller 6.14.1
    ▼
┌─────────────────────────────────┐
│       NutriPro.exe              │
│ ─────────────────────────────── │
│                                 │
│  Embedded:                      │
│  ├─ Python 3.x Runtime          │
│  ├─ Flask + dependências        │
│  ├─ SQLite engine               │
│  ├─ Templates (Jinja2)          │
│  ├─ Static files (CSS/JS)       │
│  ├─ taco_data.py (597 foods)    │
│  └─ icone.ico                   │
│                                 │
│  External (runtime):            │
│  ├─ instance/                   │
│  │   └─ plataforma_nutri.db    │
│  └─ data/                       │
│      └─ paciente_X/             │
│          ├─ paciente.json       │
│          ├─ plano_1.json        │
│          └─ plano_1.html        │
└─────────────────────────────────┘
    │
    │ Execução
    ▼
Waitress Server → http://127.0.0.1:5000
Browser abre automaticamente
```

---

**📅 Última Atualização**: 2025-10-06  
**📍 Repositório**: https://github.com/Chel0626/nutripro-plataforma
