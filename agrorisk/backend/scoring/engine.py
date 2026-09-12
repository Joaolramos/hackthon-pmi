"""
Motor de Scoring Multicamada — AgroRisk Intelligence

Score total: 0 a 1000 pontos
Dividido em 4 dimensões de 0 a 250 cada:

  1. CADASTRAL    (250 pts) — situação ativa, capital, tempo, CNAE
  2. JURÍDICO     (250 pts) — processos, RJ, falência, protestos, trabalhista
  3. FISCAL       (250 pts) — dívida ativa, CNDT, FGTS
  4. AGRO/CLIMA   (250 pts) — produtividade, risco ZARC, embargos ambientais

Farol de resultado:
  🟢 Verde  (A): 700–1000 → Aprovar em condições normais
  🟡 Amarelo(B): 400–699  → Aprovar com cautela e condições ajustadas
  🟠 Laranja(C): 200–399  → Restringir — exigir garantias
  🔴 Vermelho(D): 0–199   → Recusar — risco crítico de RJ
"""
from datetime import datetime
from typing import Optional

from ..models.domain import (
    CadastralData, JuridicalData, FiscalData,
    EnvironmentalData, AgroClimateData,
    ScoreBreakdown, RedFlag, CreditRecommendation, MonitoringFrequency,
)


# ---------------------------------------------------------------------------
# Dimensão 1 — Cadastral (0–250)
# ---------------------------------------------------------------------------

def score_cadastral(data: CadastralData) -> tuple[int, list[RedFlag]]:
    """
    Avalia a saúde cadastral da empresa.
    
    Critérios:
    - Situação ativa:         +100 pts (ou 0 se inativa/suspensa)
    - Tempo de atividade:     até +60 pts (escala linear por anos)
    - Capital social:         até +60 pts (escala por faixa de capital)
    - CNAE produtivo (agro):  +30 pts
    """
    score = 0
    flags: list[RedFlag] = []

    if data.raw_error:
        return 50, [RedFlag("CAD001", f"Erro na consulta cadastral: {data.raw_error}", "MEDIA")]

    # Situação cadastral
    situacao = (data.situacao_cadastral or "").upper()
    if situacao == "ATIVA":
        score += 100
    elif situacao in ("SUSPENSA", "INAPTA"):
        score += 20
        flags.append(RedFlag("CAD002", f"Situação cadastral irregular: {situacao}", "ALTA"))
    elif situacao == "BAIXADA":
        score += 0
        flags.append(RedFlag("CAD003", "CNPJ baixado — empresa inativa", "CRITICA"))
    else:
        score += 60  # situação desconhecida — crédito parcial

    # Tempo de atividade
    anos = _calc_anos_atividade(data.data_abertura)
    if anos >= 10:
        score += 60
    elif anos >= 5:
        score += 45
    elif anos >= 2:
        score += 25
    elif anos >= 1:
        score += 10
    else:
        flags.append(RedFlag("CAD004", f"Empresa com menos de 1 ano de atividade ({anos:.1f} anos)", "MEDIA"))

    # Capital social
    capital = data.capital_social
    if capital >= 1_000_000:
        score += 60
    elif capital >= 500_000:
        score += 45
    elif capital >= 100_000:
        score += 30
    elif capital >= 10_000:
        score += 15
    else:
        score += 5
        if capital < 1_000:
            flags.append(RedFlag("CAD005", f"Capital social muito baixo: R$ {capital:,.2f}", "MEDIA"))

    # CNAE agropecuário (seções A — agricultura, pecuária, silvicultura)
    cnae = data.cnae_principal or ""
    if cnae.startswith(("01", "02", "03", "46.1", "46.2")):
        score += 30  # CNAE diretamente agropecuário ou comércio atacadista agro

    return min(score, 250), flags


# ---------------------------------------------------------------------------
# Dimensão 2 — Jurídico (0–250)
# ---------------------------------------------------------------------------

def score_juridical(data: JuridicalData) -> tuple[int, list[RedFlag]]:
    """
    Avalia exposição jurídica da empresa.
    Parte do máximo (250) e desconta por eventos negativos.
    """
    score = 250
    flags: list[RedFlag] = []

    if data.raw_error:
        return 150, [RedFlag("JUR001", f"Erro na consulta jurídica: {data.raw_error}", "MEDIA")]

    # Pedido de RJ ou falência — desconto máximo, flag crítica
    if data.pedidos_rj > 0:
        score -= 200
        flags.append(RedFlag(
            "JUR002",
            f"Pedido(s) de Recuperação Judicial identificado(s): {data.pedidos_rj}",
            "CRITICA"
        ))

    if data.distribuicao_falencia > 0:
        score -= 200
        flags.append(RedFlag(
            "JUR003",
            f"Pedido(s) de falência distribuído(s): {data.distribuicao_falencia}",
            "CRITICA"
        ))

    # Execuções (cada execução desconta proporcionalmente)
    if data.processos_execucao >= 5:
        score -= 80
        flags.append(RedFlag("JUR004", f"Alto volume de execuções: {data.processos_execucao}", "ALTA"))
    elif data.processos_execucao >= 2:
        score -= 40
        flags.append(RedFlag("JUR005", f"Execuções em andamento: {data.processos_execucao}", "ALTA"))
    elif data.processos_execucao == 1:
        score -= 15

    # Protestos
    if data.protestos >= 3:
        score -= 50
        flags.append(RedFlag("JUR006", f"Múltiplos protestos: {data.protestos}", "ALTA"))
    elif data.protestos >= 1:
        score -= 20
        flags.append(RedFlag("JUR007", f"Protestos identificados: {data.protestos}", "MEDIA"))

    # Passivo trabalhista
    if data.passivo_trabalhista:
        score -= 30
        flags.append(RedFlag("JUR008", "CNDT irregular — passivo trabalhista com trânsito em julgado", "ALTA"))

    return max(score, 0), flags


# ---------------------------------------------------------------------------
# Dimensão 3 — Fiscal (0–250)
# ---------------------------------------------------------------------------

def score_fiscal(data: FiscalData) -> tuple[int, list[RedFlag]]:
    """
    Avalia situação fiscal federal.
    Parte do máximo (250) e desconta por irregularidades.
    """
    score = 250
    flags: list[RedFlag] = []

    if data.raw_error:
        return 150, [RedFlag("FIS001", f"Erro na consulta fiscal: {data.raw_error}", "MEDIA")]

    if data.divida_ativa_federal:
        score -= 100
        flags.append(RedFlag(
            "FIS002",
            "Débito inscrito em dívida ativa federal (PGFN)",
            "CRITICA"
        ))

    if data.cndt_irregular:
        score -= 60
        flags.append(RedFlag("FIS003", "CNDT irregular — débitos trabalhistas", "ALTA"))

    if data.fgts_irregular:
        score -= 40
        flags.append(RedFlag("FIS004", "CRF-FGTS irregular — FGTS em atraso", "MEDIA"))

    # Certidão positiva PGFN = mesma penalidade que dívida ativa (são a mesma coisa neste caso)
    # Já penalizada acima — sem double-counting

    return max(score, 0), flags


# ---------------------------------------------------------------------------
# Dimensão 4 — Agro/Climático + Ambiental (0–250)
# ---------------------------------------------------------------------------

def score_agro_climate(
    env: EnvironmentalData,
    agro: AgroClimateData
) -> tuple[int, list[RedFlag]]:
    """
    Avalia risco agronômico, climático e ambiental da propriedade.
    
    Critérios:
    - Embargo IBAMA:           -100 pts (flag crítica)
    - Risco ZARC por UF:       até +80 pts
    - Produtividade média:     até +80 pts
    - Histórico climático:     até +90 pts (penaliza secas/inundações)
    """
    score = 0
    flags: list[RedFlag] = []

    # Embargo ambiental — risco de perda da propriedade como garantia
    if env.embargo_ibama:
        score += 0
        flags.append(RedFlag(
            "AMB001",
            "Área embargada pelo IBAMA — propriedade rural com restrição legal",
            "CRITICA"
        ))
    else:
        score += 100

    # Risco climático ZARC
    risco = (agro.risco_climatico_zarc or "MEDIO").upper()
    risco_pts = {"BAIXO": 80, "MEDIO": 50, "ALTO": 20}.get(risco, 50)
    score += risco_pts
    if risco == "ALTO":
        flags.append(RedFlag("AMB002", f"Região com alto risco climático ZARC: {agro.uf}", "ALTA"))

    # Produtividade — soja como proxy principal
    prod = agro.produtividade_media_soja
    if prod >= 58:
        score += 40
    elif prod >= 52:
        score += 28
    elif prod >= 45:
        score += 15
    else:
        score += 5
        flags.append(RedFlag("AMB003", f"Produtividade regional abaixo da média: {prod:.1f} sc/ha", "MEDIA"))

    # Histórico climático (secas + inundações como fator de risco)
    eventos = agro.historico_secas + agro.historico_inundacoes
    if eventos <= 2:
        score += 30
    elif eventos <= 5:
        score += 15
    else:
        score += 0
        flags.append(RedFlag("AMB004", f"Histórico climático adverso: {eventos} eventos nos últimos 5 anos", "ALTA"))

    return min(score, 250), flags


# ---------------------------------------------------------------------------
# Orquestrador do score total
# ---------------------------------------------------------------------------

def calculate_score(
    cadastral: CadastralData,
    juridical: JuridicalData,
    fiscal: FiscalData,
    environmental: EnvironmentalData,
    agro_climate: AgroClimateData,
) -> tuple[ScoreBreakdown, list[RedFlag]]:
    """
    Calcula o score consolidado e retorna breakdown + lista de red flags.
    """
    s_cad, f_cad = score_cadastral(cadastral)
    s_jur, f_jur = score_juridical(juridical)
    s_fis, f_fis = score_fiscal(fiscal)
    s_agro, f_agro = score_agro_climate(environmental, agro_climate)

    breakdown = ScoreBreakdown(
        cadastral=s_cad,
        juridico=s_jur,
        fiscal=s_fis,
        agro_climate=s_agro,
    )

    all_flags = f_cad + f_jur + f_fis + f_agro

    # Ordena flags por severidade: CRITICA > ALTA > MEDIA
    severity_order = {"CRITICA": 0, "ALTA": 1, "MEDIA": 2}
    all_flags.sort(key=lambda f: severity_order.get(f.severidade, 9))

    return breakdown, all_flags


# ---------------------------------------------------------------------------
# Gerador de recomendação de crédito (regras — LLM enriquece depois)
# ---------------------------------------------------------------------------

def generate_recommendation(
    score: ScoreBreakdown,
    flags: list[RedFlag],
    capital_social: float = 0,
    limite_solicitado: Optional[float] = None,
) -> CreditRecommendation:
    """
    Gera recomendação de crédito baseada no score e nos red flags.
    O analista humano sempre tem a decisão final.
    
    Lógica de limite sugerido: baseado no capital social e no rating.
    Em produção calibrar com histórico de vendas da Krill Tech.
    """
    nivel = score.risk_level
    total = score.total

    # Fatores multiplicadores de limite por rating
    multiplicadores = {
        "A": 0.30,   # Verde: até 30% do capital social
        "B": 0.15,   # Amarelo: até 15%
        "C": 0.05,   # Laranja: até 5% (exige garantia real)
        "D": 0.00,   # Vermelho: não aprovar
    }
    
    mult = multiplicadores.get(nivel.value, 0.0)
    limite_base = capital_social * mult if capital_social > 0 else 50_000 * mult

    # Caps de limite por rating (proteção para carteira Krill Tech)
    caps = {"A": 500_000, "B": 150_000, "C": 30_000, "D": 0}
    limite_sugerido = min(limite_base, caps[nivel.value])

    # Se o solicitado é menor que o sugerido, usa o solicitado
    if limite_solicitado and limite_solicitado < limite_sugerido:
        limite_sugerido = limite_solicitado

    # Condições de pagamento por rating
    condicoes_map = {
        "A": "Pagamento padrão em até 120 dias. Boleto simples sem encargos adicionais.",
        "B": (
            "Parcelamento em até 60 dias. Cobrança com juros automáticos de mora a partir "
            "do vencimento (1% a.m. + IPCA). Recomendado solicitar aval do sócio principal."
        ),
        "C": (
            "Entrada mínima de 30%. Prazo máximo de 30 dias para o saldo restante. "
            "Obrigatório alienação fiduciária sobre máquinas/safra como garantia. "
            "Carência máxima de 15 dias. Juros de mora automáticos desde o vencimento."
        ),
        "D": (
            "VENDA NÃO RECOMENDADA. Risco crítico de inadimplência ou RJ iminente. "
            "Caso a diretoria decida aprovar, exigir pagamento antecipado integral."
        ),
    }

    # Prazo máximo por rating
    prazos = {"A": 120, "B": 60, "C": 30, "D": 0}

    # Tipo de cobrança
    cobranca_map = {
        "A": "normal",
        "B": "juros_automaticos",
        "C": "boleto_antecipado",
        "D": "pagamento_antecipado",
    }

    tem_flags_criticas = any(f.severidade == "CRITICA" for f in flags)

    return CreditRecommendation(
        aprovado=(nivel.value not in ("D",) and not (nivel.value == "C" and tem_flags_criticas)),
        limite_credito_sugerido=round(limite_sugerido, 2),
        condicoes_pagamento=condicoes_map[nivel.value],
        prazo_maximo_dias=prazos[nivel.value],
        exige_garantia=(nivel.value in ("C", "D")),
        tipo_cobranca=cobranca_map[nivel.value],
        observacoes=(
            f"Score total: {total}/1000 | Rating: {nivel.value} | "
            f"Red flags críticas: {sum(1 for f in flags if f.severidade == 'CRITICA')}"
        ),
    )


def get_monitoring_frequency(score: ScoreBreakdown) -> MonitoringFrequency:
    """
    Define a frequência de monitoramento com base no rating.
    
    Verde (A)   → Quinzenal (biweekly)
    Amarelo (B) → Semanal   (weekly)
    Laranja (C) → Diário    (daily) — alerta imediato
    Vermelho (D)→ Diário    (daily) — alerta imediato
    """
    nivel = score.risk_level
    if nivel == "A":
        return MonitoringFrequency.BIWEEKLY
    if nivel == "B":
        return MonitoringFrequency.WEEKLY
    return MonitoringFrequency.DAILY


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _calc_anos_atividade(data_abertura: Optional[str]) -> float:
    """Calcula anos de atividade a partir da string de data (DD/MM/YYYY)."""
    if not data_abertura:
        return 0.0
    try:
        abertura = datetime.strptime(data_abertura, "%d/%m/%Y")
        return (datetime.now() - abertura).days / 365.25
    except ValueError:
        return 0.0
