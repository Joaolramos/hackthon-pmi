"""
Agente de Análise de Risco — IBM watsonx.ai + IBM Bob

Responsabilidades:
1. Orquestrar a coleta paralela de dados de todas as fontes
2. Invocar o motor de scoring
3. Gerar o relatório em linguagem natural via LLM (IBM granite)
4. Responder perguntas conversacionais sobre a carteira (IBM Bob)

Integração:
- ibm-watsonx-ai SDK (v0.0.5+): usa ibm_watson_machine_learning internamente
- Modelo: ibm/granite-13b-instruct-v2 (disponível no watsonx.ai)
- Documentação: https://ibm.github.io/watson-machine-learning-sdk/
"""
import asyncio
import structlog
from datetime import datetime
from typing import Optional

# A versão 0.0.5 do ibm-watsonx-ai usa WatsonMachineLearningAPIClient por baixo
try:
    from ibm_watson_machine_learning.foundation_models import Model as WMLModel
    from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
    _WML_AVAILABLE = True
except ImportError:
    _WML_AVAILABLE = False

from ..config import get_settings
from ..collectors.cadastral import fetch_cadastral
from ..collectors.juridical import fetch_juridical
from ..collectors.fiscal import fetch_fiscal
from ..collectors.agro_climate import fetch_environmental, fetch_agro_climate
from ..scoring.engine import calculate_score, generate_recommendation, get_monitoring_frequency
from ..models.domain import RiskReport, CadastralData

log = structlog.get_logger()
settings = get_settings()


# ---------------------------------------------------------------------------
# Cliente watsonx.ai — singleton lazy
# ---------------------------------------------------------------------------

_watsonx_client = None


def _get_watsonx_model():
    """
    Inicializa o cliente IBM watsonx.ai (ibm_watson_machine_learning).
    Retorna None se as credenciais não estiverem configuradas
    (permite rodar sem IBM em modo degradado durante dev).
    """
    global _watsonx_client
    if _watsonx_client is not None:
        return _watsonx_client

    if not _WML_AVAILABLE:
        log.warning("watsonx.not_available", reason="ibm_watson_machine_learning não instalado")
        return None

    if not settings.watsonx_api_key or settings.watsonx_api_key == "your_ibm_api_key_here":
        log.warning("watsonx.not_configured", reason="API key não definida — modo sem LLM")
        return None

    try:
        wml_credentials = {
            "url": settings.watsonx_url,
            "apikey": settings.watsonx_api_key,
        }
        _watsonx_client = WMLModel(
            model_id="ibm/granite-13b-instruct-v2",
            credentials=wml_credentials,
            project_id=settings.watsonx_project_id,
            params={
                GenParams.MAX_NEW_TOKENS: 800,
                GenParams.TEMPERATURE: 0.3,       # baixo para análise factual
                GenParams.REPETITION_PENALTY: 1.1,
            },
        )
        log.info("watsonx.initialized", model="granite-13b-instruct-v2")
        return _watsonx_client
    except Exception as e:
        log.error("watsonx.init_error", error=str(e))
        return None


# ---------------------------------------------------------------------------
# Prompt engineering para o relatório de risco
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Você é o AgroRisk Assistant, um especialista em análise de risco de crédito 
no agronegócio brasileiro. Você analisa dados de empresas rurais e produtores e gera relatórios 
claros, objetivos e em linguagem acessível para analistas de crédito da Krill Tech.

Suas respostas devem:
- Ser diretas e objetivas (sem juridiquês desnecessário)
- Destacar os riscos mais importantes primeiro
- Sempre lembrar que a decisão final é do analista humano
- Usar o sistema de farol: 🟢 Verde (A) / 🟡 Amarelo (B) / 🟠 Laranja (C) / 🔴 Vermelho (D)
- Ter no máximo 300 palavras para o resumo executivo"""


def _build_report_prompt(report: RiskReport) -> str:
    """Constrói o prompt para geração do resumo executivo em linguagem natural."""
    score = report.score
    rec = report.recomendacao
    flags_text = "\n".join(
        f"  [{f.severidade}] {f.descricao}" for f in report.red_flags[:5]
    ) or "  Nenhum red flag crítico identificado."

    nivel_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴"}.get(score.risk_level.value, "⚪")

    prompt = f"""{SYSTEM_PROMPT}

---

Gere um RESUMO EXECUTIVO de risco de crédito para o seguinte cliente:

**Empresa:** {report.razao_social}
**CNPJ:** {report.cnpj}
**Data da análise:** {report.analisado_em.strftime('%d/%m/%Y %H:%M')}

**SCORE GERAL:** {score.total}/1000 — Rating {nivel_emoji} {score.risk_level.value}

**Breakdown do Score:**
- Cadastral:         {score.cadastral}/250
- Jurídico:          {score.juridico}/250
- Fiscal:            {score.fiscal}/250
- Agro/Climático:    {score.agro_climate}/250

**Principais Red Flags:**
{flags_text}

**Dados de Localização:** {report.cadastral.municipio}/{report.cadastral.uf}
**Risco Climático (ZARC):** {report.agro_climate.risco_climatico_zarc}
**Situação Cadastral:** {report.cadastral.situacao_cadastral}
**Processos Judiciais:** {report.juridico.total_processos} (execuções: {report.juridico.processos_execucao}, RJ: {report.juridico.pedidos_rj})
**Dívida Ativa PGFN:** {"SIM" if report.fiscal.divida_ativa_federal else "NÃO"}

**Recomendação do sistema:**
- Aprovado: {"SIM" if rec and rec.aprovado else "NÃO"}
- Limite sugerido: R$ {rec.limite_credito_sugerido:,.2f if rec else 0:,.2f}
- Condições: {rec.condicoes_pagamento if rec else "N/A"}

Escreva o resumo executivo em 3 parágrafos:
1. Situação geral da empresa e rating
2. Principais riscos identificados
3. Recomendação clara para o analista

"""
    return prompt


# ---------------------------------------------------------------------------
# Agente principal — orquestrador completo
# ---------------------------------------------------------------------------

async def analyze_client(cnpj: str, limite_solicitado: Optional[float] = None) -> RiskReport:
    """
    Pipeline completo de análise de risco para um CNPJ.
    
    Etapas:
    1. Coleta paralela de dados cadastrais + jurídicos + fiscais
    2. Coleta de dados agronômicos/climáticos baseada na localização
    3. Cálculo do score multicamada
    4. Geração de recomendação de crédito
    5. Geração do resumo executivo via LLM (watsonx Granite)
    
    Retorna RiskReport completo.
    """
    log.info("agent.analyze_start", cnpj=cnpj)
    start = datetime.now()

    # -------------------------------------------------------------------------
    # ETAPA 1: Coleta paralela (cadastral + jurídico + fiscal em simultâneo)
    # -------------------------------------------------------------------------
    cadastral_task = fetch_cadastral(cnpj)
    juridical_task = fetch_juridical(cnpj)
    fiscal_task    = fetch_fiscal(cnpj)

    cadastral, juridical, fiscal = await asyncio.gather(
        cadastral_task, juridical_task, fiscal_task,
        return_exceptions=False,
    )

    # -------------------------------------------------------------------------
    # ETAPA 2: Dados ambientais e agro/climáticos (dependem da localização)
    # -------------------------------------------------------------------------
    uf       = cadastral.uf or "MT"       # fallback: MT (maior produtor)
    municipio = cadastral.municipio or ""

    environmental, agro_climate = await asyncio.gather(
        fetch_environmental(cnpj, uf, municipio),
        fetch_agro_climate(municipio, uf),
    )

    # -------------------------------------------------------------------------
    # ETAPA 3: Score e recomendação
    # -------------------------------------------------------------------------
    score, red_flags = calculate_score(cadastral, juridical, fiscal, environmental, agro_climate)
    recomendacao = generate_recommendation(score, red_flags, cadastral.capital_social, limite_solicitado)
    monitoring_freq = get_monitoring_frequency(score)

    # -------------------------------------------------------------------------
    # ETAPA 4: Montagem do relatório
    # -------------------------------------------------------------------------
    report = RiskReport(
        cnpj=cnpj.replace(".", "").replace("/", "").replace("-", ""),
        razao_social=cadastral.razao_social or "Empresa não identificada",
        analisado_em=datetime.now(),
        cadastral=cadastral,
        juridico=juridical,
        fiscal=fiscal,
        ambiental=environmental,
        agro_climate=agro_climate,
        score=score,
        red_flags=red_flags,
        recomendacao=recomendacao,
        monitoring_frequency=monitoring_freq,
    )

    # -------------------------------------------------------------------------
    # ETAPA 5: Resumo executivo via LLM (IBM watsonx Granite)
    # -------------------------------------------------------------------------
    report.resumo_executivo = await _generate_executive_summary(report)

    elapsed = (datetime.now() - start).total_seconds()
    log.info(
        "agent.analyze_done",
        cnpj=cnpj,
        score=score.total,
        rating=score.risk_level.value,
        elapsed_s=round(elapsed, 2),
    )

    return report


async def _generate_executive_summary(report: RiskReport) -> str:
    """
    Gera o resumo executivo em linguagem natural usando IBM watsonx Granite.
    Se o LLM não estiver disponível, gera um resumo template como fallback.
    """
    model = _get_watsonx_model()

    if model is None:
        return _generate_fallback_summary(report)

    try:
        prompt = _build_report_prompt(report)
        # WMLModel.generate_text é síncrono — executa em thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_text(prompt)
        )
        if isinstance(response, dict):
            response = response.get("results", [{}])[0].get("generated_text", "")
        return str(response).strip()

    except Exception as e:
        log.error("watsonx.generate_error", error=str(e))
        return _generate_fallback_summary(report)


def _generate_fallback_summary(report: RiskReport) -> str:
    """
    Resumo executivo gerado por template quando o LLM não está disponível.
    Garante que o sistema funcione mesmo sem credenciais IBM configuradas.
    """
    score = report.score
    nivel_map = {
        "A": "🟢 BAIXO RISCO",
        "B": "🟡 RISCO MODERADO",
        "C": "🟠 RISCO ELEVADO",
        "D": "🔴 RISCO CRÍTICO",
    }
    nivel_texto = nivel_map.get(score.risk_level.value, "⚪ INDETERMINADO")
    flags_criticas = [f for f in report.red_flags if f.severidade == "CRITICA"]

    linhas = [
        f"**{report.razao_social}** (CNPJ: {report.cnpj}) — Rating {nivel_texto}",
        f"Score consolidado: {score.total}/1000 | Análise realizada em {report.analisado_em.strftime('%d/%m/%Y às %H:%M')}",
        "",
        f"A empresa apresenta situação cadastral **{report.cadastral.situacao_cadastral}**, "
        f"com {report.juridico.total_processos} processo(s) judicial(is) identificado(s), "
        f"sendo {report.juridico.pedidos_rj} pedido(s) de Recuperação Judicial.",
        "",
    ]

    if flags_criticas:
        linhas.append("**⚠️ Alertas Críticos:**")
        for f in flags_criticas:
            linhas.append(f"- {f.descricao}")
        linhas.append("")

    rec = report.recomendacao
    if rec:
        status = "**APROVADO**" if rec.aprovado else "**NÃO RECOMENDADO**"
        linhas.append(
            f"Recomendação do sistema: {status} | "
            f"Limite sugerido: R$ {rec.limite_credito_sugerido:,.2f} | "
            f"Prazo máximo: {rec.prazo_maximo_dias} dias."
        )
        linhas.append(f"Condições: {rec.condicoes_pagamento}")

    linhas.append("")
    linhas.append("*A decisão final é do analista de crédito responsável.*")

    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Interface conversacional para IBM Bob
# ---------------------------------------------------------------------------

async def ask_agent(question: str, context: Optional[dict] = None) -> str:
    """
    Interface conversacional — responde perguntas sobre risco de crédito.
    Usada pelo IBM Bob para interação via chat no dashboard.
    
    Exemplos de perguntas:
    - "Qual o risco do cliente CNPJ 12.345.678/0001-90?"
    - "Quais clientes da carteira estão em alerta esta semana?"
    - "O que significa rating C para condições de pagamento?"
    """
    model = _get_watsonx_model()

    context_text = ""
    if context:
        context_text = f"\n\nContexto atual:\n{context}"

    prompt = f"""{SYSTEM_PROMPT}

{context_text}

Pergunta do analista: {question}

Responda de forma clara, direta e em até 200 palavras:"""

    if model is None:
        return (
            "⚠️ O assistente IA não está disponível no momento "
            "(credenciais IBM watsonx não configuradas). "
            "Por favor, consulte os dados diretamente no dashboard."
        )

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_text(prompt)
        )
        if isinstance(response, dict):
            response = response.get("results", [{}])[0].get("generated_text", "")
        return str(response).strip()
    except Exception as e:
        log.error("watsonx.ask_error", error=str(e))
        return f"Erro ao consultar o assistente: {str(e)}"
