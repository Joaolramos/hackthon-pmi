from ibm_watsonx_orchestrate.agent_builder.tools import tool


@tool
def generate_credit_recommendation(score_data: dict, capital_social: float = 0.0, limite_solicitado: float = 0.0) -> dict:
    """
    Gera a recomendação de decisão operacional de crédito para um cliente do agronegócio
    com base no score e rating calculados. Define se o crédito deve ser aprovado,
    qual o limite sugerido, as condições de pagamento, prazo máximo, tipo de cobrança
    e se é necessário exigir garantias reais. A decisão final sempre cabe ao analista humano.

    Args:
        score_data: Dicionário retornado por calculate_risk_score com score e rating
        capital_social: Capital social da empresa em R$ (usado para dimensionar o limite)
        limite_solicitado: Valor solicitado pelo cliente em R$ (0 = sem solicitação específica)

    Returns:
        Dicionário com decisão de aprovação, limite sugerido, condições de pagamento e observações
    """
    rating = score_data.get("rating", "D")
    score_total = int(score_data.get("score_total") or 0)
    flags_criticas = int(score_data.get("flags_criticas") or 0)

    mult = {"A": 0.30, "B": 0.15, "C": 0.05, "D": 0.00}.get(rating, 0.0)
    caps = {"A": 500_000.0, "B": 150_000.0, "C": 30_000.0, "D": 0.0}

    limite_base    = (float(capital_social) * mult) if capital_social > 0 else (50_000.0 * mult)
    limite_sugerido = min(limite_base, caps.get(rating, 0.0))

    if limite_solicitado > 0 and limite_solicitado < limite_sugerido:
        limite_sugerido = float(limite_solicitado)

    condicoes = {
        "A": (
            "Pagamento padrão em até 120 dias. "
            "Boleto simples sem encargos adicionais. "
            "Monitoramento quinzenal da carteira."
        ),
        "B": (
            "Parcelamento em até 60 dias. "
            "Cobrança com juros automáticos de mora a partir do vencimento (1% a.m. + IPCA). "
            "Recomendado solicitar aval do sócio principal. "
            "Monitoramento semanal da carteira."
        ),
        "C": (
            "Entrada mínima de 30% no ato da compra. "
            "Prazo máximo de 30 dias para o saldo restante. "
            "Obrigatório alienação fiduciária sobre máquinas ou safra como garantia. "
            "Carência máxima de 15 dias. "
            "Juros de mora automáticos desde o vencimento. "
            "Monitoramento diário com alerta imediato."
        ),
        "D": (
            "VENDA NÃO RECOMENDADA. "
            "Risco crítico de inadimplência ou RJ iminente. "
            "Caso a diretoria decida aprovar, exigir pagamento antecipado integral (100% antes da entrega). "
            "Monitoramento diário com alerta imediato."
        ),
    }

    prazos    = {"A": 120, "B": 60, "C": 30, "D": 0}
    cobrancas = {"A": "boleto_normal", "B": "juros_automaticos",
                 "C": "boleto_com_garantia", "D": "pagamento_antecipado"}

    aprovado = rating == "A" or rating == "B" or (rating == "C" and flags_criticas == 0)

    obs = (
        f"Score: {score_total}/1000 | Rating: {rating} — {score_data.get('rating_label', '')} | "
        f"Red flags críticas: {flags_criticas}. "
        + ("⚠️ Sistema não recomenda aprovação neste cenário. " if not aprovado else "")
        + "A decisão final é sempre do analista de crédito responsável."
    )

    return {
        "cnpj": score_data.get("cnpj", ""),
        "razao_social": score_data.get("razao_social", ""),
        "aprovado_pelo_sistema": aprovado,
        "rating": rating,
        "limite_credito_sugerido_brl": round(limite_sugerido, 2),
        "condicoes_pagamento": condicoes.get(rating, ""),
        "prazo_maximo_dias": prazos.get(rating, 0),
        "exige_garantia_real": rating in ("C", "D"),
        "tipo_cobranca": cobrancas.get(rating, "boleto_normal"),
        "monitoramento": score_data.get("monitoring_frequency", "Quinzenal"),
        "observacoes": obs,
        "aviso_legal": (
            "Este relatório é uma ferramenta de apoio à decisão. "
            "A aprovação ou rejeição de crédito é responsabilidade exclusiva do analista humano."
        ),
    }
