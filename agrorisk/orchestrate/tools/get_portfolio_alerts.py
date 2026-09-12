from ibm_watsonx_orchestrate.agent_builder.tools import tool
from datetime import datetime

_PORTFOLIO_DEMO = [
    {"cnpj": "01838723000127", "razao_social": "Cooperativa Agrária Ltda",
     "rating": "A", "score": 820, "ultimo_check": "2025-07-14",
     "red_flags_criticas": 0, "uf": "PR", "limite_aprovado_brl": 350000.0},
    {"cnpj": "12345678000190", "razao_social": "Fazenda São João Agropecuária",
     "rating": "B", "score": 610, "ultimo_check": "2025-07-13",
     "red_flags_criticas": 0, "uf": "MT", "limite_aprovado_brl": 80000.0},
    {"cnpj": "98765432000110", "razao_social": "Agro Cerrado Comércio e Representações",
     "rating": "B", "score": 430, "ultimo_check": "2025-07-10",
     "red_flags_criticas": 1, "uf": "GO", "limite_aprovado_brl": 45000.0},
    {"cnpj": "11222333000144", "razao_social": "Produtores Unidos do MT",
     "rating": "C", "score": 310, "ultimo_check": "2025-07-14",
     "red_flags_criticas": 2, "uf": "MT", "limite_aprovado_brl": 15000.0},
    {"cnpj": "55666777000188", "razao_social": "Rural Insumos Goiás S.A.",
     "rating": "C", "score": 240, "ultimo_check": "2025-07-14",
     "red_flags_criticas": 1, "uf": "GO", "limite_aprovado_brl": 10000.0},
    {"cnpj": "33444555000166", "razao_social": "Agroindústria Sertão Verde",
     "rating": "D", "score": 95,  "ultimo_check": "2025-07-14",
     "red_flags_criticas": 3, "uf": "BA", "limite_aprovado_brl": 0.0},
]


@tool
def get_portfolio_alerts(filter_rating: str = "ALL") -> dict:
    """
    Retorna o estado atual da carteira monitorada de clientes da Krill Tech,
    incluindo alertas ativos, distribuição de risco por farol e clientes que
    requerem atenção imediata. Implementa o Early Warning System — sistema de
    alerta precoce para prevenção à inadimplência no agronegócio.

    Args:
        filter_rating: Filtrar por rating específico — "A", "B", "C", "D" ou "ALL" para todos

    Returns:
        Dicionário com resumo da carteira, alertas ativos e lista de clientes por rating
    """
    portfolio = _PORTFOLIO_DEMO
    if filter_rating.upper() != "ALL":
        portfolio = [c for c in portfolio if c["rating"] == filter_rating.upper()]

    dist = {"A": 0, "B": 0, "C": 0, "D": 0}
    for c in _PORTFOLIO_DEMO:
        dist[c["rating"]] = dist.get(c["rating"], 0) + 1

    alertas_imediatos = [c for c in _PORTFOLIO_DEMO if c["rating"] in ("C", "D")]
    em_atencao        = [c for c in _PORTFOLIO_DEMO if c["rating"] == "B" and c["red_flags_criticas"] > 0]

    mensagens_alerta = []
    for c in alertas_imediatos:
        emoji = "🔴" if c["rating"] == "D" else "🟠"
        mensagens_alerta.append(
            f"{emoji} {c['razao_social']} — Rating {c['rating']} | Score {c['score']}/1000 | "
            f"{c['red_flags_criticas']} flag(s) crítica(s) | "
            f"Limite exposto: R$ {c['limite_aprovado_brl']:,.2f}"
        )

    score_medio     = sum(c["score"] for c in _PORTFOLIO_DEMO) // len(_PORTFOLIO_DEMO)
    exposicao_risco = sum(c["limite_aprovado_brl"] for c in _PORTFOLIO_DEMO if c["rating"] in ("C", "D"))

    return {
        "data_consulta": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "resumo_carteira": {
            "total_clientes": len(_PORTFOLIO_DEMO),
            "score_medio": score_medio,
            "distribuicao_ratings": {
                "A_verde": dist["A"], "B_amarelo": dist["B"],
                "C_laranja": dist["C"], "D_vermelho": dist["D"],
            },
            "alertas_imediatos": len(alertas_imediatos),
            "clientes_em_atencao": len(em_atencao),
            "exposicao_risco_brl": round(exposicao_risco, 2),
        },
        "alertas_ativos": mensagens_alerta,
        "clientes_filtrados": portfolio,
        "monitoramento_ativo": {
            "quinzenal_verde_A": dist["A"],
            "semanal_amarelo_B": dist["B"],
            "diario_laranja_C_vermelho_D": dist["C"] + dist["D"],
        },
        "recomendacao_equipe": (
            f"Priorize revisão imediata dos clientes C e D. "
            f"Exposição total a risco crítico: R$ {exposicao_risco:,.2f}. "
            "Considere renegociação contratual antes do vencimento das próximas parcelas."
        ) if alertas_imediatos else "Carteira dentro dos parâmetros normais de risco.",
    }
