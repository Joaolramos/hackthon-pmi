"""
API REST — AgroRisk Intelligence
Endpoints para análise de risco, gestão de carteira e monitoramento.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import structlog

from ..agents.risk_agent import analyze_client, ask_agent
from ..models.domain import RiskReport, RiskLevel

log = structlog.get_logger()

app = FastAPI(
    title="AgroRisk Intelligence API",
    description="Sistema Inteligente de Prevenção à Inadimplência no Agronegócio — Krill Tech",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # em produção: restringir ao domínio do dashboard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Schemas de entrada/saída (Pydantic v2)
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    cnpj: str = Field(..., example="12.345.678/0001-90", description="CNPJ ou CPF do cliente")
    limite_solicitado: Optional[float] = Field(None, description="Valor solicitado em R$ (opcional)")

class AnalyzeResponse(BaseModel):
    cnpj: str
    razao_social: str
    score_total: int
    rating: str                 # A / B / C / D
    rating_label: str           # Verde / Amarelo / Laranja / Vermelho
    aprovado: bool
    limite_sugerido: float
    condicoes_pagamento: str
    prazo_maximo_dias: int
    exige_garantia: bool
    tipo_cobranca: str
    red_flags: list[dict]
    score_breakdown: dict
    resumo_executivo: str
    monitoring_frequency: str
    analisado_em: str

class ChatRequest(BaseModel):
    question: str
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    answer: str

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RATING_LABELS = {
    "A": "🟢 Verde — Baixo Risco",
    "B": "🟡 Amarelo — Risco Moderado",
    "C": "🟠 Laranja — Risco Elevado",
    "D": "🔴 Vermelho — Risco Crítico",
}


def _report_to_response(report: RiskReport) -> AnalyzeResponse:
    """Converte RiskReport (domínio) para AnalyzeResponse (API)."""
    rec = report.recomendacao
    return AnalyzeResponse(
        cnpj=report.cnpj,
        razao_social=report.razao_social,
        score_total=report.score.total,
        rating=report.score.risk_level.value,
        rating_label=RATING_LABELS.get(report.score.risk_level.value, "⚪ Indeterminado"),
        aprovado=rec.aprovado if rec else False,
        limite_sugerido=rec.limite_credito_sugerido if rec else 0.0,
        condicoes_pagamento=rec.condicoes_pagamento if rec else "",
        prazo_maximo_dias=rec.prazo_maximo_dias if rec else 0,
        exige_garantia=rec.exige_garantia if rec else False,
        tipo_cobranca=rec.tipo_cobranca if rec else "normal",
        red_flags=[
            {"codigo": f.codigo, "descricao": f.descricao, "severidade": f.severidade}
            for f in report.red_flags
        ],
        score_breakdown={
            "cadastral": report.score.cadastral,
            "juridico": report.score.juridico,
            "fiscal": report.score.fiscal,
            "agro_climate": report.score.agro_climate,
            "total": report.score.total,
        },
        resumo_executivo=report.resumo_executivo,
        monitoring_frequency=report.monitoring_frequency.value,
        analisado_em=report.analisado_em.isoformat(),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Health check — verifica se a API está no ar."""
    return {"status": "ok", "service": "AgroRisk Intelligence"}


@app.post("/api/v1/analyze", response_model=AnalyzeResponse, tags=["Análise de Risco"])
async def analyze(request: AnalyzeRequest):
    """
    **Análise completa de risco de crédito para um CNPJ.**
    
    Pipeline:
    1. Due diligence cadastral (Receita Federal)
    2. Verificação jurídica (DataJud/CNJ)
    3. Verificação fiscal (PGFN, CNDT)
    4. Risco ambiental (IBAMA) e agronômico (ZARC/CONAB)
    5. Score 0–1000 com farol A/B/C/D
    6. Recomendação de crédito e condições de pagamento
    7. Resumo executivo em linguagem natural (IBM watsonx Granite)
    """
    log.info("api.analyze", cnpj=request.cnpj)
    
    try:
        report = await analyze_client(request.cnpj, request.limite_solicitado)
        return _report_to_response(report)
    except Exception as e:
        log.error("api.analyze_error", cnpj=request.cnpj, error=str(e))
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@app.get("/api/v1/analyze/{cnpj}", response_model=AnalyzeResponse, tags=["Análise de Risco"])
async def analyze_get(cnpj: str, limite_solicitado: Optional[float] = None):
    """
    Análise de risco via GET (conveniente para chamadas diretas).
    O CNPJ pode ser enviado com ou sem formatação.
    """
    return await analyze(AnalyzeRequest(cnpj=cnpj, limite_solicitado=limite_solicitado))


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Assistente IA"])
async def chat(request: ChatRequest):
    """
    **Interface conversacional com o Assistente AgroRisk (IBM Bob/watsonx).**
    
    Exemplos de perguntas:
    - "Qual o risco do cliente CNPJ 12.345.678/0001-90?"
    - "O que significa rating C para condições de pagamento?"
    - "Quais red flags são mais críticas no agronegócio?"
    """
    try:
        answer = await ask_agent(request.question, request.context)
        return ChatResponse(answer=answer)
    except Exception as e:
        log.error("api.chat_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risk-levels", tags=["Referência"])
async def risk_levels():
    """Retorna a tabela de referência do sistema de farol de risco."""
    return {
        "levels": [
            {
                "rating": "A",
                "label": "Verde — Baixo Risco",
                "score_range": "700–1000",
                "recomendacao": "Aprovar em condições normais",
                "monitoring": "Quinzenal",
                "emoji": "🟢",
            },
            {
                "rating": "B",
                "label": "Amarelo — Risco Moderado",
                "score_range": "400–699",
                "recomendacao": "Aprovar com condições ajustadas (juros automáticos, prazo reduzido)",
                "monitoring": "Semanal",
                "emoji": "🟡",
            },
            {
                "rating": "C",
                "label": "Laranja — Risco Elevado",
                "score_range": "200–399",
                "recomendacao": "Restringir — exigir garantias reais e entrada mínima de 30%",
                "monitoring": "Diário com alerta imediato",
                "emoji": "🟠",
            },
            {
                "rating": "D",
                "label": "Vermelho — Risco Crítico",
                "score_range": "0–199",
                "recomendacao": "Não recomendar venda a prazo — risco iminente de RJ/inadimplência",
                "monitoring": "Diário com alerta imediato",
                "emoji": "🔴",
            },
        ]
    }
