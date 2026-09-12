# AgroRisk Intelligence 🌾

**Sistema Inteligente de Prevenção à Inadimplência no Agronegócio**  
Hackathon PMI-DF 2026 × Krill Tech × IBM watsonx

---

## Visão Geral

O AgroRisk Intelligence é um sistema de análise de risco de crédito especializado no agronegócio
brasileiro. Ele realiza **due diligence automatizada** de clientes (produtores rurais e
agroindústrias) consultando fontes públicas e gera um **score 0–1000** com recomendações
de crédito e condições de pagamento.

### Farol de Risco

| Rating | Score | Decisão | Monitoramento |
|--------|-------|---------|---------------|
| 🟢 A — Verde   | 700–1000 | Aprovar — condições normais           | Quinzenal |
| 🟡 B — Amarelo | 400–699  | Aprovar com cautela — juros automáticos | Semanal  |
| 🟠 C — Laranja | 200–399  | Restringir — exigir garantias           | Diário   |
| 🔴 D — Vermelho| 0–199   | Não recomendar — risco crítico de RJ    | Diário   |

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                     AgroRisk Intelligence                        │
├───────────────────────┬─────────────────────────────────────────┤
│  Frontend (React)     │  Backend (FastAPI + Python)             │
│  ─────────────────    │  ──────────────────────────────         │
│  • Dashboard carteira │  • Agente de risco (IBM watsonx)        │
│  • Página de análise  │  • Coletores de dados públicos          │
│  • Chat assistente    │  • Motor de scoring multicamada         │
│    (IBM Bob/watsonx)  │  • Scheduler de monitoramento           │
└───────────────────────┴─────────────────────────────────────────┘

Fontes de dados:
  Cadastral   → ReceitaWS / Portal Redesim
  Jurídico    → DataJud (CNJ) — 11 tribunais agro
  Fiscal      → PGFN (dívida ativa), TST (CNDT)
  Ambiental   → IBAMA (embargos)
  Agro/Clima  → CONAB, ZARC/MAPA, INMET

IA:
  Relatório em linguagem natural → IBM watsonx Granite
  Chat assistente                → IBM watsonx Granite
```

---

## Como Rodar

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- (opcional) Docker

### Backend

```bash
cd agrorisk/backend

# Crie o arquivo .env a partir do exemplo
cp .env.example .env
# Edite .env com suas credenciais IBM watsonx (opcional para testes)

# Instale dependências
pip install -r requirements.txt

# Rode o servidor
uvicorn main:api_app --reload --port 8000
```

A API ficará disponível em `http://localhost:8000`  
Documentação Swagger: `http://localhost:8000/docs`

### Frontend

```bash
cd agrorisk/frontend

npm install
npm run dev
```

Dashboard em `http://localhost:5173`

### Docker (tudo junto)

```bash
cd agrorisk
docker-compose up --build
```

---

## Configuração IBM watsonx

1. Acesse [ibm.biz/watsonx-signup](https://www.ibm.com/watsonx)
2. Crie uma instância no IBM Cloud
3. Copie o API Key e o Project ID
4. Preencha no `.env`:

```
WATSONX_API_KEY=sua_chave_aqui
WATSONX_PROJECT_ID=seu_project_id_aqui
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

> O sistema funciona sem IBM watsonx — nesse caso usa resumos por template.

---

## Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/analyze` | Análise completa de risco por CNPJ |
| `GET`  | `/api/v1/analyze/{cnpj}` | Análise via GET |
| `POST` | `/api/v1/chat` | Chat com o assistente IA |
| `GET`  | `/api/v1/risk-levels` | Tabela de referência do farol |
| `GET`  | `/health` | Health check |

### Exemplo de uso

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"cnpj": "01.838.723/0001-27", "limite_solicitado": 100000}'
```

---

## Score Breakdown

O score total (0–1000) é dividido em 4 dimensões de 0 a 250 pontos cada:

| Dimensão | Peso | Critérios |
|----------|------|-----------|
| **Cadastral** | 250 | Situação CNPJ, tempo de atividade, capital social, CNAE |
| **Jurídico** | 250 | Processos DataJud, pedidos de RJ, execuções, protestos |
| **Fiscal** | 250 | Dívida ativa PGFN, CNDT irregular, FGTS |
| **Agro/Clima** | 250 | Embargo IBAMA, risco ZARC, produtividade CONAB, histórico climático |

---

## Sistema de Monitoramento Contínuo

O scheduler APScheduler roda automaticamente em background:

- **A cada 5 min** — analisa clientes recém-adicionados (sem rating ainda)
- **Diário** — reanálise de clientes C e D (alerta imediato)
- **Semanal** — reanálise de clientes B (amarelo)
- **Quinzenal** — reanálise de clientes A (verde)

Quando um cliente piora de rating ou ganha uma red flag crítica, o sistema dispara alertas.

---

## Estrutura do Projeto

```
agrorisk/
├── backend/
│   ├── agents/
│   │   └── risk_agent.py       # Orquestrador + IBM watsonx
│   ├── api/
│   │   └── routes.py           # FastAPI endpoints
│   ├── collectors/
│   │   ├── cadastral.py        # ReceitaWS
│   │   ├── juridical.py        # DataJud/CNJ
│   │   ├── fiscal.py           # PGFN, CNDT
│   │   └── agro_climate.py     # IBAMA, ZARC, CONAB
│   ├── models/
│   │   └── domain.py           # Modelos de domínio
│   ├── scoring/
│   │   └── engine.py           # Motor de scoring
│   ├── scheduler/
│   │   └── monitor.py          # Monitoramento contínuo
│   ├── config.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── AnalyzePage.tsx     # Análise individual
│       │   ├── PortfolioPage.tsx   # Carteira monitorada
│       │   └── ChatPage.tsx        # Assistente IA
│       ├── components/
│       │   └── RiskComponents.tsx  # RatingBadge, ScoreGauge, etc.
│       └── services/
│           └── api.ts              # Client HTTP
└── docker-compose.yml
```

---

## Equipe

Hackathon PMI-DF 2026 × Krill Tech  
Powered by IBM watsonx.ai · IBM Bob · IBM Granite
